import os

BASE_DIR = os.getcwd()
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
WEB_DRIVER_DIR = os.path.join(BASE_DIR, "webdriver", "chromedriver.exe")
USER_AGENTS = os.path.join(BASE_DIR, "browser", "user_agents.txt")
PROXIES_DIR = os.path.join(BASE_DIR, "browser", "proxies")
