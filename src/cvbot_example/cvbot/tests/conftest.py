import asyncio
from datetime import datetime, date
import os
from typing import Tuple, Type
import re
import pytest
from dotenv import load_dotenv
from dataclasses import dataclass
import logging
import sys
from cvtools.util.package_tools import get_project_root_path
import pytest_asyncio

OUTPUT_DIR = "tests/output/"


def basic_config(level: int = logging.INFO):
    """Basic logging configuration with sysout logger.

    Parameters
    ----------
    level : logging._Level, optional
        The logging level to consider, by default logging.INFO
    """
    root = logging.getLogger()
    root.setLevel(level)
    _fmt = '%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    _date_fmt = '%Y-%m-%d:%H:%M:%S'
    logging.basicConfig(format=_fmt,
                        datefmt=_date_fmt,
                        level=level)
    fmt = logging.Formatter(_fmt, _date_fmt)
    root.handlers[0].setFormatter(fmt)
    # Set default for other loggers
    if "matplotlib" in sys.modules:
        logger = logging.getLogger("matplotlib")
        logger.setLevel(logging.WARNING)


def today_time_now() -> Tuple[str, str]:
    today = date.today()
    date_today = today.strftime("%Y_%m_%d")
    now = datetime.now()
    date_now = now.strftime("%Y_%m_%d_%H_%M_%S")
    return date_today, date_now


@pytest.mark.asyncio
@pytest_asyncio.fixture(scope='session')
async def session():
    """Fixture for aiohttp ClientSession."""
    from aiohttp import ClientSession
    session = ClientSession()
    yield session
    session.close()


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(autouse=True, scope='session')
def session_encapsule():
    setup_session()
    yield
    teardown_session()


def get_output_dir() -> str:
    """Returns the output dir for this test run."""
    dir = OUTPUT_DIR
    if not os.path.exists(dir):
        os.makedirs(dir, exist_ok=True)
    return dir


def setup_session():
    # Change to project root
    os.chdir(get_project_root_path())
    basic_config()
    # load dotenv
    env_path = os.path.join(os.path.dirname(__file__), "..", "pytest.env")
    if not os.path.exists(env_path):
        logging.warning(f"Could not find pytest.env at {env_path}.")
    else:
        load_dotenv(os.path.join(os.path.dirname(__file__),
                    "..", "pytest.env"), override=True)
    # Setup output dir for test session
    global OUTPUT_DIR
    _date, _time = today_time_now()
    OUTPUT_DIR = os.path.join(OUTPUT_DIR, _date, _time)
    pass


def teardown_session():
    pass


def get_test_name() -> str:
    return os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]


def get_test_name_for_path(allow_dot: bool = True) -> str:
    return re.sub(f'[^\w_{"." if allow_dot else ""} -]', '_', get_test_name())


def pytest_make_parametrize_id(config, val, argname):
    if isinstance(val, int):
        return f'{argname}={val}'
    if isinstance(val, str):
        return f'{argname}=\'{val}\''
    if isinstance(val, tuple):
        vals = [str(x) for x in val]
        return f'{argname}=({",".join(vals) + ("," if len(vals) == 1 else "")})'
    if isinstance(val, complex):
        return f'{argname}={str(val)}'
    # return None to let pytest handle the formatting
    return None
