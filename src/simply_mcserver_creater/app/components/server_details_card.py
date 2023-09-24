from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout
from qfluentwidgets import VBoxLayout, PushButton, ScrollArea, setTheme, setThemeColor, Theme

from ...utils.config import config
from ...utils.style_sheet import StyleSheet


class ServerDetailsWindows(ScrollArea):
    cancelSignal = pyqtSignal()

    data: dict

    def __init__(self) -> None:
        super().__init__()

        self.setWindowIcon(QIcon('resources/icon.ico'))

        self.buttonGroup = QFrame(self)
        self.cancelButton = PushButton(self.tr("Cancel"), self.buttonGroup)
        self.cancelButton.clicked.connect(self.__cancel_button_clicked)
        self.downloadButton = PushButton(self.tr("Download"), self.buttonGroup)
        self.downloadButton.clicked.connect(self.__download_button_clicked)
        self.cancelButton.setAttribute(Qt.WA_LayoutUsesWidgetRect)

        self.buttonGroup.setObjectName('buttonGroup')
        self.cancelButton.setObjectName('cancelButton')

        setTheme(Theme.DARK if config.dark_mode else Theme.LIGHT)
        setThemeColor(config.theme_color)

        StyleSheet.SERVER_DETAILS_PAGE.apply(self)

        self.cancelButton.adjustSize()

        self.vBoxLayout = VBoxLayout(self)
        self.textLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout(self.buttonGroup)

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignBottom)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        self.buttonLayout.setSpacing(12)
        self.buttonLayout.setContentsMargins(24, 24, 24, 24)
        self.buttonLayout.addWidget(self.downloadButton, 1)
        self.buttonLayout.addWidget(self.cancelButton, 1, Qt.AlignVCenter)

        self.buttonGroup.setMinimumWidth(350)
        self.setFixedSize(200, 50)

    def push_data(self, data):
        self.data = data

    def __cancel_button_clicked(self):
        self.close()

    def __download_button_clicked(self):
        ...

    ...
