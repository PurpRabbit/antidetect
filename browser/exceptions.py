class ProfileExists(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class ProfileDoesNotExist(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class InvalidProxyFormat(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class ProxyDoesNotExist(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class ProfileIsRunning(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class ProfileIsNotRunning(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class ProxyExist(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
