import asyncio
import matplotlib.pyplot as plt
import numpy as np

from cvbot.communication import controller
from cvbot.communication.txtapiclient import TxtApiClient
from cvbot.controller.easy_drive_controller import EasyDriveController
from cvbot.config.drive_robot_configuration import DriveRobotConfiguration

from dotenv import load_dotenv
import os

load_dotenv()  # loads .env from current dir

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
KEY = os.getenv("KEY")
# print(HOST, PORT, KEY)
# print(type(HOST), type(PORT), type(KEY))

async def connect(angle=0.0, distance=0.0):
    # The following classes are needed to init the drive controller
    api_client = TxtApiClient(HOST, PORT, KEY)
    controller = EasyDriveController(api_client, DriveRobotConfiguration())
    await api_client.initialize()
    
    await controller.stop()

    while (angle > 5 ):
        await controller.drive(speeds=np.array([0.0, 100.0, 0.0]))
        angle = angle - 1
        await asyncio.sleep(1.0)
    await controller.stop()

    while (distance > 5 ):
        await controller.drive(speeds=np.array([0.0, 0.0, -100.0]))
    await controller.stop()

    # first param turns front and rear in reverse
    # second param rotate positive -> left
    # third param forward (negative)
    # await asyncio.sleep(1.0)

asyncio.run(connect(10.0, 0.0))


