from typing import Iterable, Callable
from threading import Thread

from PyQt6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QComboBox, QVBoxLayout, QTextEdit, QDialog, QCheckBox
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QIcon

from browser import profile_factory
from browser.profile import Profile
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
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setGeometry(SIDEBAR_WIDTH, 45, APP_WIDTH - SIDEBAR_WIDTH, SIDEBAR_HEIGHT - 45)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.setStyleSheet(utils.load_style_sheet("content.qss"))

        self.checked_rows = set()

    def checkbox_clicked(self) -> None:
        sender: QCheckBox = self.sender()
        if sender.isChecked():
            self.checked_rows.add(sender)
        else:
            self.checked_rows.remove(sender)

        delete_button: QPushButton = self.parent().managebar.delete_entity_button
        if self.checked_rows and delete_button.isHidden():
           delete_button.show()
        elif not self.checked_rows and not delete_button.isHidden():
            delete_button.hide()

class ProfilesView(ContentView):
    COLUMN_NAMES = ["", "Name", "", "Status", "Notes", "Proxy"]

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setColumnCount(len(self.COLUMN_NAMES))
        self.setHorizontalHeaderLabels(self.COLUMN_NAMES)
        self.setColumnWidth(0, 5)
        self.update()

    def set_items(self, data: Iterable[Iterable]):
        proxies = self._get_proxies()

        for i, profile in enumerate(data):
            checkbox = ProfileCheckBox(profile[0], i)
            checkbox.clicked.connect(self.checkbox_clicked)
            self.setCellWidget(i, 0, checkbox)

            self.setItem(i, 1, ContentItem(QIcon(icons.PROFILE_ICON), profile[0]))

            button = ProfileActiveButton(QIcon(icons.START_ICON), "Start", profile[0], i, 2, profile[1]) if not profile[1] else ProfileActiveButton(QIcon(icons.STOP_ICON), "Stop", profile[0], i, 2, profile[1])
            button.clicked.connect(self.change_running_status)
            self.setCellWidget(i, 2, button)

            status = ProfileStatusCombo(["New", "Ready"], profile[2], profile[0], i, 3)
            status.currentIndexChanged.connect(self.update_status)
            self.setCellWidget(i, 3, status)

            notes = ProfileNotesButton(QIcon(icons.EDIT_ICON), text=(profile[3] if profile[3] != "None" else "note"), profile_name=profile[0], row=i, col=4)
            notes.clicked.connect(self.update_note)
            self.setCellWidget(i, 4, notes)

            proxy = ProfileProxyCombo(
                proxies, 
                profile_factory.database.get_proxy(profile[4]).server if profile[4] else None,
                profile[4], profile[0], row=i, col=5)
            proxy.currentIndexChanged.connect(self.update_proxy)
            self.setCellWidget(i, 5, proxy)

    def _get_proxies(self) -> list[str]:
        proxies = [(proxy.id, proxy.server) for proxy in profile_factory.database.get_proxies()]
        proxies.insert(0, (0, ""))
        return proxies

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
    
    def update_proxy(self):
        combo: ProfileProxyCombo = self.sender()
        current_combo_text = combo.currentText()
        for id_, server in combo.items:
            if server == current_combo_text:
                profile_factory.database.change_profile_proxy(combo.profile_name, id_)
                break

    def update(self):
        profiles = [
            (profile.name, profile_factory.profile_is_running(profile.name), profile.status, str(profile.note), int(profile.proxy_id))
            for profile in profile_factory.database.get_profiles()
        ]
        self.setRowCount(len(profiles))
        self.set_items(profiles)

    def change_running_status(self):
        button: ProfileActiveButton = self.sender()

        if button.is_active:
            profile_factory.stop_profile(button.profile_name)
            button_text = "Start"
            button_icon = QIcon(icons.START_ICON)
        else:
            profile = profile_factory.run_profile(button.profile_name)
            # Worker checks if browser was closed by clicking on X button
            worker = ProfileWorker(profile)
            on_finish = self.profile_finished(profile, button.row, button.col, not button.is_active)
            worker.finished_signal.connect(on_finish)
            worker.start()
            button_text = "Stop"
            button_icon = QIcon(icons.STOP_ICON)

        new_button = ProfileActiveButton(
            button_icon, 
            button_text, 
            button.profile_name, 
            button.row, button.col, 
            not button.is_active
        )
        new_button.clicked.connect(self.change_running_status)
        self.setCellWidget(button.row, button.col, new_button)

    def profile_finished(self, profile: Profile, row: int, col: int, is_active: bool):
        def wrapper(): 
            new_button = ProfileActiveButton(
                QIcon(icons.START_ICON), 
                "Start", 
                profile.name, 
                row, col, 
                not is_active
            )
            new_button.clicked.connect(self.change_running_status)
            self.setCellWidget(row, col, new_button)
        return wrapper


class ProxiesView(ContentView):
    COLUMN_NAMES = ["", "Country", "Address", "Port", "Username", "Password", "Valid", "Profiles count"]

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setColumnCount(len(self.COLUMN_NAMES))
        self.setHorizontalHeaderLabels(self.COLUMN_NAMES)
        self.setColumnWidth(0, 5)
        self.update()

    def set_items(self, data: Iterable[Iterable]):
        for i, proxy in enumerate(data):
            checkbox = ProxyCheckBox(proxy[0], i)
            checkbox.clicked.connect(self.checkbox_clicked)
            self.setCellWidget(i, 0, checkbox)
            self.setItem(i, 1, ContentItem(proxy[1]))
            self.setItem(i, 2, ContentItem(proxy[2]))
            self.setItem(i, 3, ContentItem(proxy[3]))
            self.setItem(i, 4, ContentItem(proxy[4]))
            self.setItem(i, 5, ContentItem(proxy[5]))
            self.setItem(i, 6, ContentItem(proxy[6]))
            self.setItem(i, 7, ContentItem(proxy[7]))

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
                    str(len([profile for profile in profile_factory.database.get_profiles() if profile.proxy_id == proxy.id])),
                )
            )
        self.setRowCount(len(proxies))
        self.set_items(proxies)


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


class ProfileProxyCombo(QComboBox):
    def __init__(self, items: Iterable[str], active_proxy: str, proxy_id: int, profile_name: str, row: int, col: int):
        super().__init__()

        self.addItems([item[1] for item in items])
        self.items = items
        self.profile_name = profile_name
        self.active_proxy = active_proxy
        self.proxy_id = proxy_id
        self.row = row
        self.col = col

        if active_proxy:
            self.setCurrentIndex(self.proxy_id)


class ProfileNotesButton(QPushButton):
    def __init__(self, icon: QIcon, text: str, profile_name: str, row: int, col: int):
        super().__init__(icon, text)

        self.text_ = text
        self.profile_name = profile_name
        self.row = row
        self.col = col

        self.setIconSize(QSize(10, 10))


class CheckBoxEntity(QCheckBox):
    def __init__(self, entity: str, row: int):
        super().__init__()

        self.entity = entity
        self.row = row

    def __hash__(self):
        return self.row
    

class ProfileCheckBox(CheckBoxEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProxyCheckBox(CheckBoxEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProfileWorker(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, profile: Profile, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.profile = profile

    def run(self):
        while self.profile.thread_running:
            pass
        
        self.finished_signal.emit()
