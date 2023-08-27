from PyQt6.QtWidgets import QMainWindow, QWidget
from PyQt6.QtGui import QIcon

from ui.settings import (
    APP_WIDTH,
    APP_HEIGHT,
    SIDEBAR_WIDTH,
    SIDEBAR_HEIGHT,
    MANAGEBAR_WIDTH,
    MANAGEBAR_HEIGHT,
)
from ui.sidebar import Sidebar
from ui.managebar import ManageBar
from ui.content import ProfilesView, ProxiesView
from ui import utils
from ui import icons
from browser import profile_factory


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Antidetect Browser by PurpRabbit")
        self.setWindowIcon(QIcon(icons.MAIN_WINDOW_PIC))
        self.setGeometry(500, 200, APP_WIDTH, APP_HEIGHT)
        self.setFixedSize(APP_WIDTH, APP_HEIGHT)
        self.setStyleSheet(utils.load_style_sheet("mainwindow.qss"))

        self.init_ui()

    def init_ui(self):
        self.sidebar_widget = QWidget(self)
        self.sidebar_widget.setGeometry(0, 0, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
        self.sidebar_widget.setStyleSheet(utils.load_style_sheet("sidebar.qss"))

        self.sidebar = Sidebar(self.sidebar_widget)
        self.sidebar.profiles_button.clicked.connect(self.set_profiles_active)
        self.sidebar.proxies_button.clicked.connect(self.set_proxies_active)

        self.manage_bar_widget = QWidget(self)
        self.manage_bar_widget.setGeometry(
            SIDEBAR_WIDTH, 0, MANAGEBAR_WIDTH, MANAGEBAR_HEIGHT
        )
        self.manage_bar_widget.setStyleSheet(utils.load_style_sheet("managebar.qss"))

        self.managebar = ManageBar(self.manage_bar_widget)
        self.managebar.delete_entity_button.clicked.connect(self.delete_entity)

        self.show_profiles_content()

    def delete_entity(self):
        if isinstance(self.content, ProfilesView):
            for checkbox in self.content.checked_rows:
                profile_factory.delete_profile(checkbox.entity)
        elif isinstance(self.content, ProxiesView):
            for checkbox in self.content.checked_rows:
                profile_factory.delete_proxy(checkbox.entity)
        
        self.content.checked_rows.clear()
        self.content.update()
        self.managebar.delete_entity_button.hide()

    def show_profiles_content(self):
        self.content = ProfilesView(self)
        self.content.show()
        self.managebar.delete_entity_button.hide()

    def show_proxies_content(self):
        self.content = ProxiesView(self)
        self.content.show()
        self.managebar.delete_entity_button.hide()

    def set_profiles_active(self):
        if isinstance(self.content, ProxiesView):
            self.content.deleteLater()
            self.show_profiles_content()
            self.sidebar.set_profiles_active()
            self.managebar.set_profiles_active()

    def set_proxies_active(self):
        if isinstance(self.content, ProfilesView):
            self.content.deleteLater()
            self.show_proxies_content()
            self.sidebar.set_proxies_active()
            self.managebar.set_proxies_active()
