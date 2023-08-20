import random

from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QDialog,
    QLineEdit,
    QComboBox,
    QTextEdit
)
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon

from browser import profile_factory
from browser.user_agent import user_agents
from browser.exceptions import ProfileExists, InvalidProxyFormat, ProxyExist
from ui import icons
from ui import utils


class ManageBar(QHBoxLayout):
    def __init__(self, parent: QWidget | None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.create_profile_button = QPushButton(
            icon=QIcon(icons.CREATE_ICON), text="Create profile"
        )
        self.create_profile_button.setIconSize(QSize(20, 20))
        self.create_profile_button.clicked.connect(self.create_profile)

        self.add_proxy_button = QPushButton(
            icon=QIcon(icons.CREATE_ICON), text="Add proxy"
        )
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
        CreateProfileForm(self.parent())

    def add_proxy(self):
        CreateProxyForm(self.parent())


class CreateProfileForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create profile")
        self.setStyleSheet(utils.load_style_sheet("create_profile.qss"))
        self.setFixedSize(400, 100)

        self.profile_name = QLineEdit()
        self.profile_name.setPlaceholderText("Name")
        self.profile_name.setFixedWidth(280)

        self.status = QComboBox()
        self.status.setPlaceholderText("Set status")
        self.status.setFixedWidth(90)
        self.status.addItem("New")
        self.status.addItem("Ready")

        self.user_agent = QLineEdit()
        self.user_agent.setReadOnly(True)

        self.refresh_user_agent_button = QPushButton(icon=QIcon(icons.REFRESH_ICON))
        self.refresh_user_agent_button.setIconSize(QSize(20, 20))
        self.refresh_user_agent_button.setStyleSheet("""border: none;""")
        self.refresh_user_agent_button.clicked.connect(self.refresh_user_agent)

        self.create_button = QPushButton(icon=QIcon(icons.CREATE_ICON), text="Create")
        self.create_button.clicked.connect(self.create)

        main_layout = QVBoxLayout(self)
        name_layout = QHBoxLayout()
        useragent_layout = QHBoxLayout()
        create_layout = QVBoxLayout()

        name_layout.addWidget(self.profile_name)
        name_layout.addWidget(self.status)
        useragent_layout.addWidget(self.refresh_user_agent_button)
        useragent_layout.addWidget(self.user_agent)
        create_layout.addWidget(self.create_button)

        main_layout.addLayout(name_layout)
        main_layout.addLayout(useragent_layout)
        main_layout.addLayout(create_layout)

        self.refresh_user_agent()
        self.show()

    def create(self):
        name = self.profile_name.text().strip()
        if not name:
            return
        status = self.status.currentText()
        user_agent = self.user_agent.text()

        try:
            profile_factory.create_profile(
                name=name,
                proxy_id=None,
                note=None,
                status=status or "New",
                user_agent=user_agent,
            )
        except ProfileExists:
            return

        self.parent().parent().content.update()
        self.deleteLater()

    def refresh_user_agent(self):
        user_agent = random.choice(user_agents)
        self.user_agent.setText(user_agent)


class CreateProxyForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add proxy")

        main_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setText("Allowed format:\n    username:password@ip_address:port\nYou can add an unlimited number of proxies.\nPaste each proxy on a new line.\nIf the proxy does not match the format, it will not be added.")

        self.proxy_input = QTextEdit()
        create_button = QPushButton(QIcon(icons.CREATE_ICON), "Add")
        create_button.clicked.connect(self.create)

        h_layout.addWidget(self.info)
        h_layout.addWidget(self.proxy_input)
        v_layout.addWidget(create_button)

        main_layout.addLayout(h_layout)
        main_layout.addLayout(v_layout)

        self.show()

    def create(self):
        servers = self.proxy_input.toPlainText().split("\n")
        for server in servers:
            try:
                profile_factory.create_proxy(server)
            except (InvalidProxyFormat, ProxyExist) as ex:
                continue
        
        self.parent().parent().content.update()
        self.deleteLater()