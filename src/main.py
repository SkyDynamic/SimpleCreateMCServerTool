import sys

from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtWidgets import QApplication

from simple_create_mcserver_tool.utils.logger import ColoredLogger, patch_getLogger
from simple_create_mcserver_tool.utils.config import config

log = ColoredLogger('LittlePaimon', level=config.log_level)

def main():
    patch_getLogger(log)
    log.set_file('logs/latest.log')

    from simple_create_mcserver_tool.app.main_window import MainWindow
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.font().families().append("Microsoft YaHei UI")
    
    trans = QTranslator()
    trans.load("source", f"./resources/i18n/{config.language}")
    app.installTranslator(trans)

    main_app = MainWindow()
    main_app.show()

    app.exec_()


if __name__ == '__main__':
    sys.exit(main())
