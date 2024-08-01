import re
import os

from sqlalchemy import select, update
from webdriver_manager.chrome import ChromeDriverManager
from browser.manager import ObjectsManager
from browser.models import WebDriver


class DriverManager:
    def __init__(self):
        self.web_driver = ObjectsManager.get(select(WebDriver))
        self.chrome_driver_manager = ChromeDriverManager()

    def get_driver(self) -> str:
        """Return driver path"""
        # Download driver if no driver was found in database
        if not self.web_driver:
            path, version = self._get_latest_driver()
            self._create_driver_data(path, version)
            return path

        # Compare driver version in database with latest
        # return if latest driver version == database version
        os_version = self.web_driver[0].version
        latest_version = (
            self.chrome_driver_manager.driver.get_driver_version_to_download()
        )

        if os_version == latest_version and os.path.exists(self.web_driver[0].path):
            return self.web_driver[0].path

        # Download load latest driver version and update database
        path, version = self._get_latest_driver()
        self._update_driver_data(path, version, os_version)
        return path

    def _get_latest_driver(self) -> tuple[str, str]:
        """Download latest webdriver; return path, version"""
        path = self.chrome_driver_manager.install()
        version = self._get_driver_version(path)

        return path, version

    def _get_driver_version(self, path: str) -> str:
        """Get driver version from driver path"""
        version_pattern = r"\d+\.\d+\.\d+\.\d+"
        match = re.search(version_pattern, path)
        return match.group(0)

    def _create_driver_data(self, path: str, version: str) -> None:
        """Create new driver in database"""
        ObjectsManager.create(WebDriver(path=path, version=version))

    def _update_driver_data(self, path: str, version: str, os_version: str) -> None:
        """Update driver data in database by version"""
        stmt = (
            update(WebDriver)
            .where(WebDriver.version == os_version)
            .values(path=path, version=version)
        )
        ObjectsManager.update(stmt)
