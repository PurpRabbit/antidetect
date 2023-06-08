import cmd
import sys
import os
from prettytable import PrettyTable

from browser.factory import ProfileFactory
from browser.exceptions import *
from progterminal.customize import CUSTOM_PROMPT, CUSTOM_BANNER, success_message, error_message, warning
from utils.paths import PROFILES_DIR


class Terminal(cmd.Cmd):
    prompt = CUSTOM_PROMPT
    intro = CUSTOM_BANNER

    def preloop(self):
        """Initialization before the command loop starts."""
        self.runners = dict()
        self.profile_factory = ProfileFactory()

    def do_profile(self, args):
        """Handle the 'profile' command and its subcommands."""
        if args and ('-h' in args or '--help' in args):
            error_message("use 'help [command]'")
            return

        args = args.split(' ')
        match args:
            case ["list"]:
                self._show_profiles_list()
            case ["prune"]:
                if warning("Are you sure you want to delete all profiles?(y/n): "):
                    self._profiles_prune()
            case ["create", profile_name, *options]:
                self._create_profile(profile_name, options)
            case ["run", profile_name]:
                self._run_profile(profile_name)
            case ["stop", profile_name]:
                self._stop_profile(profile_name)
            case ["delete", profile_name]:
                self._delete_profile(profile_name)
            case ["change", "proxy", profile_name, proxy_id]:
                if not proxy_id.isnumeric():
                    error_message("provide proxy id from 'proxy list'")
                    return
                self._change_proxy(profile_name, int(proxy_id))
            case ["change", "desc" | "description", profile_name, *description]:
                self._change_description(profile_name, description)
            case _:
                error_message("unknown command")

    def do_proxy(self, args):
        """Handle the 'proxy' command and its subcommands."""
        if args and ('-h' in args or '--help' in args):
            error_message("use 'help [command]'")
            return

        args = args.split(' ')
        match args:
            case ["list"]:
                self._show_proxy_list()
            case ["create", server]:
                self._create_proxy(server)
            case ["create", "-f" | "--file", file_name]:
                self._create_proxies(file_name)
            case ["validate"]:
                self._validate_proxies()
            case ["delete", proxy_id]:
                if not proxy_id.isnumeric():
                    error_message("provide proxy id from 'proxy list'")
                    return
                self._delete_proxy(int(proxy_id))
            case ["prune"]:
                if warning("Are you sure you want to delete all profiles?(y/n): "):
                    self._proxy_prune()
            case _:
                error_message("unknown command")

    def _validate_proxies(self):
        """Validate the proxies in the profile factory."""
        self.profile_factory.validate_proxies()

    def _proxy_prune(self):
        """Prune the proxies in the profile factory."""
        self.profile_factory.database.proxy_prune()

    def _show_proxy_list(self):
        """Show the list of proxies in a formatted table."""
        table = PrettyTable(["ID", "Country", "Address", "Port", "Username", "Password", "Valid", "Profiles count"])
        for proxy in self.profile_factory.database.get_proxies():
            username, password, address, port = proxy.split_server()
            table.add_row(
                [
                    proxy.id,
                    proxy.country,
                    address,
                    port,
                    username,
                    password,
                    proxy.is_valid,
                    len([profile for profile in self.profile_factory.database.get_profiles() if profile.proxy_id == proxy.id]),
                ]
            )
        print(table)

    def _create_proxies(self, file_name: str):
        """Create proxies from a file."""
        try:
            self.profile_factory.create_proxies_from_file(file_name)
        except FileNotFoundError as ex:
            error_message(ex)

    def _create_proxy(self, server: str):
        """Create a proxy with the given server."""
        try:
            self.profile_factory.create_proxy(server)
            success_message(f"Proxy '{server}' created")
        except (InvalidProxyFormat, ProxyExist) as ex:
            error_message(ex)

    def _delete_proxy(self, proxy_id: int):
        """Delete the proxy with the given ID."""
        try:
            self.profile_factory.delete_proxy(proxy_id)
            success_message(f"Proxy '{proxy_id}' was deleted")
        except ProxyDoesNotExist as ex:
            error_message(ex)

    def _profiles_prune(self):
        """Delete all profiles."""
        self.profile_factory.prune()
        success_message("Profiles successfully deleted")

    def _change_description(self, name: str, description: tuple):
        """Change the description of a profile."""
        try:
            self.profile_factory.change_description(name, " ".join(description))
            success_message(f"Description for '{name}' was successfully changed ")
        except ProfileDoesNotExist as ex:
            error_message(ex)

    def _change_proxy(self, name: str, proxy_id: int):
        """Change the proxy of a profile."""
        try:
            self.profile_factory.change_proxy(name, proxy_id)
            success_message(f"Proxy for '{name}' was changed to '{proxy_id}'")
            # If u dont remove this path, after u change proxy to 0 value,
            # ur browser will be requiring for pass ang login for prev proxy
            if os.path.exists(PROFILES_DIR + f'\\{name}\\Default\\Secure Preferences'):
                os.remove(PROFILES_DIR + f'\\{name}\\Default\\Secure Preferences')
        except ProxyDoesNotExist as ex:
            error_message(ex)

    def _delete_profile(self, name: str):
        """Delete a profile."""
        try:
            self.profile_factory.delete_profile(name)
            success_message(f"Profile '{name}' was deleted")
        except ProfileDoesNotExist as ex:
            error_message(ex)

    def _run_profile(self, name: str):
        """Run a profile."""
        try:
            self.profile_factory.run_profile(name)
        except (ProfileDoesNotExist, ProfileIsRunning) as ex:
            error_message(ex)

    def _stop_profile(self, name: str):
        """Stop a running profile."""
        try:
            self.profile_factory.stop_profile(name)
        except ProfileIsNotRunning as ex:
            error_message(ex)

    def _show_profiles_list(self):
        """Show the list of profiles in a formatted table."""
        table = PrettyTable(["ID", "Name", "Active", "Proxy", "Description"])
        for profile in self.profile_factory.database.get_profiles():
            table.add_row(
                [
                    profile.id,
                    profile.name,
                    self.profile_factory.profile_is_running(profile.name),
                    profile.proxy_id,
                    profile.description
                ]
            )
        print(table)

    def _create_profile(self, name, args) -> None:
        """Create a profile with the given name and options."""
        options = {
            "proxy": ("-p","--proxy"),
            "description": ("-desc", "--description")
        }
        parsed_options = self._parse_options(args, options)
        proxy_id = int(parsed_options.get("proxy")) if parsed_options.get("proxy") else None
        description = parsed_options.get("description")
        try:
            self.profile_factory.create_profile(name, proxy_id, description)
            success_message(f"Profile '{name}' created")
        except ProfileExists as ex:
            error_message(ex)

    def _parse_options(self, args: tuple, options: dict[str, tuple]) -> dict:
        """Parse the options provided in the command arguments."""
        parsed_options = {
            option_name: next((arg if not arg.startswith(('-', '--')) else None for arg in args[args.index(option) + 1:]))
            for option_name, option_list in options.items()
            for option in option_list
            if option in args
        }
        return parsed_options

    def _help_proxy(self) -> None:
        help_text = """
Usage: proxy [command]

Available commands:
    - list                       : Show the list of proxies
    - create [server]            : Create a new proxy using the provided server address
    - create [-f | --file] [file_name] : Create proxies from the provided file
    - validate                   : Validate the existing proxies
    - delete [proxy_id]          : Delete the proxy with the specified ID
    - prune                      : Remove all proxies
    """
        print(help_text)

    def _help_profile(self) -> None:
        help_text = """
Usage: profile [command]

Available commands:
    - list                                      : Show the list of profiles
    - prune                                     : Delete all profiles
    - create [profile_name] [options]           : Create a new profile with the specified name and options
    - run [profile_name]                        : Run the profile with the specified name
    - stop [profile_name]                       : Stop the profile with the specified name
    - delete [profile_name]                     : Delete the profile with the specified name
    - change proxy [profile_name] [proxy_id]     : Change the proxy of the profile with the specified name using the given proxy ID
    - change [desc | description] [profile_name] [description] : Change the description of the profile with the specified name to the provided description
    """
        print(help_text)

    def do_help(self, arg):
        if arg == 'profile':
            self._help_profile()
        elif arg == 'proxy':
            self._help_proxy()
        else:
            print(CUSTOM_BANNER)

    def default(self, line):
        error_message("unknown command")

    def do_exit(self, arg):
        sys.exit()