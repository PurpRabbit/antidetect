from PyQt6.QtWidgets import QMainWindow, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

from ui.sidebar import Sidebar
from ui.content import (
    ContentView,
    ProfileContentView,
    ProxyContentView,
    Web3AccountsContentView,
)
from ui import icons, utils
from ui.settings import (
    APP_WIDTH,
    APP_HEIGHT,
    SIDEBAR_WIDTH,
    SIDEBAR_HEIGHT,
    MANAGEBAR_WIDTH,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Antidetect Browser by PurpRabbit")
        self.setWindowIcon(QIcon(icons.MAIN_WINDOW_PIC))
        self.setGeometry(500, 200, APP_WIDTH, APP_HEIGHT)
        self.setMinimumSize(APP_WIDTH, APP_HEIGHT)
        self.setStyleSheet(utils.load_style_sheet("mainwindow.qss"))

        self.sidebar_widget = QWidget(self)
        self.sidebar_widget.setGeometry(0, 0, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
        self.sidebar_widget.setStyleSheet(utils.load_style_sheet("sidebar.qss"))

        self.sidebar = Sidebar(self.sidebar_widget)
        self.sidebar.profiles_button.clicked.connect(self.set_profiles_active)
        self.sidebar.proxies_button.clicked.connect(self.set_proxies_active)
        self.sidebar.web3_button.clicked.connect(self.set_web3_accounts_active)

        self.resizeEvent = self.resize_event

        self.show_content(ProfileContentView)

    def resize_event(self, event):
        super().resizeEvent(event)
        self.update_size()

    def update_size(self):
        window_size: QSize = self.size()
        self.content.setGeometry(
            SIDEBAR_WIDTH, 0, window_size.width() - SIDEBAR_WIDTH, window_size.height()
        )
        self.sidebar_widget.setGeometry(0, 0, SIDEBAR_WIDTH, window_size.height())

    def set_profiles_active(self):
        if isinstance(self.content, ProxyContentView):
            self.content.deleteLater()
            self.show_content(ProfileContentView)
            self.sidebar.set_profiles_active()

    def set_proxies_active(self):
        if isinstance(self.content, (ProfileContentView, Web3AccountsContentView)):
            self.content.deleteLater()
            self.show_content(ProxyContentView)
            self.sidebar.set_proxies_active()

    def set_web3_accounts_active(self):
        if isinstance(self.content, (ProfileContentView, ProxyContentView)):
            self.content.deleteLater()
            self.show_content(Web3AccountsContentView)
            self.sidebar.set_web3_accounts_active()

    def show_content(self, contentview: ContentView):
        self.content = contentview(self)
        self.content.show()
