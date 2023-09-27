from enum import Enum

from qfluentwidgets import getIconColor, Theme, FluentIconBase


class CustomFluentIcon(FluentIconBase, Enum):
    """ Custom icons """

    BOOK_OPEN = "BookOpen"
    RELEASE = "release"
    SNAPSHOT = "snapshot"

    def path(self, theme=Theme.AUTO):
        return f'./resources/icons/{self.value}_{getIconColor(theme)}.svg'