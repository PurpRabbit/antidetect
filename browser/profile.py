import time
import threading
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from browser.proxy import Proxy
from utils.paths import PROFILES_DIR


BROWSER_CLOSE_MESSAGE = 'Unable to evaluate script: no such window: target window already closed\nfrom unknown error: web view not found\n'


class Profile:
    def __init__(self, name: str, user_agent: str, proxy: Proxy | None = None) -> None:
        """Initialize a Profile instance.

        Args:
            name (str): The name of the profile.
            user_agent (str): The user agent string for the profile.
            proxy (Proxy | None, optional): The Proxy instance associated with the profile. Defaults to None.
        """
        self.name = name
        self.user_agent = user_agent
        self._proxy = proxy
        self.thread_running = threading.Event()

        self.options = webdriver.ChromeOptions()

        self.options.add_argument("--port={}".format(random.randint(8001, 9000)))
        self.options.add_argument("--user-data-dir={}".format(PROFILES_DIR + f'\\{name}'))
        self.options.add_argument("user-agent={}".format(user_agent))
        self.options.add_argument("--start-maximized")
        self.options.add_experimental_option("excludeSwitches", ["disable-background-timer-throttling"])
        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

        self.service = Service()

        if proxy:
            self.options.add_extension(proxy.pluginfile)

    def run(self):
        """Start running the profile in a separate thread."""
        self.browser = webdriver.Chrome(service=self.service, options=self.options)

        self.thread_running.set()
        while self.thread_running.is_set():
            log = self.browser.get_log('driver')
            if not log:
                time.sleep(1)
                continue
            if log[-1]["message"] == BROWSER_CLOSE_MESSAGE:
                self.thread_running.clear()
        self.browser.quit()

    def stop(self):
        """Stop the running profile."""
        self.browser.close()
        self.browser.quit()
        self.thread_running.clear()
