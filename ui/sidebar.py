from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

from ui import icons
from ui import utils


class SideBarButton(QPushButton):
    def __init__(self, *args, tool_tip=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFixedSize(40, 40)
        self.setIconSize(QSize(30, 30))
        self.setToolTip(tool_tip)

    def set_active(self):
        self.setChecked(True)

    def set_inactive(self):
        self.setChecked(False)


class Sidebar(QVBoxLayout):
    def __init__(self, parent: QWidget = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Create sidebar buttons
        self.profiles_button = SideBarButton(
            icon=QIcon(icons.PROFILES_MENU_ICON), tool_tip="Profiles"
        )
        self.proxies_button = SideBarButton(
            icon=QIcon(icons.PROXIES_MENU_ICON), tool_tip="Proxies"
        )
        self.web3_button = SideBarButton(
            icon=QIcon(icons.WEB3_ICON), tool_tip="Web3 accounts"
        )

        # Set profiles button as active
        self.set_profiles_active()

        # Sidebar settings
        self.addWidget(self.profiles_button)
        self.addWidget(self.proxies_button)
        self.addWidget(self.web3_button)
        self.addStretch(5)

    def set_profiles_active(self):
        self.proxies_button.set_inactive()
        self.web3_button.set_inactive()
        self.profiles_button.set_active()

    def set_proxies_active(self):
        self.profiles_button.set_inactive()
        self.web3_button.set_inactive()
        self.proxies_button.set_active()

    def set_web3_accounts_active(self):
        self.profiles_button.set_inactive()
        self.proxies_button.set_inactive()
        self.web3_button.set_active()
