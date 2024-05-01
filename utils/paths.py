import os

BASE_DIR = os.getcwd()

DATA_DIR = os.path.join(BASE_DIR, "data")
SETUP_DIR = os.path.join(BASE_DIR, "setup")

PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
USER_AGENTS = os.path.join(SETUP_DIR, "user_agents.txt")
PROXIES_DIR = os.path.join(DATA_DIR, "proxies")
