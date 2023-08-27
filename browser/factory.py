import os
import shutil
import random
from threading import Thread

from browser.exceptions import (
    ProfileExists,
    ProfileDoesNotExist,
    ProfileIsRunning,
    ProxyDoesNotExist,
    ProfileIsNotRunning,
    ProxyExist,
    InvalidProxyFormat,
)
from utils.paths import PROFILES_DIR, BASE_DIR
from utils.ipgeo import get_country_from_ip
from browser.user_agent import user_agents
from browser.profile import Profile
from browser.proxy import Proxy
from database.connector import SqlDatabase


class ProfileFactory:
    def __init__(self) -> None:
        """Initialize the ProfileFactory class."""
        self.database = SqlDatabase(db_name="database.db")
        self.running_profiles: dict[str, Profile] = dict()

    def validate_proxies(self):
        """Validate the proxies stored in the database.

        This method checks the connection status of each proxy and updates their validity
        in the database accordingly.
        """
        proxies = self.database.get_proxies()
        for proxy in proxies:
            if proxy.is_valid:
                continue

            validated = Proxy.check_connection(proxy.server)
            if validated:
                self.database.change_proxy_valid(proxy.server, True)
            else:
                self.database.change_proxy_valid(proxy.server, False)

    def create_proxy(self, server: str) -> None:
        """Create a new proxy with the provided server address.

        Args:
            server (str): The server address of the proxy.

        Raises:
            InvalidProxyFormat: If the proxy format is invalid.
            ProxyExist: If the proxy already exists in the database.
        """
        if not Proxy.valid_format(server):
            raise InvalidProxyFormat(
                "expected proxy format - username:password@ip_address:port"
            )
        if self.database.proxy_exists(server):
            raise ProxyExist("this proxy already exist")
        self.database.create_proxy(server, get_country_from_ip(Proxy.get_ip(server)))

    def create_proxies_from_file(self, file_name: str) -> None:
        """Create proxies from a text file.

        This method reads proxies from a text file, validates them, and creates them in the database.

        Args:
            file_name (str): The name of the text file containing proxies.

        Raises:
            FileNotFoundError: If the file format is invalid or the file does not exist.
        """
        if not file_name.endswith(".txt"):
            raise FileNotFoundError("invalid file format, .txt expected")
        if not os.path.exists(BASE_DIR + f"\\{file_name}"):
            raise FileNotFoundError("file not found")

        with open(BASE_DIR + f"\\{file_name}") as fp:
            proxies = fp.readlines()

        for proxy in proxies:
            proxy = proxy.strip()
            if not Proxy.valid_format(proxy):
                continue
            if self.database.proxy_exists(proxy):
                continue
            self.database.create_proxy(proxy, get_country_from_ip(Proxy.get_ip(proxy)))

    def delete_proxy(self, proxy_id: int) -> str:
        """Delete a proxy from the database.

        Args:
            proxy_id (int): The ID of the proxy to delete.

        Returns:
            str: The success message after deleting the proxy.

        Raises:
            ProxyDoesNotExist: If the proxy ID is invalid.
        """
        if not self.database.proxy_exists_by_id(proxy_id):
            raise ProxyDoesNotExist("invalid proxy id")

        profiles = self.database.get_profiles()
        for profile in profiles:
            if profile.proxy_id == proxy_id:
                self.change_proxy(profile.name, 0)

        self.database.delete_proxy(proxy_id)

    def _get_user_agent(self) -> str:
        """Get a random user agent.

        Returns:
            str: A randomly selected user agent.
        """
        return random.choice(user_agents)

    @staticmethod
    def profile_exist_required(func):
        """Decorator to ensure a profile exists before executing a method.

        Args:
            func (function): The function to decorate.

        Returns:
            function: The decorated function.
        """

        def wrapper(self, name, *args):
            if not self.database.profile_exists(name):
                raise ProfileDoesNotExist("profile does not exist")
            return func(self, name, *args)

        return wrapper

    @profile_exist_required
    def stop_profile(self, name: str) -> None:
        """Stop the execution of a running profile.

        Args:
            name (str): The name of the profile to stop.

        Raises:
            ProfileIsNotRunning: If the profile is not currently active.
        """
        profile = self.running_profiles.pop(name, None)
        if not profile:
            raise ProfileIsNotRunning("profile is not active")
        thread = Thread(target=profile.stop, daemon=True)
        thread.start()

    @profile_exist_required
    def run_profile(self, name: str) -> Profile:
        """Run a browser profile.

        Args:
            name (str): The name of the profile to run.

        Returns:
            Profile: The running profile instance.

        Raises:
            ProfileIsRunning: If the profile is already active.
        """
        if self.profile_is_running(name):
            raise ProfileIsRunning("profile is active")

        profile_model = self.database.get_profile(name)
        proxy_model = (
            self.database.get_proxy(profile_model.proxy_id)
            if profile_model.proxy_id
            else None
        )
        profile = Profile(
            profile_model.name,
            profile_model.user_agent,
            proxy=Proxy(proxy_model.server) if proxy_model else None,
        )

        thread = Thread(target=profile.run, daemon=True)
        thread.start()
        self.running_profiles[name] = profile
        return profile

    def profile_is_running(self, name: str) -> bool:
        """Check if a profile is currently running.

        Args:
            name (str): The name of the profile to check.

        Returns:
            bool: True if the profile is running, False otherwise.
        """
        if (
            name in self.running_profiles
            and not self.running_profiles[name].thread_running
        ):
            self.running_profiles.pop(name)
        return name in self.running_profiles

    def create_profile(
        self,
        name: str,
        proxy_id: int = None,
        note: str = None,
        status: str = None,
        user_agent: str = None,
    ) -> Profile:
        """Create a new browser profile.

        Args:
            name (str): The name of the profile to create.
            proxy_id (int, optional): The ID of the associated proxy. Defaults to None.
            description (str, optional): The description of the profile. Defaults to None.

        Raises:
            ProfileExists: If a profile with the same name already exists.
        """
        if self.database.profile_exists(name):
            raise ProfileExists("Profile with this name already exists")

        user_agent = user_agent or self._get_user_agent()

        proxy_id = proxy_id if self.database.proxy_exists_by_id(proxy_id) else None
        self.database.create_profile(name, user_agent, proxy_id, note, status)
        os.mkdir(PROFILES_DIR + f"\\{name}")

    def prune(self) -> None:
        """Delete all existing profiles and their directories.

        This method deletes all profiles and their corresponding directories from the system.
        """
        for profile in self.database.get_profiles():
            shutil.rmtree(PROFILES_DIR + f"\\{profile.name}")
        self.database.profile_prune()

    @profile_exist_required
    def change_proxy(self, name: str, proxy_id: int) -> None:
        """Change the proxy associated with a profile.

        Args:
            name (str): The name of the profile.
            proxy_id (int): The ID of the new proxy.

        Raises:
            ProxyDoesNotExist: If the proxy ID is invalid.
        """
        if proxy_id == 0:
            self.database.change_profile_proxy(name, proxy_id)
            return
        if not self.database.proxy_exists_by_id(proxy_id):
            raise ProxyDoesNotExist("Invalid proxy id")
        self.database.change_profile_proxy(name, proxy_id)

    @profile_exist_required
    def change_note(self, name: str, note: str) -> None:
        """Change the description of a profile.

        Args:
            name (str): The name of the profile.
            description (str): The new description for the profile.
        """
        self.database.change_profile_note(name, note)

    @profile_exist_required
    def delete_profile(self, name: str) -> None:
        """Delete a profile and its associated directory.

        Args:
            name (str): The name of the profile to delete.
        """
        self.database.delete_profile(name)
        shutil.rmtree(PROFILES_DIR + f"\\{name}")
