import pytest
from cvbot.communication.txtapiclient import TxtApiClient
from cvbot.controller.easy_drive_controller import EasyDriveController
from cvbot.config.drive_robot_configuration import DriveRobotConfiguration
import os
import numpy as np
from ..conftest import session
from ..communication.test_txtapiclient import api_client
import asyncio
import pytest_asyncio


@pytest_asyncio.fixture(scope="session")
async def drive_controller(api_client: TxtApiClient) -> EasyDriveController:
    """Create a EasyDriveController instance."""
    await api_client.initialize()
    return EasyDriveController(api_client, DriveRobotConfiguration())


@pytest.mark.asyncio
async def test_camera(drive_controller: EasyDriveController):
    """Test the discovery of the TxtApiClient."""
    iter_ = drive_controller.camera()
    frame1 = await anext(iter_)
    assert frame1 is not None
    assert frame1.shape == (3, 480, 640)
    assert frame1.dtype == np.float32
    assert frame1.min() >= 0.0
    assert frame1.max() <= 1.0
    await asyncio.sleep(2)
    frame2 = await anext(iter_)
    assert frame2 is not None
    assert frame2.shape == (3, 480, 640)
    assert frame2.dtype == np.float32
    assert frame2.min() >= 0.0
    assert frame2.max() <= 1.0
    return True


@pytest.mark.asyncio
async def test_forward_drive(drive_controller: EasyDriveController):
    """Test the discovery of the TxtApiClient."""
    await drive_controller.straight(3)
    await asyncio.sleep(2)
    await drive_controller.straight(-3)
    await asyncio.sleep(2)
    await drive_controller.stop()
    return True


@pytest.mark.asyncio
async def test_side_drive(drive_controller: EasyDriveController):
    """Test the discovery of the TxtApiClient."""
    await drive_controller.side(3)
    await asyncio.sleep(2)
    await drive_controller.side(-3)
    await asyncio.sleep(2)
    await drive_controller.stop()
    return True


@pytest.mark.asyncio
async def test_diagonal_drive(drive_controller: EasyDriveController):
    """Test the discovery of the TxtApiClient."""
    await drive_controller.diagonal(3, 2)
    await asyncio.sleep(2)
    await drive_controller.diagonal(-3, -2)
    await asyncio.sleep(2)
    await drive_controller.diagonal(3, -3)
    await asyncio.sleep(2)
    await drive_controller.diagonal(-3, 3)
    await asyncio.sleep(2)
    await drive_controller.stop()
    return True


@pytest.mark.asyncio
async def test_rotate_drive(drive_controller: EasyDriveController):
    """Test the discovery of the TxtApiClient."""
    await drive_controller.rotate(20)
    await asyncio.sleep(2)
    await drive_controller.rotate(-20)
    await asyncio.sleep(2)
    await drive_controller.stop()
    return True
