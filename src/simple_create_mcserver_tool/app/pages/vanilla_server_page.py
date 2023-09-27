import logging
import time

import requests

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy, QHeaderView, QAbstractItemView, QFrame, QTableWidgetItem
from qfluentwidgets import ScrollArea, PushButton, FluentIcon, setTheme, setThemeColor, Theme, TableWidget, StateToolTip, SwitchSettingCard

from ..components.server_details_card import ServerDetailsWindows
from ...utils.style_sheet import StyleSheet
from ...utils.config import config
from ...utils.manager import VanillaServerManager
from ...utils.custom_icon import CustomFluentIcon
from ...utils.time_format import format_time

log = logging.getLogger(__name__)
server_data = None


class UpdateThread(QThread):
    server_data = pyqtSignal()
    stateTooltipSignal = pyqtSignal(str, str, bool)
    updateButtonSignal = pyqtSignal(bool)

    def __init__(self, parent: 'VanillaPage' = None, api_url: str = None) -> None:
        super().__init__(parent)
        self.api_url = api_url

    def emit_error(self) -> None:
        log.error("得到预期之外的回应")
        self.stateTooltipSignal.emit(self.tr("Data update failed!"), "", False)
        self.updateButtonSignal.emit(True)

    def run(self) -> None:
        log.info("正在更新数据...")
        self.stateTooltipSignal.emit(self.tr("Updating manifest..."),
                                     self.tr("It may take some time, please be patient and wait"), True)
        try:
            response = requests.get("https://piston-meta.mojang.com/mc/game/version_manifest.json")
            if response.status_code == 200:
                manager = VanillaServerManager()
                data = response.json()
                data = data.get("versions")
                release_list = []
                snapshot_list = []
                for server_data_ in data:
                    server_type = server_data_.get("type")
                    if server_type == "release":
                        release_list.append(server_data_)
                    if server_type == "snapshot":
                        snapshot_list.append(server_data_)

                manager.save_to_file(data=data, server_type="All")
                manager.save_to_file(data=release_list)
                manager.save_to_file(data=snapshot_list, server_type="Snapshot")

                self.updateButtonSignal.emit(True)
                self.server_data.emit()
                self.stateTooltipSignal.emit(self.tr("Data update completed!"), "", False)
            else:
                self.emit_error()
        except Exception as e:
            log.error(e)
            self.emit_error()


class VanillaPage(ScrollArea):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("vanilla_server_page")

        self.server_data = None

        self.vBoxLayout = QVBoxLayout(self)

        self.update_button = PushButton(self.tr("Update Manifest"), self, FluentIcon.SYNC)
        self.update_button.clicked.connect(self.__on_update_button_clicked)
        self.download_button = PushButton(self.tr("Download"), self, CustomFluentIcon.BOOK_OPEN)
        self.download_button.clicked.connect(self.__on_download_button_clicked)
        self.download_window = ServerDetailsWindows(self)
        self.snapshot_switch = SwitchSettingCard(FluentIcon.CAMERA, "Show Snapshot", "")
        self.snapshot_switch.setFixedSize(QSize(250, 36))
        self.snapshot_switch.checkedChanged.connect(self.__on_snapshot_switch)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setContentsMargins(8, 8, 8, 8)
        self.buttonLayout.addWidget(self.update_button)
        self.buttonLayout.addWidget(self.download_button)
        self.buttonLayout.addWidget(self.snapshot_switch)

        self.vBoxLayout.addLayout(self.buttonLayout)

        self.vBoxLayout.setContentsMargins(16, 32, 16, 16)

        self.tableFrame = TableFrame(self)
        self.vBoxLayout.addWidget(self.tableFrame)

        self.snapshot_switch.switchButton.setChecked(config.show_snapshot)
        self.fill_table()

        StyleSheet.DOWNLOAD_SERVER_PAGE.apply(self)

        setTheme(Theme.DARK if config.dark_mode else Theme.LIGHT)
        setThemeColor(config.theme_color)

    def __on_snapshot_switch(self):
        config.show_snapshot = self.snapshot_switch.isChecked()
        config.save()
        self.fill_table()

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
        self.download_window.push_data(data)
        self.download_window.setWindowTitle("Server Version: %s" % data.get("id"))
        self.download_window.server_version_text.setText((self.tr("Server Version: %s" % data.get("id"))))
        self.download_window.server_type_text.setText(self.tr("Server Type: %s" % data.get("type").title()))
        release_time_uxin = format_time(data.get('releaseTime'))
        self.download_window.server_release_time_text.setText(self.tr(f"Server Release Time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(release_time_uxin))))
        self.download_window.show()

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
        manager = VanillaServerManager()
        snapshot = self.snapshot_switch.isChecked()
        if snapshot:
            server_data = manager.load_from_file("All")
        else:
            server_data = manager.load_from_file("Release")
        if server_data:
            self.tableFrame.table.setRowCount(len(server_data))
            for i, data in enumerate(server_data):
                self.tableFrame.table.setItem(i, 0, QTableWidgetItem(data.get("id")))
                self.tableFrame.table.setItem(i, 1, QTableWidgetItem(data.get("type").title()))


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
