import random

from PyQt6.QtWidgets import (
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

from browser.useragent import user_agents
from browser.profile import Profile
from browser import exceptions
from ui import utils, icons


class CreateProfileForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create profile")
        self.setStyleSheet(utils.load_style_sheet("create_profile.qss"))
        self.setFixedSize(400, 110)

        self.profile_name = QLineEdit()
        self.profile_name.setPlaceholderText("Name")
        self.profile_name.setFixedSize(280, 25)

        self.status = QComboBox()
        self.status.setPlaceholderText("Set status")
        self.status.addItem("New")
        self.status.addItem("Ready")
        self.status.setFixedSize(90, 25)

        self.user_agent = QLineEdit()
        self.user_agent.setReadOnly(True)
        self.user_agent.setFixedHeight(25)

        self.refresh_user_agent_button = QPushButton(icon=QIcon(icons.REFRESH_ICON))
        self.refresh_user_agent_button.setIconSize(QSize(25, 25))
        self.refresh_user_agent_button.setStyleSheet("""border: none;""")
        self.refresh_user_agent_button.clicked.connect(self.refresh_useragent)

        self.create_button = QPushButton(icon=QIcon(icons.CREATE_ICON), text="Create")
        self.create_button.clicked.connect(self.create)
        self.create_button.setIconSize(QSize(20, 20))

        main_layout = QVBoxLayout(self)
        name_layout = QHBoxLayout()
        useragent_layout = QHBoxLayout()
        create_layout = QHBoxLayout()

        name_layout.addWidget(self.profile_name)
        name_layout.addWidget(self.status)
        useragent_layout.addWidget(self.refresh_user_agent_button)
        useragent_layout.addWidget(self.user_agent)
        create_layout.addWidget(self.create_button)

        main_layout.addLayout(name_layout)
        main_layout.addLayout(useragent_layout)
        main_layout.addLayout(create_layout)

        self.refresh_useragent()
        self.show()
        

    def create(self):
        name = self.profile_name.text().strip()
        if not name:
            return
        status = self.status.currentText()
        user_agent = self.user_agent.text()

        profile = Profile(name=name, user_agent=user_agent, status=status)
        try:
            profile.save()
        except exceptions.ProfileExists:
            return
        
        self.parent().parent().table.update()
        self.close()

    def refresh_useragent(self):
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
        create_button.setIconSize(QSize(20, 20))

        h_layout.addWidget(self.info)
        h_layout.addWidget(self.proxy_input)
        v_layout.addWidget(create_button)

        main_layout.addLayout(h_layout)
        main_layout.addLayout(v_layout)

        self.show()