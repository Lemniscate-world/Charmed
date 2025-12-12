from PyQt5 import QtWidgets
from gui import AlarmApp
from logging_config import setup_logging, get_logger
import sys

logger = get_logger(__name__)

def main():
    setup_logging()
    logger.info('Starting Alarmify application')
    
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
