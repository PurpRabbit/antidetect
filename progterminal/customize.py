from art import text2art
from colorama import init as colorama_init
from colorama import Fore, Style


colorama_init(autoreset=True)


_banner_info = """
This script allows you to manage browser profiles and associate proxies with them. 
It provides several commands to perform different actions:

    profile list - Lists all the available browser profiles.
    profile create - Creates a new browser profile with the specified name.
    profile run - Launches the browser using the specified profile.
    profile stop - Stops the browser associated with the specified profile.
    profile delete - Deletes the specified browser profile.
    profile change proxy - Associates the specified proxy (identified by its ID) with the given browser profile.
    profile change description - Changes the description of the specified browser profile.

    proxy list - Lists all the available proxies.
    proxy create - Create a new proxy.
    proxy validate - Validate the existing proxies.
    proxy delete - Delete the proxy with the specified ID.

    You can get more information using 'help profile/proxy'
    """


CUSTOM_PROMPT = Fore.BLUE + ">>> " + Style.RESET_ALL
_banner = text2art("AntiDetect\nBrowser")
CUSTOM_BANNER = Fore.BLUE + Style.BRIGHT + _banner + _banner_info


def success_message(text: str) -> None:
    print(Fore.GREEN + f"--> {text}" + Style.RESET_ALL)

def error_message(text: str) -> None:
    print(Fore.RED + f"--> {text}" + Style.RESET_ALL)

def invalid_arguments_message(argument: str) -> None:
    error_message(f"unexpected argument: {argument}")

def warning(text: str) -> bool:
    decision = input(Fore.RED + text)
    if decision.lower().strip() in ("y", "yes"):
        return True
    return False