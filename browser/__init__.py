import os

from utils.paths import PROXIES_DIR, PROFILES_DIR


if not os.path.exists(PROXIES_DIR):
    os.mkdir(PROXIES_DIR)

if not os.path.exists(PROFILES_DIR):
    os.mkdir(PROFILES_DIR)