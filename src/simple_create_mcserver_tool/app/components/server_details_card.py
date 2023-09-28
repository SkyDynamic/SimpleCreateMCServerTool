import logging

import requests
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QFileDialog, QLabel, QWidget, QProgressBar, QMessageBox
from qfluentwidgets import VBoxLayout, PushButton, setTheme, setThemeColor, Theme

from ...utils.config import config
from ...utils.style_sheet import StyleSheet

from typing import Union

log = logging.getLogger(__name__)


class DownloadCoreThread(QThread):
    updateButtonSignal = pyqtSignal(bool)
    download_process_signal = pyqtSignal(int)

    def __init__(self, parent: Union['VanillaPage', 'FabricPage'], url: str, path: str, file_name: str, server_core_url: str = None) -> None:
        super().__init__(parent)
        self.file_size = None
        self.server_core_url = server_core_url
        self.url = url
        self.path = path
        self.file_name = file_name

    def run(self) -> None:
        log.info("正在下载服务端...")
        try:
            if not self.server_core_url:
                info = requests.get(self.url)
                self.file_size = info.json().get("downloads").get("server").get("size")
                server_core_url = info.json().get("downloads").get("server").get("url")
            else:
                server_core_url = self.server_core_url
                # 由于无法获取到正确的jar大小, 通过各个版本对比, 写成约152kb
                self.file_size = 155095

            core = requests.get(server_core_url, stream=True)
            offset = 0
            with open(self.path + f"/{self.file_name}", 'wb') as f:
                for chunk in core.iter_content(chunk_size=512):
                    f.write(chunk)
                    offset = offset + len(chunk)
                    process = offset / int(self.file_size) * 100
                    self.download_process_signal.emit(int(process))
                f.close()

        except Exception as e:
            log.error(str(e))

        log.info("下载完成")

        self.updateButtonSignal.emit(True)


class ServerDetailsWindows(QWidget):
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

        self.textGroup = QFrame(self)
        self.server_version_text = QLabel()
        self.server_type_text = QLabel()
        self.server_release_time_text = QLabel()

        self.progressBarGroup = QFrame(self)
        self.progressBar = QProgressBar(self, minimumWidth=400, textVisible=False)
        self.progressBar.setValue(0)

        self.textGroup.setObjectName("textGroup")
        self.progressBarGroup.setObjectName("progressBarGroup")
        self.progressBar.setObjectName("progressBar")
        self.server_type_text.setObjectName("ServerTypeText")
        self.server_release_time_text.setObjectName("ServerReleaseTimeText")
        self.server_version_text.setObjectName("ServerVersionText")

        setTheme(Theme.DARK if config.dark_mode else Theme.LIGHT)
        setThemeColor(config.theme_color)

        StyleSheet.SERVER_DETAILS_PAGE.apply(self)

        self.cancelButton.adjustSize()

        self.vBoxLayout = VBoxLayout(self)
        self.buttonLayout = QHBoxLayout(self.buttonGroup)
        self.textLayout = QVBoxLayout(self.textGroup)
        self.progressBarLayout = QVBoxLayout(self.progressBarGroup)

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.textGroup, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.progressBarGroup, 0)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignBottom)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        self.textLayout.setSpacing(0)
        self.textLayout.setContentsMargins(24, 24, 24, 24)
        self.textLayout.addWidget(self.server_version_text)
        self.textLayout.addWidget(self.server_type_text)
        self.textLayout.addWidget(self.server_release_time_text)
        self.progressBarLayout.addWidget(self.progressBar)

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
        self.progressBar.setValue(0)
        download_thread = DownloadCoreThread(self.parent, url, path, "server - " + self.data.get("id") + ".jar", server_core_url)
        download_thread.updateButtonSignal.connect(self.__update_downloadButton_signalReceive)
        download_thread.download_process_signal.connect(self.set_progressbar_value)
        download_thread.start()

    def __update_downloadButton_signalReceive(self, status):
        self.downloadButton.setEnabled(status)

    def set_progressbar_value(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            # QMessageBox.information(self, self.tr("Tips"), self.tr("Download Success !"))
            return

    ...
