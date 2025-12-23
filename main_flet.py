"""
Main entry point for Flet-based Alarmify
Beautiful modern UI with Material Design
"""

import flet as ft
import sys
from pathlib import Path
import logging
from logging_config import setup_logging

# Import Flet GUI
from gui_flet import main

if __name__ == "__main__":
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Alarmify (Flet UI)")
    
    # Run Flet app
    ft.app(
        target=main,
        view=ft.AppView.FLET_APP,  # Native window
        assets_dir="assets",
    )

