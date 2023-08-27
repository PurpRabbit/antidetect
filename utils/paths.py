import os

BASE_DIR = os.getcwd()

DATA_DIR = os.path.join(BASE_DIR, "data")

PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
WEB_DRIVER_DIR = os.path.join(BASE_DIR, "webdriver", "chromedriver.exe")
USER_AGENTS = os.path.join(DATA_DIR, "user_agents.txt")
PROXIES_DIR = os.path.join(DATA_DIR, "proxies")
