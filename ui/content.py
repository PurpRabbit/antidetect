from typing import Iterable

from PyQt6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QComboBox, QVBoxLayout, QTextEdit, QDialog
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from browser import profile_factory
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

        self.setGeometry(SIDEBAR_WIDTH, 45, APP_WIDTH - SIDEBAR_WIDTH, SIDEBAR_HEIGHT - 45)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.setStyleSheet(utils.load_style_sheet("content.qss"))


class ProfilesView(ContentView):
    COLUMN_NAMES = ["Name", "", "Status", "Notes", "Proxy"]

    def __init__(self, parent: QWidget | None):
        super().__init__(parent)

        self.setColumnCount(len(self.COLUMN_NAMES))
        self.setHorizontalHeaderLabels(self.COLUMN_NAMES)
        self.update()

    def setItems(self, data: Iterable[Iterable]):
        for i, profile in enumerate(data):
            self.setItem(i, 0, ContentItem(QIcon(icons.PROFILE_ICON), profile[0]))

            button = ProfileActiveButton(QIcon(icons.START_ICON), "Start", profile[0], i, 1, profile[1]) if not profile[1] else ProfileActiveButton(QIcon(icons.STOP_ICON), "Stop", profile[0], i, 1, profile[1])
            button.clicked.connect(self.change_running_status)
            self.setCellWidget(i, 1, button)

            status = ProfileStatusCombo(["New", "Ready"], profile[2], profile[0], i, 2)
            status.currentIndexChanged.connect(self.update_status)
            self.setCellWidget(i, 2, status)

            notes = ProfileNotesButton(QIcon(icons.EDIT_ICON), text=(profile[3] if profile[3] != "None" else "note"), profile_name=profile[0], row=i, col=3)
            notes.clicked.connect(self.update_note)
            self.setCellWidget(i, 3, notes)

            self.setItem(i, 4, ContentItem(profile[4]))

    def update_note(self):
        self.sender_note: ProfileNotesButton = self.sender()

        self.note_dialog = QDialog()
        self.note_dialog.setWindowTitle("Note")
        layout = QVBoxLayout(self.note_dialog)
        
        self.note = QTextEdit()
        self.note.setPlaceholderText("Enter note...")
        if self.sender_note.text_ != "note":
            self.note.setText(self.sender_note.text_)

        save_button = QPushButton(QIcon(icons.SAVE_ICON), "Save")
        save_button.clicked.connect(self.save_note)

        layout.addWidget(self.note)
        layout.addWidget(save_button)

        self.note_dialog.exec()

    def save_note(self):
        profile_factory.database.change_profile_note(self.sender_note.profile_name, self.note.toPlainText())
        self.update()
        self.note_dialog.deleteLater()

    def update_status(self):
        combo: ProfileStatusCombo = self.sender()
        profile_factory.database.update_profile_status(combo.profile_name, combo.currentText())

    def update(self):
        profiles = [
            (profile.name, profile_factory.profile_is_running(profile.name), profile.status, str(profile.note), str(profile.proxy_id))
            for profile in profile_factory.database.get_profiles()
        ]
        self.setRowCount(len(profiles))
        self.setItems(profiles)

    def change_running_status(self):
        button: ProfileActiveButton = self.sender()
        if button.is_active:
            profile_factory.stop_profile(button.profile_name)
            new_button = ProfileActiveButton(
                QIcon(icons.START_ICON), 
                "Start", 
                button.profile_name, 
                button.row, button.col, 
                not button.is_active
            )
            new_button.clicked.connect(self.change_running_status)
            self.setCellWidget(button.row, button.col, new_button)
        else:
            profile_factory.run_profile(button.profile_name)
            new_button = ProfileActiveButton(
                QIcon(icons.STOP_ICON), 
                "Stop", 
                button.profile_name, 
                button.row, button.col, 
                not button.is_active
            )
            new_button.clicked.connect(self.change_running_status)
            self.setCellWidget(button.row, button.col, new_button)


class ProxiesView(ContentView):
    COLUMN_NAMES = ["Country", "Address", "Port", "Username", "Password", "Valid", "Profiles count"]

    def __init__(self, parent: QWidget | None):
        super().__init__(parent)

        self.setColumnCount(len(self.COLUMN_NAMES))
        self.setHorizontalHeaderLabels(self.COLUMN_NAMES)
        self.update()

    def setItems(self, data: Iterable[Iterable]):
        for i, proxy in enumerate(data):
            self.setItem(i, 0, ContentItem(proxy[0]))
            self.setItem(i, 1, ContentItem(proxy[1]))
            self.setItem(i, 2, ContentItem(proxy[2]))
            self.setItem(i, 3, ContentItem(proxy[3]))
            self.setItem(i, 4, ContentItem(proxy[4]))
            self.setItem(i, 5, ContentItem(proxy[5]))

    def update(self):
        proxies = []
        for proxy in profile_factory.database.get_proxies():
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
                    len([profile for profile in profile_factory.database.get_profiles() if profile.proxy_id == proxy.id]),
                )
            )
        self.setRowCount(len(proxies))
        self.setItems(proxies)


class ProfileActiveButton(QPushButton):
    def __init__(self, icon: QIcon, text: str, profile_name: str, row: int, col: int, is_active: bool, *args, **kwargs):
        super().__init__(icon, text, *args, **kwargs)

        self.is_active = is_active
        self.profile_name = profile_name
        self.row = row
        self.col = col

        style_sheet_file = "profile_active.qss" if self.is_active else "profile_inactive.qss"
        self.setStyleSheet(utils.load_style_sheet(style_sheet_file))


class ProfileStatusCombo(QComboBox):
    def __init__(self, items: Iterable[str], active_status: str, profile_name: str, row: int, col: int):
        super().__init__()

        self.addItems(items)
        self.profile_name = profile_name
        self.active_status = active_status
        self.row = row
        self.col = col

        if active_status:
            self.setCurrentIndex(items.index(self.active_status))


class ProfileNotesButton(QPushButton):
    def __init__(self, icon: QIcon, text: str, profile_name, row: int, col: int):
        super().__init__(icon, text)

        self.text_ = text
        self.profile_name = profile_name
        self.row = row
        self.col = col

        self.setIconSize(QSize(10, 10))