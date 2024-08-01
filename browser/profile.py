"""
This module is created to manage profile objects.

Docstrings:
    Usage of profile, Profile and ProfileModel in docstrings has different meanings.
    profile - used when docstring is related to both Profile and ProfileModel objects.
    Profile - used when docstring is related to Profile object.
    ProfileModel - used when docstring is related to ProfileModel object.
"""

import os
import shutil
import random
from typing import overload

from sqlalchemy import update, delete, select
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common import exceptions

from browser.manager import ObjectsManager
from browser.models import ProfileModel
from browser.proxy import Proxy
from browser.exceptions import ProfileDoesNotExist, ProfileExists
from browser.driver import DriverManager
from utils import paths


class Profile:
    model = ProfileModel
    _instances = dict()

    def __new__(cls, *args, **kwargs):
        """
        This method has been overwritten to check if the given object has already been created
        during program execution. This is necessary so that the same profile is not recreated repeatedly.
        In fact, it is something like a Singleton
        """
        # Get profile name
        try:
            profile_model_name = args[
                0
            ].name  # If Profile is creating by ProfileModel object
        except IndexError:
            profile_model_name = kwargs.get("name")  # If Profile is creating by fields

        if profile_model_name in cls._instances:
            return cls._instances.get(profile_model_name)
        obj = super().__new__(cls)
        cls._instances[profile_model_name] = obj
        return obj

    @overload
    def __init__(
        self,
        name: str,
        user_agent: str,
        status: str = None,
        proxy_server: str = None,
        note: str = None,
    ):
        """Initialize a Profile instance by fields

        Args:
            :name: Profile name (mantadory)
            :user_agent: Profile user agent (mantadory)
            :status: Profile status (optional)
            :proxy_server: Profile proxy (optional)
            :note: Profile note (optional)
        """

    @overload
    def __init__(self, profile_model: ProfileModel) -> None:
        """Initialize a Profile instance by ProfileModel object"""

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], ProfileModel):
            profile_model = args[0]
            self.name = profile_model.name
            self.user_agent = profile_model.user_agent
            self.status = profile_model.status
            self.proxy_server = profile_model.proxy_server
            self.note = profile_model.note
        else:
            self.name = kwargs.get("name")
            self.user_agent = kwargs.get("user_agent")
            self.status = kwargs.get("status")
            self.proxy_server = kwargs.get("proxy_server")
            self.note = kwargs.get("note")

        self._add_options()

    def _add_options(self):
        self.options = webdriver.ChromeOptions()

        self.options.add_argument(
            "--port={}".format(random.randint(8001, 9999))
        )  # Use random port for webdriver
        self.options.add_argument(
            "--user-data-dir={}".format(
                os.path.join(paths.PROFILES_DIR, self.name)
            )  # Use needed profile path
        )
        self.options.add_argument(
            "user-agent={}".format(self.user_agent)
        )  # Set user agent
        self.options.add_argument("--start-maximized")  # Start window in maximixed size
        self.options.add_experimental_option(
            "excludeSwitches", ["disable-background-timer-throttling"]
        )
        self.options.add_experimental_option("useAutomationExtension", False)
        # excludeSwitches - List of Chrome command line switches to EXCLUDE that ChromeDriver by default passes when starting Chrome. Do not prefix switches with --
        # enable-automation - Disable 'automation' message from settings
        # enable-logging - Disable console logging
        self.options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )

        self.service = Service(DriverManager().get_driver())

        if self.proxy_server:
            # Add proxy to profile
            proxy = Proxy(self.proxy_server)
            self.options.add_extension(proxy.pluginfile)

    def is_running(self) -> bool:
        """Check if profile is still running by searching element on page
        Return True if element was found otherwise - False"""
        try:
            self.browser.find_element(By.TAG_NAME, "body")
        except (
            exceptions.NoSuchWindowException,
            exceptions.NoSuchElementException,
        ):
            return False
        return True

    def run(self):
        """Start the profile"""
        self.browser = webdriver.Chrome(options=self.options, service=self.service)

    def stop(self):
        """Stop the running profile."""
        try:
            self.browser.close()
        except exceptions.WebDriverException:
            pass
        self.browser.quit()

    def _create_path(self) -> None:
        """Create new path for profile"""
        os.mkdir(os.path.join(paths.PROFILES_DIR, self.name))

    def _delete_path(self) -> None:
        """Delete path related to profile"""
        try:
            shutil.rmtree(os.path.join(paths.PROFILES_DIR, self.name))
        except FileNotFoundError:
            return

    def set_note(self, note: str) -> None:
        """Update profile note by profile name"""
        stmt = update(self.model).where(self.model.name == self.name).values(note=note)
        ObjectsManager.update(stmt)

    def set_proxy(self, proxy_server: str | None) -> None:
        """Update profile proxy server by profile name"""
        if proxy_server is None:
            # If u dont remove this path, after u change proxy to None value,
            # ur browser will be requiring pass ang login for prev proxy
            secure_path = os.path.join(
                paths.PROFILES_DIR, self.name, "Default", "Secure Preferences"
            )
            if os.path.exists(secure_path):
                os.remove(secure_path)

        stmt = (
            update(self.model)
            .where(self.model.name == self.name)
            .values(proxy_server=proxy_server)
        )
        self.proxy_server = proxy_server
        ObjectsManager.update(stmt)

    def set_status(self, status: str) -> None:
        """Update profile status"""
        stmt = (
            update(self.model).where(self.model.name == self.name).values(status=status)
        )
        ObjectsManager.update(stmt)

    def set_useragent(self, user_agent: str) -> None:
        """Update profile user agent"""
        stmt = (
            update(self.model)
            .where(self.model.name == self.name)
            .values(user_agent=user_agent)
        )
        ObjectsManager.update(stmt)

    def save(self) -> None:
        """Save new profile model object with 'Profile' object data and create new profile path

        Raises: ProfileExists, if profile with this name already exist in db.
        """
        if self.exists():
            raise ProfileExists("Profile with this name already exist")

        ObjectsManager.create(
            ProfileModel(
                name=self.name,
                user_agent=self.user_agent,
                status=self.status,
                proxy_server=self.proxy_server,
                note=self.note,
            )
        )
        self._create_path()

    def exists(self) -> bool:
        """Return True if profile model with this name alredy exist in db, otherwise False"""
        stmt = select(self.model).where(self.model.name == self.name)
        if ObjectsManager.get(stmt):
            return True
        return False

    def delete(self) -> None:
        """Delete profile model from db and delete profile path

        Raises: ProfileDoesNotExists, if profile with this name do not exist in db.
        """
        if not self.exists():
            raise ProfileDoesNotExist("Profile with this name dont exist")

        stmt = delete(self.model).where(self.model.name == self.name)
        ObjectsManager.delete(stmt)
        self._delete_path()

    @classmethod
    def all(cls) -> list["Profile"]:
        """Return list of all profiles initialized with db data"""
        return [Profile(model) for model in ObjectsManager.all(cls.model)]

    def __eq__(self, other):
        if isinstance(other, Profile):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)
