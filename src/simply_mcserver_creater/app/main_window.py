from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSettings, QVariant, QSize, QPoint
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QStackedWidget
from qfluentwidgets import NavigationInterface, qrouter, FluentIcon
from qframelesswindow import FramelessWindow, StandardTitleBar

from .pages.fabric_server_page import FabricPage
from .pages.vanilla_server_page import VanillaPage
from .pages.setting_page import SettingsPage
from ..utils.style_sheet import StyleSheet
from ..constant import VERSION


class MainWindow(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = StandardTitleBar(self)
        self.title.titleLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                font: 13px 'Microsoft YaHei';
                padding: 0 4px
            }
        """)
        self.setTitleBar(self.title)
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(
            self, showMenuButton=True, showReturnButton=True)
        self.stackWidget = QStackedWidget(self)

        self.vanilla_interface = VanillaPage(self)
        self.fabric_interface = FabricPage(self)
        self.settings_interface = SettingsPage(self)

        self.stackWidget.addWidget(self.vanilla_interface)
        self.stackWidget.addWidget(self.fabric_interface)
        self.stackWidget.addWidget(self.settings_interface)

        self.initLayout()
        self.initNavigation()
        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

        self.titleBar.raise_()
        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)

    def initNavigation(self):
        self.navigationInterface.addItem(
            routeKey=self.vanilla_interface.objectName(),
            icon="./resources/icon.ico",
            text=self.tr("Vanilla Server"),
            onClick=lambda: self.switchTo(self.vanilla_interface)
        )

        self.navigationInterface.addItem(
            routeKey=self.fabric_interface.objectName(),
            icon="./resources/icons/fabric.png",
            text=self.tr("Fabric Server"),
            onClick=lambda: self.switchTo(self.fabric_interface)
        )

        self.navigationInterface.addItem(
            routeKey=self.settings_interface.objectName(),
            icon=FluentIcon.SETTING,
            text=self.tr("Settings"),
            onClick=lambda: self.switchTo(self.settings_interface),
            #position=NavigationItemPosition.BOTTOM
        )

        qrouter.setDefaultRouteKey(self.stackWidget, self.vanilla_interface.objectName())
        self.navigationInterface.setCurrentItem(self.vanilla_interface.objectName())

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(0)

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def initWindow(self):
        self.readSettings()
        self.setWindowIcon(QIcon('resources/icon.ico'))
        self.setWindowTitle(self.tr("Simple MC Server Creater v%s") % VERSION)
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        StyleSheet.MAIN_WINDOW.apply(self)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        super().closeEvent(event)
        self.saveSettings()

    def readSettings(self):
        settings = QSettings("SkyDynamic", "SimpleMCServerCreater")
        size = settings.value("size", QVariant(QSize(900, 700)))
        pos = settings.value("pos", QVariant(QPoint(200, 200)))
        self.resize(size)
        self.move(pos)

    def saveSettings(self):
        settings = QSettings("SkyDynamic", "SimpleMCServerCreater")
        settings.setValue("size", QVariant(self.size()))
        settings.setValue("pos", QVariant(self.pos()))
