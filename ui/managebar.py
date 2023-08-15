from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QDialog, QLineEdit, QComboBox
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon

from browser import profile_factory
from ui import icons
from ui import utils


class ManageBar(QHBoxLayout):
    def __init__(self, parent: QWidget | None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.create_profile_button = QPushButton(icon=QIcon(icons.CREATE_ICON), text="Create profile")
        self.create_profile_button.setIconSize(QSize(20, 20))
        self.create_profile_button.clicked.connect(self.create_profile)

        self.add_proxy_button = QPushButton(icon=QIcon(icons.CREATE_ICON), text="Add proxy")
        self.add_proxy_button.setIconSize(QSize(20, 20))
        self.add_proxy_button.clicked.connect(self.add_proxy)

        self.addStretch(10)
        self.addWidget(self.create_profile_button)
        self.addWidget(self.add_proxy_button)
        self.add_proxy_button.hide()

    def set_profiles_active(self):
        self.create_profile_button.show()
        self.add_proxy_button.hide()

    def set_proxies_active(self):
        self.add_proxy_button.show()
        self.create_profile_button.hide()

    def create_profile(self):
        profile_form = CreateProfileForm(self.parent())

    def add_proxy(self):
        pass


class CreateProfileForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create profile")
        self.setStyleSheet(utils.load_style_sheet("create_profile.qss"))
        self.setFixedSize(400, 80)

        self.profile_name = QLineEdit()
        self.profile_name.setPlaceholderText("Name")
        self.profile_name.setFixedWidth(280)

        self.status = QComboBox()
        self.status.setPlaceholderText("Set status")
        self.status.setFixedWidth(90)
        self.status.addItem("Set status")
        self.status.addItem("New")
        self.status.addItem("Ready")

        self.create_button = QPushButton(icon=QIcon(icons.CREATE_ICON), text="Create")
        self.create_button.clicked.connect(self.create)

        main_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()
        
        h_layout.addWidget(self.profile_name)
        h_layout.addWidget(self.status)
        v_layout.addWidget(self.create_button)

        main_layout.addLayout(h_layout)
        main_layout.addLayout(v_layout)

        self.show()

    def create(self):
        name = self.profile_name.text().strip()
        profile_factory.create_profile(name)
        self.parent().parent().content.update()
        self.deleteLater()


class CreateProxyForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add proxy")

        main_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()