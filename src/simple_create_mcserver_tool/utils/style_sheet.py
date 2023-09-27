from enum import Enum

from qfluentwidgets import Theme, StyleSheetBase, qconfig


class StyleSheet(StyleSheetBase, Enum):
    MAIN_WINDOW = "main_window"
    DOWNLOAD_SERVER_PAGE = "download_server_page"
    SETTINGS_PAGE = "settings_page"
    SERVER_DETAILS_PAGE = "server_details_page"

    def path(self, theme: Theme = Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f"resources/qss/{theme.value.lower()}/{self.value}.qss"
