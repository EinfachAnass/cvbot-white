import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from dotenv import load_dotenv
import asyncio
import numpy as np


from cvbot.communication.txtapiclient import TxtApiClient
from cvbot.config.drive_robot_configuration import DriveRobotConfiguration
from cvbot.controller.easy_drive_controller import EasyDriveController
from cvbot import controller


async def main() -> None:
    # Load environment variables
    load_dotenv(os.path.join(os.path.dirname(__file__), 'PathandEnv.env'))
    
    # Get configuration from environment variables
    host = os.getenv('TXT_API_HOST')
    port = int(os.getenv('TXT_API_PORT', '80'))
    key = os.getenv('TXT_API_KEY')

    client = TxtApiClient(host, port, key)
    await client.initialize()
    drive_controller = EasyDriveController(client, DriveRobotConfiguration())

    await drive_controller.drive(np.array([0.0, 500.0, 1000.0]))
    frame = await anext(controller.camera())
    await asyncio.sleep(5)
    await drive_controller.stop()


if __name__ == "__main__":
    asyncio.run(main())