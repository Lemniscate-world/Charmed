from PyQt5 import QtWidgets
from gui import AlarmApp, CrashReportDialog
from logging_config import setup_logging, get_logger
import sys
import logging
import traceback


def exception_hook(exc_type, exc_value, exc_traceback):
    """
    Global exception handler for uncaught exceptions.
    
    Shows crash report dialog and logs the error before the application exits.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger = logging.getLogger(__name__)
    logger.critical(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    app = QtWidgets.QApplication.instance()
    if app:
        dialog = CrashReportDialog(exc_type, exc_value, exc_traceback)
        dialog.exec_()
    
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


logger = get_logger(__name__)

def main():
    setup_logging()
    logger.info('Starting Alarmify application')
    
    sys.excepthook = exception_hook
    
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        window = AlarmApp()
        window.show()
        logger.info('Main window displayed')
        sys.exit(app.exec_())
    except Exception as e:
        logger.exception('Fatal error in main application')
        raise


if __name__ == '__main__':
    main()
