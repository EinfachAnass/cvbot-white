import sys

from cvbot.config.drive_robot_configuration import DriveRobotConfiguration
from cvbot.controller.easy_drive_controller import EasyDriveController
from cvbot.communication.txtapiclient import TxtApiClient
import os

from PySide6.QtWidgets import (QApplication)
from cvtools.logger.logging import logger, basic_config
import PySide6.QtAsyncio as QtAsyncio
from dotenv import load_dotenv

from cvbot.ui.drive_control_app import DriveControlApp


if __name__ == '__main__':
    basic_config()
    loaded = load_dotenv()
    if not loaded:
        logger.warning("No .env file found.")

    app = QApplication(sys.argv)

    # Erstelle eine Dummy-Konfiguration und einen Dummy-Controller für die GUI
    config = DriveRobotConfiguration()

    host = os.getenv("TXT_API_HOST", "localhost")
    port = int(os.getenv("TXT_API_PORT", 8080))
    key = os.getenv("TXT_API_KEY", None)
    client = TxtApiClient(host, port, key)

    # Erstelle den DriveController mit der Konfiguration und dem Controller
    drive_controller = EasyDriveController(client, config)

    # Starte die PyQt5-Anwendung
    main = DriveControlApp(drive_controller)
    main.show()
    QtAsyncio.run(handle_sigint=True)
