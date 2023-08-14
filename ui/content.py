from typing import Iterable

from PyQt6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from ui.settings import APP_WIDTH, SIDEBAR_WIDTH, SIDEBAR_HEIGHT
from ui import icons
from ui import utils


class ContentItem(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)


class ContentView(QTableWidget):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent)

        self.setGeometry(SIDEBAR_WIDTH, 0, APP_WIDTH - SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.setStyleSheet(utils.load_style_sheet("content.qss"))


class ProfileActiveButton(QPushButton):
    def __init__(self, icon: QIcon, text: str, profile_name: str, row: int, col: int, is_active: bool, *args, **kwargs):
        super().__init__(icon, text, *args, **kwargs)

        self.is_active = is_active
        self.profile_name = profile_name
        self.row = row
        self.col = col


class ProfilesView(ContentView):
    COLUMN_NAMES = ["Name", "", "Status", "Notes", "Proxy"]

    def __init__(self, parent: QWidget | None, data: Iterable[Iterable]):
        super().__init__(parent)

        self.setColumnCount(len(self.COLUMN_NAMES))
        self.setHorizontalHeaderLabels(self.COLUMN_NAMES)
        self.setRowCount(len(data))

        self.setItems(data)

    def setItems(self, data: Iterable[Iterable]):
        for i, profile in enumerate(data):
            self.setItem(i, 0, ContentItem(QIcon(icons.PROFILE_ICON), profile[0]))
            button = ProfileActiveButton(QIcon(icons.START_ICON), "Start", profile[0], i, 1, profile[1]) if not profile[1] else ProfileActiveButton(QIcon(icons.STOP_ICON), "Stop", profile[0], i, 1, profile[1])
            button.clicked.connect(self.change_running_status)
            self.setCellWidget(i, 1, button)
            self.setItem(i, 2, ContentItem(profile[2]))
            self.setItem(i, 3, ContentItem(profile[3]))
            self.setItem(i, 4, ContentItem(profile[4]))

    def change_running_status(self):
        button: ProfileActiveButton = self.sender()
        profile_factory = self.parent().profile_factory
        if button.is_active:
            profile_factory.stop_profile(button.profile_name)
            new_button = ProfileActiveButton(QIcon(icons.START_ICON), "Start", button.profile_name, button.row, button.col, not button.is_active)
            new_button.clicked.connect(self.change_running_status)
            self.setCellWidget(button.row, button.col, new_button)
        else:
            profile_factory.run_profile(button.profile_name)
            new_button = ProfileActiveButton(QIcon(icons.STOP_ICON), "Stop", button.profile_name, button.row, button.col, not button.is_active)
            new_button.clicked.connect(self.change_running_status)
            self.setCellWidget(button.row, button.col, new_button)


class ProxiesView(ContentView):
    COLUMN_NAMES = ["Country", "Address", "Port", "Username", "Password", "Valid", "Profiles count"]

    def __init__(self, parent: QWidget | None, data: Iterable[Iterable]):
        super().__init__(parent)

        self.setColumnCount(len(self.COLUMN_NAMES))
        self.setHorizontalHeaderLabels(self.COLUMN_NAMES)
        self.setRowCount(len(data))

        self.setItems(data)

    def setItems(self, data: Iterable[Iterable]):
        for i, proxy in enumerate(data):
            self.setItem(i, 0, ContentItem(proxy[0]))
            self.setItem(i, 1, ContentItem(proxy[1]))
            self.setItem(i, 2, ContentItem(proxy[2]))
            self.setItem(i, 3, ContentItem(proxy[3]))
            self.setItem(i, 4, ContentItem(proxy[4]))
            self.setItem(i, 5, ContentItem(proxy[5]))
