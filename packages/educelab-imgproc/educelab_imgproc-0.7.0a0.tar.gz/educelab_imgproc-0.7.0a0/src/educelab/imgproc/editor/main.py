import logging
import sys


def has_pyside() -> bool:
    try:
        import PySide6.QtCore
    except ImportError:
        return False
    return True


def main():
    if not has_pyside():
        print('PySide6 is not installed. Cannot launch ImgProc editor.',
              file=sys.stderr)
        sys.exit(1)

    from PySide6.QtCore import QCoreApplication
    from PySide6.QtWidgets import QApplication
    from educelab.imgproc.editor.util import setup_logging
    from educelab.imgproc.editor.main_window import MainWindow

    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName('EduceLab')
    QCoreApplication.setApplicationName('ImgProc')
    QCoreApplication.setApplicationVersion('1.0.0')

    setup_logging(log_level=logging.DEBUG)
    logger = logging.getLogger('ImgProc')
    logger.info(
        f'Launching {QCoreApplication.organizationName()} '
        f'{QCoreApplication.applicationName()} '
        f'v{QCoreApplication.applicationVersion()}')

    # app_icon = QIcon(app_icon_path())
    # app.setWindowIcon(app_icon)

    main_window = MainWindow()
    main_window.setWindowTitle('ImgProc')
    # main_window.setWindowIcon(app_icon)
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
