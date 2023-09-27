import logging

import requests

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy, QHeaderView, QAbstractItemView, QFrame, QTableWidgetItem
from qfluentwidgets import ScrollArea, PushButton, FluentIcon, setTheme, setThemeColor, Theme, TableWidget, StateToolTip, SwitchSettingCard

from ..components.combo_box_setting_card import ComboBoxSettingCard
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

    def emit_error(self) -> None:
        log.error("得到预期之外的回应")
        self.stateTooltipSignal.emit(self.tr("Data update failed!"), "", False)
        self.updateButtonSignal.emit(True)

    def run(self) -> None:
        log.info("正在更新数据...")
        self.stateTooltipSignal.emit(self.tr("Updating manifest..."),
                                     self.tr("It may take some time, please be patient and wait"), True)
        try:
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
            else:
                self.emit_error()

            loader_response = requests.get("https://meta.fabricmc.net/v2/versions/loader")
            if loader_response.status_code == 200:
                manager.save_loader_or_installer(loader_response.json(), "loader")
            else:
                self.emit_error()

            installer_response = requests.get("https://meta.fabricmc.net/v2/versions/installer")
            if installer_response.status_code == 200:
                manager.save_loader_or_installer(installer_response.json(), "installer")
            else:
                self.emit_error()
        except Exception as e:
            log.error(e)
            self.emit_error()

        self.updateButtonSignal.emit(True)
        self.stateTooltipSignal.emit(self.tr("Data update completed!"), "", False)
        self.server_data.emit()


class FabricPage(ScrollArea):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.installer_list = []
        self.loader_list = []
        self.setObjectName("fabric_server_page")

        self.server_data = None

        self.vBoxLayout = QVBoxLayout(self)

        self.load_loader_version_and_installer_version()

        try:
            loader_vaule = self.loader_list[0]
            installer_vaule = self.installer_list[0]
        except IndexError:
            loader_vaule = ""
            installer_vaule = ""
        self.loader_comboBox = ComboBoxSettingCard(
            loader_vaule,
            self.loader_list,
            FluentIcon.CLOUD_DOWNLOAD,
            "LoaderVersion"
        )
        self.loader_comboBox.setFixedSize(QSize(320, 50))
        self.installer_comboBox = ComboBoxSettingCard(
            installer_vaule,
            self.installer_list,
            FluentIcon.CLOUD_DOWNLOAD,
            "InstallerVersion"
        )
        self.installer_comboBox.setFixedSize(QSize(320, 50))

        self.fabricBoxLayout = QHBoxLayout()
        self.fabricBoxLayout.setContentsMargins(8, 8, 8, 8)
        self.fabricBoxLayout.addWidget(self.loader_comboBox)
        self.fabricBoxLayout.addWidget(self.installer_comboBox)

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
        self.vBoxLayout.addLayout(self.fabricBoxLayout)

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
        data = {
            "id": "fabric" + data.get("version"),
            "url": "https://fabricmc.net",
            "server_core_url": f"https://meta.fabricmc.net/v2/versions/loader/{data.get('version')}/{self.loader_comboBox.comboBox.text()}/{self.installer_comboBox.comboBox.text()}/server/jar",
            "type": "Release" if data.get("stable") else "Snapshot"
        }
        self.download_window.setWindowTitle(f"Server Version: {data.get('id')}")
        self.download_window.server_version_text.setText((self.tr("Server Version: %s" % data.get("id"))))
        self.download_window.server_type_text.setText(self.tr("Server Type: %s" % data.get("type").title()))
        self.download_window.push_data(data)
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

    def load_loader_version_and_installer_version(self):
        manager = FabricServerManager()
        self.installer_list, self.loader_list = manager.load_fabric_data()

    def fill_table(self):
        global server_data
        manager = FabricServerManager()
        snapshot = self.snapshot_switch.isChecked()
        if snapshot:
            server_data = manager.load_from_file("All")
        else:
            server_data = manager.load_from_file("Release")
        if server_data:
            self.tableFrame.table.setRowCount(len(server_data))
            for i, data in enumerate(server_data):
                self.tableFrame.table.setItem(i, 0, QTableWidgetItem(data.get("version")))
                self.tableFrame.table.setItem(i, 1, QTableWidgetItem("Release" if data.get("stable") else "Snapshot"))
        self.load_loader_version_and_installer_version()
        self.loader_comboBox.comboBox.clear()
        self.installer_comboBox.comboBox.clear()
        self.loader_comboBox.comboBox.addItems(self.loader_list)
        self.installer_comboBox.comboBox.addItems(self.installer_list)


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
