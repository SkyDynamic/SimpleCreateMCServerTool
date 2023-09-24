import logging

import requests

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy, QHeaderView, QAbstractItemView, QFrame, QTableWidgetItem
from qfluentwidgets import ScrollArea, PushButton, FluentIcon, setTheme, setThemeColor, Theme, TableWidget, StateToolTip

from ..components.server_details_card import ServerDetailsWindows
from ...utils.style_sheet import StyleSheet
from ...utils.config import config
from ...utils.manager import FabricServerManager
from ...utils.custom_icon import CustomFluentIcon

log = logging.getLogger(__name__)
server_data = None


class UpdateThread(QThread):
    server_data = pyqtSignal()
    stateTooltipSignal = pyqtSignal(str, str, bool)
    updateButtonSignal = pyqtSignal(bool)

    def __init__(self, parent: 'FabricPage' = None, api_url: str = None) -> None:
        super().__init__(parent)
        self.api_url = api_url

    def run(self) -> None:
        log.info("正在更新数据...")
        self.stateTooltipSignal.emit(self.tr("Updating manifest..."),
                                     self.tr("It may take some time, please be patient and wait"), True)
        response = requests.get("https://meta.fabricmc.net/v2/versions/game")
        manager = FabricServerManager()
        if response.status_code == 200:
            data = response.json()
            release_list = []
            snapshot_list = []
            for server_data_ in data:
                if server_data_.get("stable"):
                    release_list.append(server_data_)
                else:
                    snapshot_list.append(server_data_)

            manager.save_to_file(data=data, server_type="All")
            manager.save_to_file(data=release_list)
            manager.save_to_file(data=snapshot_list, server_type="Snapshot")

        loader_response = requests.get("https://meta.fabricmc.net/v2/versions/loader")
        if loader_response.status_code == 200:
            manager.save_loader_or_installer(loader_response.json(), "loader")

        installer_response = requests.get("https://meta.fabricmc.net/v2/versions/installer")
        if installer_response.status_code == 200:
            manager.save_loader_or_installer(installer_response.json(), "installer")

            self.updateButtonSignal.emit(True)
            self.server_data.emit()
            self.stateTooltipSignal.emit(self.tr("Data update completed!"), "", False)
        else:
            log.error("得到预期之外的回应")
            self.stateTooltipSignal.emit(self.tr("Data update failed!"), "", False)
            self.updateButtonSignal.emit(True)


class FabricPage(ScrollArea):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("fabric_server_page")

        self.server_data = None

        self.vBoxLayout = QVBoxLayout(self)

        self.update_button = PushButton(self.tr("Update Manifest"), self, FluentIcon.SYNC)
        self.update_button.clicked.connect(self.__on_update_button_clicked)
        self.download_button = PushButton(self.tr("Download"), self, CustomFluentIcon.BOOK_OPEN)
        self.download_button.clicked.connect(self.__on_download_button_clicked)
        self.download_window = ServerDetailsWindows()
        self.fabric_setting_button = PushButton(self.tr("Fabric Setting"), self, FluentIcon.SETTING)
        self.fabric_setting_button.clicked.connect(self.__on_fabric_setting_button_clicked)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setContentsMargins(8, 8, 8, 8)
        self.buttonLayout.addWidget(self.update_button)
        self.buttonLayout.addWidget(self.download_button)
        self.buttonLayout.addWidget(self.fabric_setting_button)

        self.vBoxLayout.addLayout(self.buttonLayout)

        self.vBoxLayout.setContentsMargins(16, 32, 16, 16)

        self.tableFrame = TableFrame(self)
        self.vBoxLayout.addWidget(self.tableFrame)

        self.fill_table()

        StyleSheet.DOWNLOAD_SERVER_PAGE.apply(self)

        setTheme(Theme.DARK if config.dark_mode else Theme.LIGHT)
        setThemeColor(config.theme_color)

    def __on_update_button_clicked(self):
        self.update_button.setEnabled(False)
        update_thread = UpdateThread(self)
        update_thread.server_data.connect(self.fill_table)
        update_thread.stateTooltipSignal.connect(self.__update_data_stateTooltip_signalReceive)
        update_thread.updateButtonSignal.connect(self.__update_data_updateButton_signalReceive)
        update_thread.start()

    def __on_download_button_clicked(self):
        if self.tableFrame.table.currentRow() == -1:
            return
        data = server_data[self.tableFrame.table.currentRow()]
        self.details_window.setWindowTitle(f"Server Version: {data.get('id')}")
        self.details_window.push_data(data)
        self.details_window.show()

    def __on_fabric_setting_button_clicked(self):
        ...

    def __update_data_stateTooltip_signalReceive(self, title, content, status):
        if status:
            self.stateTooltip = StateToolTip(title, content, self.window())
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
        else:
            self.stateTooltip.setContent(title)
            self.stateTooltip.setState(True)
            self.stateTooltip = None

    def __update_data_updateButton_signalReceive(self, status):
        self.update_button.setEnabled(status)

    def fill_table(self):
        global server_data
        manager = FabricServerManager()
        server_data = manager.load_from_file("All")
        if server_data:
            self.tableFrame.table.setRowCount(len(server_data))
            for i, data in enumerate(server_data):
                self.tableFrame.table.setItem(i, 0, QTableWidgetItem(data.get("version")))
                self.tableFrame.table.setItem(i, 1, QTableWidgetItem("Release" if data.get("stable") else "Snapshot"))
                i += 1


class TableFrame(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 8, 0, 0)

        # 表格部分
        self.table = TableWidget(self)
        self.table.verticalHeader().hide()
        self.table.setColumnCount(2)
        self.table.setRowCount(0)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setHorizontalHeaderLabels([
            self.tr("Server Version"),
            self.tr("Server Type")
        ])

        self.table.setColumnWidth(0, 250)
        self.table.setColumnWidth(1, 100)

        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.vBoxLayout.addWidget(self.table, Qt.AlignLeft)
