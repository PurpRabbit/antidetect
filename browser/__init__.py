import os

from browser.factory import ProfileFactory
from utils.paths import PROXIES_DIR, PROFILES_DIR, DATA_DIR


if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

if not os.path.exists(PROXIES_DIR):
    os.mkdir(PROXIES_DIR)

if not os.path.exists(PROFILES_DIR):
    os.mkdir(PROFILES_DIR)


profile_factory = ProfileFactory()
