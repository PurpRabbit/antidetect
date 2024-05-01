from PyQt6.QtWidgets import QWidget

from ui.settings import SIDEBAR_WIDTH, MANAGEBAR_HEIGHT
from ui.managebar import ProfileManageBar, ProxyManageBar, Web3AccountsManageBar
from ui.table import ProfileTable, ProxyTable, Web3AccountsTable
from ui import utils


class ContentView(QWidget):
    def __init__(self, parent: QWidget, table, manage_bar):
        super().__init__(parent)

        self.managebar_widget = QWidget(self)
        self.managebar = manage_bar(self.managebar_widget)
        self.table = table(self)
        self.table.update()

        self.setStyleSheet(utils.load_style_sheet("content.qss"))
        window_size = self.parent().size()
        self.setGeometry(
            SIDEBAR_WIDTH, 0, window_size.width() - SIDEBAR_WIDTH, window_size.height()
        )

    def setGeometry(self, x, y, w, h):
        super().setGeometry(x, y, w, h)
        self.managebar_widget.setGeometry(0, 0, w, MANAGEBAR_HEIGHT)
        self.table.setGeometry(0, MANAGEBAR_HEIGHT, w, h - MANAGEBAR_HEIGHT)


class ProfileContentView(ContentView):
    def __init__(self, parent: QWidget):
        super().__init__(parent, ProfileTable, ProfileManageBar)


class ProxyContentView(ContentView):
    def __init__(self, parent: QWidget):
        super().__init__(parent, ProxyTable, ProxyManageBar)


class Web3AccountsContentView(ContentView):
    def __init__(self, parent: QWidget):
        super().__init__(parent, Web3AccountsTable, Web3AccountsManageBar)
