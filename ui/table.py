from typing import Iterable
from threading import Thread
import time

from PyQt6.QtWidgets import (
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QComboBox,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
    QDialog,
    QTextEdit,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from browser.profile import Profile, Proxy
from ui.settings import (
    SIDEBAR_HEIGHT,
    MANAGEBAR_HEIGHT,
    MANAGEBAR_WIDTH,
)
from ui import icons
from utils import threadutil


class Table(QTableWidget):
    COLUMN_NAMES = []

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.checked_rows = set()

        if not self.COLUMN_NAMES:
            raise ValueError("COLUMN NAMES attr cant be empty")

        self.setGeometry(
            0, MANAGEBAR_HEIGHT, MANAGEBAR_WIDTH, SIDEBAR_HEIGHT - MANAGEBAR_HEIGHT
        )
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.setColumnCount(len(self.COLUMN_NAMES))
        self.setHorizontalHeaderLabels(self.COLUMN_NAMES)

        self.update()

    def update():
        raise NotImplementedError

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


class TableItem(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)


class CheckBoxEntity(QCheckBox):
    def __init__(self, entity: str, row: int):
        super().__init__()

        self.entity = entity
        self.row = row

    def __hash__(self):
        return self.row


class ProfileTable(Table):
    COLUMN_NAMES = ["Name", "", "Status", "Notes", "Proxy"]

    running_profiles = set()
    running_threads = dict()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def update(self):
        profiles = Profile.all()
        self.setRowCount(len(profiles))

        for index, profile in enumerate(profiles):
            self._set_name_column(index, 0, profile)
            self._set_start_button(index, 1, profile)
            self._set_status_combo(index, 2, profile)
            self._set_note(index, 3, profile)
            self._set_proxy(index, 4, profile)

    def _set_proxy(self, row: int, col: int, profile: Profile):
        proxies = [proxy.server for proxy in Proxy.all_models()]
        proxies.insert(0, None)

        if not Proxy.exists(profile.proxy_server):
            profile.set_proxy(None)

        active_proxy = profile.proxy_server

        proxy = ProfileProxyCombo(
            items=proxies,
            active_proxy=active_proxy,
            proxy_id=proxies.index(active_proxy),
            profile=profile,
            row=row,
            col=col,
        )

        proxy.currentIndexChanged.connect(self._update_proxy)
        self.setCellWidget(row, col, proxy)

    def _update_proxy(self):
        combo: ProfileProxyCombo = self.sender()
        profile: Profile = combo.profile
        current_combo_proxy_server = combo.currentText()
        for server in combo.items:
            if server == current_combo_proxy_server:
                profile.set_proxy(server)
                break

    def _set_note(self, row: int, col: int, profile: Profile):
        note = ProfileNotesButton(
            QIcon(icons.EDIT_ICON),
            text=(profile.note if profile.note != "None" else "note"),
            profile=profile,
            row=row,
            col=col,
        )
        note.clicked.connect(self._update_note)
        self.setCellWidget(row, col, note)

    def _update_note(self):
        self.sender_note: ProfileNotesButton = self.sender()

        self.note_dialog = QDialog()
        self.note_dialog.setWindowTitle("Note")
        layout = QVBoxLayout(self.note_dialog)

        self.note = QTextEdit()
        self.note.setPlaceholderText("Enter note...")
        if self.sender_note.text_ != "note":
            self.note.setText(self.sender_note.text_)

        save_button = QPushButton(QIcon(icons.SAVE_ICON), "Save")
        save_button.clicked.connect(self._save_note)

        layout.addWidget(self.note)
        layout.addWidget(save_button)

        self.note_dialog.exec()

    def _save_note(self):
        profile: Profile = self.sender_note.profile
        profile.set_note(self.note.toPlainText())
        self.update()
        self.note_dialog.deleteLater()

    def _set_status_combo(self, row: int, col: int, profile: Profile):
        status_combo = ProfileStatusCombo(["New", "Ready"], profile, row, col)
        status_combo.currentIndexChanged.connect(self._update_status)
        self.setCellWidget(row, col, status_combo)

    def _update_status(self):
        sender: ProfileStatusCombo = self.sender()
        profile: Profile = sender.profile
        profile.set_status(sender.currentText())

    def _set_start_button(self, row: int, col: int, profile: Profile):
        if profile not in self.running_profiles:
            icon = QIcon(icons.START_ICON)
            button_text = "Start"
            is_running = False
        else:
            icon = QIcon(icons.STOP_ICON)
            button_text = "Stop"
            is_running = True
        button = ProfileActiveButton(icon, button_text, profile, row, col, is_running)
        button.clicked.connect(self.change_running_status)
        self.setCellWidget(row, col, button)

    def change_running_status(self, button=None):
        if not button:
            button: ProfileActiveButton = self.sender()
        if button.is_running:
            ProfileTable.running_profiles.remove(button.profile)
            self._wait_thread(button.profile.name)
            button.profile.stop()
            button_text = "Start"
            button_icon = QIcon(icons.START_ICON)
        else:
            ProfileTable.running_profiles.add(button.profile)
            button.profile.run()
            button_text = "Stop"
            button_icon = QIcon(icons.STOP_ICON)
            thread = Thread(target=self._profile_stopped, args=(button,))
            self.running_threads[button.profile.name] = {
                "thread": thread,
                "status": True,
            }
            thread.start()

        new_button = ProfileActiveButton(
            button_icon,
            button_text,
            button.profile,
            button.row,
            button.col,
            not button.is_running,
        )
        new_button.clicked.connect(self.change_running_status)
        self.setCellWidget(button.row, button.col, new_button)

    def _wait_thread(self, profile_name):
        thread = self.running_threads[profile_name]["thread"]
        self.running_threads[profile_name] = {"thread": "", "status": False}
        thread.join()

    def _profile_stopped(self, button: "ProfileActiveButton"):
        while self.running_threads[button.profile.name]["status"]:
            time.sleep(0.5)
            if button.profile.is_running():
                continue
            button.is_running = True
            threadutil.run_in_main_thread(self.change_running_status)(button)
            break

    def _set_name_column(self, row: int, col: int, profile: Profile) -> None:
        name_widget = QWidget(self)
        layout = QHBoxLayout(name_widget)

        checkbox = ProfileCheckBox(profile, row)
        checkbox.clicked.connect(self.checkbox_clicked)
        checkbox.setFixedHeight(20)

        content = QPushButton(QIcon(icons.PROFILE_ICON), profile.name)
        content.setIconSize(QSize(20, 20))
        content.setFixedHeight(20)

        layout.addWidget(checkbox)
        layout.addWidget(content)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        name_widget.setLayout(layout)

        self.setCellWidget(row, col, name_widget)


class ProfileActiveButton(QPushButton):
    def __init__(
        self,
        icon: QIcon,
        text: str,
        profile: Profile,
        row: int,
        col: int,
        is_running: bool,
        *args,
        **kwargs
    ):
        super().__init__(icon, text, *args, **kwargs)

        self.is_running = is_running
        self.profile = profile
        self.row = row
        self.col = col


class ProfileCheckBox(CheckBoxEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProfileStatusCombo(QComboBox):
    def __init__(self, items: Iterable[str], profile: Profile, row: int, col: int):
        super().__init__()

        self.addItems(items)
        self.profile = profile
        self.active_status = profile.status
        self.row = row
        self.col = col

        if self.active_status:
            self.setCurrentIndex(items.index(self.active_status))


class ProfileNotesButton(QPushButton):
    def __init__(self, icon: QIcon, text: str, profile: str, row: int, col: int):
        super().__init__(icon, text)

        self.text_ = text
        self.profile = profile
        self.row = row
        self.col = col

        self.setIconSize(QSize(10, 10))


class ProfileProxyCombo(QComboBox):
    def __init__(
        self,
        items: Iterable[str],
        active_proxy: str,
        proxy_id: int,
        profile: str,
        row: int,
        col: int,
    ):
        super().__init__()

        self.addItems(items)
        self.items = items
        self.profile = profile
        self.active_proxy = active_proxy
        self.proxy_id = proxy_id
        self.row = row
        self.col = col

        if active_proxy:
            self.setCurrentIndex(self.proxy_id)


class ProxyTable(Table):
    COLUMN_NAMES = [
        "",
        "Country",
        "Address",
        "Port",
        "Username",
        "Password",
        "Valid",
        "Profiles count",
    ]

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setColumnCount(len(self.COLUMN_NAMES))
        self.setHorizontalHeaderLabels(self.COLUMN_NAMES)
        self.setColumnWidth(0, 5)
        self.update()

    def set_items(self, data: Iterable[Iterable]):
        for i, proxy in enumerate(data):
            checkbox = ProxyCheckBox(proxy[7], i)
            checkbox.clicked.connect(self.checkbox_clicked)
            self.setCellWidget(i, 0, checkbox)
            self.setItem(i, 1, TableItem(proxy[0]))
            self.setItem(i, 2, TableItem(proxy[1]))
            self.setItem(i, 3, TableItem(proxy[2]))
            self.setItem(i, 4, TableItem(proxy[3]))
            self.setItem(i, 5, TableItem(proxy[4]))
            self.setItem(i, 6, TableItem(proxy[5]))
            self.setItem(i, 7, TableItem(proxy[6]))

    def update(self):
        proxies = []
        for proxy_model in Proxy.all_models():
            username, password, address, port = Proxy.split_server(proxy_model.server)
            proxies.append(
                (
                    proxy_model.country,
                    address,
                    port,
                    username,
                    password,
                    proxy_model.is_valid,
                    str(
                        len(
                            [
                                profile
                                for profile in Profile.all()
                                if profile.proxy_server == proxy_model.server
                            ]
                        )
                    ),
                    Proxy(proxy_model.server),
                )
            )
        self.setRowCount(len(proxies))
        self.set_items(proxies)


class ProxyCheckBox(CheckBoxEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Web3AccountsTable(Table):
    COLUMN_NAMES = ["", "Name", "Address"]

    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def update(self): ...
