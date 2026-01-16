import os
import logging
import sys
from pathlib import Path

# Import PyQt5 for GUI
from PyQt5 import QtWidgets

# Import existing backend
from logging_config import setup_logging, get_logger
from gui import AlarmApp, CrashReportDialog
from gui_setup_wizard import SetupWizard

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Qt GUI support
def exception_hook(exc_type, exc_value, exc_traceback):
    """
    Global exception handler for uncaught exceptions.

    Shows crash report dialog and logs the error before the application exits.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

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


def is_first_run():
    """
    Check if this is the first time running Alarmify.
    
    Returns:
        bool: True if first run, False otherwise
    """
    # Check if .env file exists and has credentials
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        return True
    
    # Check if credentials are set
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv('SPOTIPY_CLIENT_ID')
    client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        return True
    
    return False


def main():
    setup_logging()
    logger.info('Starting Alarmify application')
    
    sys.excepthook = exception_hook
    
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        # Check if first run and show wizard
        if is_first_run():
            logger.info('First run detected - showing setup wizard')
            from gui_setup_wizard import SetupWizard
            wizard = SetupWizard()
            if wizard.exec_() == QtWidgets.QDialog.Accepted:
                logger.info('Setup wizard completed successfully')
            else:
                logger.info('Setup wizard cancelled')
                # Still show main window, user can configure later
                pass
        
        window = AlarmApp()
        window.show()
        logger.info('Main window displayed')
        sys.exit(app.exec_())
    except Exception as e:
        logger.exception('Fatal error in main application')
        raise


if __name__ == '__main__':
    main()
