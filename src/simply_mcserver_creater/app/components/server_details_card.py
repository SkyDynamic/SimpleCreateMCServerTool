import logging

import requests
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QFileDialog
from qfluentwidgets import VBoxLayout, PushButton, ScrollArea, setTheme, setThemeColor, Theme

from ...utils.config import config
from ...utils.style_sheet import StyleSheet

from typing import Union

log = logging.getLogger(__name__)


class DownloadCoreThread(QThread):
    updateButtonSignal = pyqtSignal(bool)

    def __init__(self, parent: Union['VanillaPage', 'FabricPage'], url: str, path: str, file_name: str, server_core_url: str = None) -> None:
        super().__init__(parent)
        self.server_core_url = server_core_url
        self.url = url
        self.path = path
        self.file_name = file_name

    def run(self) -> None:
        log.info("正在下载服务端...")
        try:
            if not self.server_core_url:
                info = requests.get(self.url)
                server_core_url = info.json().get("downloads").get("server").get("url")
            else:
                server_core_url = self.server_core_url
            core = requests.get(server_core_url, stream=True)
            with open(self.path + f"/{self.file_name}", 'wb') as f:
                for chunk in core.iter_content(chunk_size=512):
                    f.write(chunk)
        except Exception as e:
            log.error(str(e))

        log.info("下载完成")

        self.updateButtonSignal.emit(True)


class ServerDetailsWindows(ScrollArea):
    cancelSignal = pyqtSignal()

    data: dict

    def __init__(self, parent: Union['VanillaPage', 'FabricPage']) -> None:
        super().__init__()

        self.parent = parent

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
        self.downloadButton.setEnabled(False)
        path = QFileDialog.getExistingDirectory(self, "Choose saved directory", ".")
        url = self.data.get("url")
        server_core_url = self.data.get("server_core_url") if self.data.get("server_core_url") else None
        download_thread = DownloadCoreThread(self.parent, url, path, "server - " + self.data.get("id") + ".jar", server_core_url)
        download_thread.updateButtonSignal.connect(self.__update_downloadButton_signalReceive)
        download_thread.start()

    def __update_downloadButton_signalReceive(self, status):
        self.downloadButton.setEnabled(status)

    ...
