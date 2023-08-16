import os
import re
import hashlib
import zipfile

import requests

from browser.proxy_setup import manifest_json, get_background_js
from utils.paths import PROXIES_DIR


class Proxy:
    def __init__(self, server: str) -> None:
        """Initialize a Proxy instance.

        Args:
            server (str): The proxy server address in the format 'username:password@ip_address:port'.
        """
        self.server = server
        self.pluginfile = "{}{}".format(PROXIES_DIR, self._get_proxy_name())

        if not os.path.exists(self.pluginfile):
            self._build_proxy()

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

    def _build_proxy(self) -> None:
        """Build the proxy plugin file."""
        username, password, address, port = self.server.split("@")[0].split(
            ":"
        ) + self.server.split("@")[1].split(":")
        with zipfile.ZipFile(self.pluginfile, "w") as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr(
                "background.js", get_background_js(username, password, address, port)
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
