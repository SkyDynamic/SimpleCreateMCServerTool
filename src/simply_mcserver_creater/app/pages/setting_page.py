import re

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel, QWidget
from qfluentwidgets import FluentIcon, InfoBar, setTheme, setThemeColor, Theme, SettingCardGroup, \
    SwitchSettingCard, ExpandLayout, ScrollArea, HyperlinkCard

from ..components.combo_box_setting_card import ComboBoxSettingCard
from ..components.language_setting_card import LanguageSettingCard
from ..components.save_setting_card import PrimaryPushSettingCard
from ..components.theme_color_setting_card import ThemeColorSettingCard
from ...utils.config import config
from ...utils.style_sheet import StyleSheet


class SettingsPage(ScrollArea):
    stateTooltipSignal = pyqtSignal(str, str, bool)
    downloadedUpdateSignal = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("setting_page")

        self.stateTooltip = None

        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.settingLabel = QLabel(self.tr("Settings"), self)
        self.personalGroup = SettingCardGroup(self.tr("Personalization"), self.scrollWidget)
        # self.sererType = ComboBoxSettingCard(
        #    config.server_type,
        #    ["Release", "Snapshot"],
        #    FluentIcon.FLAG,
        #    self.tr("Server Type"),
        #    self.tr("Set the type what would want to get server core."),
        #    parent=self.personalGroup
        # )
        self.themeCard = SwitchSettingCard(
            FluentIcon.BRUSH,
            self.tr("Dark Theme"),
            self.tr("When opening, the interface will change to dark mode."),
            parent=self.personalGroup
        )
        self.themeCard.switchButton.setChecked(config.dark_mode)
        self.themeColorCard = ThemeColorSettingCard(
            "#009faa",
            config.theme_color,
            FluentIcon.PALETTE,
            self.tr("Theme Color"),
            parent=self.personalGroup
        )
        self.languageCard = LanguageSettingCard(
            config.language,
            FluentIcon.LANGUAGE,
            self.tr("Language"),
            self.tr("Select the software display language, which will take effect after restarting."),
            parent=self.personalGroup
        )
        self.otherGroup = SettingCardGroup(self.tr("Other"), self.scrollWidget)
        self.logLevelCard = ComboBoxSettingCard(
            config.log_level,
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            FluentIcon.BOOK_SHELF,
            self.tr("Log Level"),
            self.tr("Set the log level of the software. The higher the level, the more logs will be output, which will take effect after restarting."),
            parent=self.otherGroup
        )
        self.aboutGroup = SettingCardGroup(self.tr("About"), self.scrollWidget)
        self.githubCard = HyperlinkCard(
            "https://github.com/SkyDynamic/SimpleMCServerCreater",
            self.tr("GitHub Repository"),
            FluentIcon.GITHUB,
            self.tr("Open the Project GitHub Repository"),
            "",
            self.aboutGroup
        )

        self.saveCard = PrimaryPushSettingCard(
            self.tr("Save Settings"),
            FluentIcon.SAVE,
            self.tr("Save the current settings"),
            parent=self.scrollWidget
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTINGS_PAGE.apply(self)

        self.saveCard.clicked.connect(self.save_config)

        # initialize layout
        self.__initLayout()

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        # self.personalGroup.addSettingCard(self.sererType)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.otherGroup.addSettingCard(self.logLevelCard)

        self.aboutGroup.addSettingCard(self.githubCard)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.otherGroup)
        self.expandLayout.addWidget(self.aboutGroup)
        self.expandLayout.addWidget(self.saveCard)

    def save_config(self):
        config.dark_mode = self.themeCard.switchButton.isChecked()
        config.theme_color = self.themeColorCard.customColorLineEdit.text() if \
            self.themeColorCard.customRadioButton.isChecked() else \
            "#009faa"
        language_text = self.languageCard.comboBox.currentText()
        match = re.match(r".*\((.*)\)", language_text)
        if match:
            config.language = match.group(1)
        else:
            config.language = language_text
        config.log_level = self.logLevelCard.comboBox.text()
        config.save()
        setTheme(Theme.DARK if config.dark_mode else Theme.LIGHT)
        setThemeColor(config.theme_color)

        InfoBar.success("", self.tr("Configuration file saved successfully!"), parent=self, duration=2000)
