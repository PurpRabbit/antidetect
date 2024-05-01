from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QDialog,
    QLineEdit,
    QComboBox,
    QTextEdit,
)
from PyQt6.QtCore import QSize, QRect
from PyQt6.QtGui import QIcon

from ui.table import Table
from ui.form import CreateProfileForm, CreateProxyForm
from ui.settings import (
    APP_WIDTH,
    APP_HEIGHT,
    SIDEBAR_WIDTH,
    SIDEBAR_HEIGHT,
    MANAGEBAR_HEIGHT,
    MANAGEBAR_WIDTH,
)
from ui import icons


class PageManageBar(QHBoxLayout):
    def __init__(self, parent: QWidget, *args, **kwargs):
        button_text = kwargs.pop("text")
        super().__init__(parent, *args, **kwargs)

        self.create_entity_button = QPushButton(
            icon=QIcon(icons.CREATE_ICON), text=button_text
        )
        self.create_entity_button.setIconSize(QSize(30, 30))
        self.create_entity_button.clicked.connect(self.create_entity)
        self.addStretch(10)
        self.addWidget(self.create_entity_button)

        self.delete_entity_button = QPushButton(icon=QIcon(icons.DELETE_ICON))
        self.delete_entity_button.clicked.connect(self.delete_entity)
        self.addWidget(self.delete_entity_button)
        self.delete_entity_button.hide()

    def create_entity(self):
        raise NotImplementedError

    def delete_entity(self):
        table: Table = self.parent().parent().table
        for row in table.checked_rows:
            row.entity.delete()

        table.update()


class ProfileManageBar(PageManageBar):
    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, text="Create profile", **kwargs)

    def create_entity(self):
        CreateProfileForm(self.parent())


class ProxyManageBar(PageManageBar):
    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, text="Add proxy", **kwargs)

    def create_entity(self):
        CreateProxyForm(self.parent())


class Web3AccountsManageBar(PageManageBar):
    def __init__(self, parent: QWidget, *args, **kwargs):
        super().__init__(parent, *args, text="Add Web3 Account", **kwargs)

    def create_entity(self): ...
