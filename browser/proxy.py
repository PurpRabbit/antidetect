import os
import re
import hashlib
import zipfile

import requests
from sqlalchemy import update, delete, select

from browser.models import ProxyModel
from browser.manager import ObjectsManager
from utils.paths import PROXIES_DIR, SETUP_DIR


class Proxy:
    model = ProxyModel

    def __init__(self, server: str) -> None:
        """Initialize a Proxy instance.

        Args:
            server (str): The proxy server address in the format 'username:password@ip_address:port'.
        """
        self.server = server
        self.pluginfile = "{}{}".format(PROXIES_DIR, self._get_proxy_name())

        if not os.path.exists(self.pluginfile):
            self._build_proxy()

    @classmethod
    def all_models(cls) -> list[ProxyModel]:
        """Return list of all proxies"""
        return ObjectsManager.all(cls.model)

    @classmethod
    def exists(cls, proxy_server: str) -> bool:
        stmt = select(cls.model).where(cls.model.server == proxy_server)
        if ObjectsManager.get(stmt):
            return True
        return False

    @staticmethod
    def check_connection(server: str) -> bool:
        """Check the connection to a proxy server.

        Args:
            server (str): The proxy server address in the format 'username:password@ip_address:port'.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        proxy = {
            "http": "http://{}".format(server),
            "https": "http://{}".format(server),
        }
        try:
            response = requests.get("https://www.google.com/", proxies=proxy)
            if response.ok:
                return True
            else:
                return False
        except requests.exceptions.RequestException as ex:
            return False

    @staticmethod
    def valid_format(server: str) -> bool:
        """Check if the proxy server address has a valid format.

        Args:
            server (str): The proxy server address in the format 'username:password@ip_address:port'.

        Returns:
            bool: True if the format is valid, False otherwise.
        """
        pattern = r"^(\w+):(\w+)@(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)$"
        if not server:
            return False
        match = re.match(pattern, server)

        if match:
            return True
        return False

    def _get_proxy_name(self) -> str:
        """Generate a unique name for the proxy file.

        Returns:
            str: The unique name for the proxy file.
        """
        return hashlib.sha256(self.server.encode()).hexdigest() + ".zip"

    def _get_manifest(self) -> str:
        with open(os.path.join(SETUP_DIR + "proxymanifest.json")) as fp:
            manifest = fp.read()
            return manifest

    def _get_background_js(
        self, username: str, password: str, address: str, port: int
    ) -> str:
        with open(os.path.join(SETUP_DIR + "proxybackground.js")) as fp:
            background = fp.read()
            return background % (address, port, username, password)

    def _build_proxy(self) -> None:
        """Build the proxy plugin file."""
        username, password, address, port = self.server.split("@")[0].split(
            ":"
        ) + self.server.split("@")[1].split(":")
        with zipfile.ZipFile(self.pluginfile, "w") as zp:
            zp.writestr("manifest.json", self._get_manifest)
            zp.writestr(
                "background.js",
                self._get_background_js(username, password, address, port),
            )

    @staticmethod
    def get_ip(server: str) -> str:
        """Get the IP address from the proxy server address.

        Args:
            server (str): The proxy server address in the format 'username:password@ip_address:port'.

        Returns:
            str: The IP address of the proxy server.
        """
        return server.split("@")[1].split(":")[0]

    @staticmethod
    def split_server(server: str) -> tuple[str]:
        user_data, ip_address = server.split("@")
        return tuple(user_data.split(":") + ip_address.split(":"))
