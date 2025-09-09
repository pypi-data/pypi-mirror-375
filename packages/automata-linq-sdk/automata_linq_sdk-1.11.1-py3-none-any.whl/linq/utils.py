import os
import re
from pathlib import Path
from typing import Generator

import requests
import urllib3.util


def get_latest_scheduler_version() -> str:
    """Gets the latest supported scheduler version.

    This can be used to automatically make a workflow use the latest support version (at time of saving the workflow).
    """
    from linq.client import Linq  # Avoid circular import

    client = Linq()
    return client.get_supported_scheduler_versions()["maestro"][0]


def validate_scheduler_driver_compatibility(scheduler_version: str, drivers_version: str) -> bool:
    """Validate that a scheduler version is compatible with a drivers version.

    :param scheduler_version: The scheduler version to check
    :param drivers_version: The drivers version to check against
    :return: True if compatible
    :raises IncompatibleDriverVersionError: if versions are incompatible
    """
    from packaging.version import Version

    from linq.client import Linq  # Avoid circular import
    from linq.exceptions import IncompatibleDriverVersionError  # Avoid circular import

    client = Linq()
    maestro_versions_response = client.get_maestro_versions()

    target_scheduler_versions = [
        v
        for v in maestro_versions_response.get("versions", [])
        if v.get("name") == scheduler_version and v.get("compatible", False)
    ]

    if not target_scheduler_versions:
        raise IncompatibleDriverVersionError(f"Scheduler version '{scheduler_version}' not found or not compatible")

    for version_info in target_scheduler_versions:  # pragma: no cover
        compatible_drivers_version = version_info.get("drivers_version")
        if compatible_drivers_version:
            try:
                if Version(drivers_version) >= Version(compatible_drivers_version):
                    return True
            except Exception:
                if drivers_version == compatible_drivers_version:
                    return True

    raise IncompatibleDriverVersionError(
        f"Scheduler version '{scheduler_version}' is not compatible with drivers version '{drivers_version}'"
    )


class Download:
    def __init__(
        self,
        url: str,
        output_dir: str | Path,
        *,
        chunk_size: int = 8192,
    ):
        self.url = url

        self.output_dir = output_dir if isinstance(output_dir, Path) else Path(output_dir)
        self._check_output_dir()

        self._chunk_size = chunk_size

        self._response = requests.get(self.url, stream=True)
        self._response.raise_for_status()

        self.filename = self._get_download_filename()
        self.full_path = self.output_dir / self.filename

        self._file = open(self.full_path, "wb")

        self.total_size = int(self._response.headers.get("Content-Length", 0))
        self.written = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._response.close()
        self._file.close()

    def transfer(self) -> None:
        for _ in self.transfer_with_progress():
            pass

    def transfer_with_progress(self) -> Generator[float, None, None]:
        for chunk in self._response.iter_content(chunk_size=self._chunk_size):
            self._file.write(chunk)
            self.written += len(chunk)
            yield self.progress

    @property
    def progress(self):
        return self.written / self.total_size

    def _check_output_dir(self):
        assert self.output_dir.is_dir(), f'output_dir "{self.output_dir}" must be a directory'
        assert os.access(
            self.output_dir, os.W_OK
        ), f'insufficient permissions to write to output_dir "{self.output_dir}"'

    def _get_download_filename(self) -> str:
        if "Content-Disposition" in self._response.headers:
            disposition = self._response.headers["Content-Disposition"]
            if match := re.search(r'filename="?([^\s"]+)"?', disposition):  # pragma: no branch
                return match.group(1)
        parsed_url = urllib3.util.parse_url(self.url)
        assert parsed_url.path is not None
        return Path(parsed_url.path).name
