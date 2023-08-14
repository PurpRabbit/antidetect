from PyQt6.QtWidgets import QMainWindow, QWidget

from ui.settings import APP_WIDTH, APP_HEIGHT, SIDEBAR_WIDTH, SIDEBAR_HEIGHT
from ui.sidebar import Sidebar
from ui.content import ProfilesView, ProxiesView
from ui import utils
from browser.factory import ProfileFactory


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Antidetect Browser by PurpRabbit")
        self.setGeometry(500, 200, APP_WIDTH, APP_HEIGHT)
        self.setFixedSize(APP_WIDTH, APP_HEIGHT)
        self.setStyleSheet(utils.load_style_sheet("mainwindow.qss"))

        self.profile_factory = ProfileFactory()

        self.init_ui()

    def init_ui(self):
        self.sidebar_widget = QWidget(self)
        self.sidebar_widget.setGeometry(0, 0, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
        self.sidebar_widget.setStyleSheet(utils.load_style_sheet("sidebar.qss"))
        self.sidebar = Sidebar(self.sidebar_widget)
        self.sidebar.profiles_button.clicked.connect(self.set_profiles_active)
        self.sidebar.proxies_button.clicked.connect(self.set_proxies_active)

        self.show_profiles_content()

    def show_profiles_content(self):
        profiles = [
            (profile.name, self.profile_factory.profile_is_running(profile.name), '', str(profile.description), str(profile.proxy_id))
            for profile in self.profile_factory.database.get_profiles()
        ]

        self.content = ProfilesView(self, profiles)
        self.content.show()

    def show_proxies_content(self):
        proxies = []
        for proxy in self.profile_factory.database.get_proxies():
            username, password, address, port = proxy.split_server()
            proxies.append(
                (
                    proxy.id,
                    proxy.country,
                    address,
                    port,
                    username,
                    password,
                    proxy.is_valid,
                    len([profile for profile in self.profile_factory.database.get_profiles() if profile.proxy_id == proxy.id]),
                )
            )
        
        self.content = ProxiesView(self, proxies)
        self.content.show()

    def set_profiles_active(self):
        if isinstance(self.content, ProxiesView):
            self.content.deleteLater()
            self.show_profiles_content()
            self.sidebar.set_profiles_active()

    def set_proxies_active(self):
        if isinstance(self.content, ProfilesView):
            self.content.deleteLater()           
            self.show_proxies_content()
            self.sidebar.set_proxies_active()