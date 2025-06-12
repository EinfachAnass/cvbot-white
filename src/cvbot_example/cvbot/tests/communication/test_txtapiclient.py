import pytest
from cvbot.communication.txtapiclient import TxtApiClient
import os
from ..conftest import session



@pytest.fixture(scope="session")
def api_client(session) -> TxtApiClient:
    """Create a TxtApiClient instance."""
    host = os.getenv("TXT_API_HOST", "localhost")
    port = int(os.getenv("TXT_API_PORT", 8080))
    key = os.getenv("TXT_API_KEY", None)
    return TxtApiClient(host, port, key, session=session)

@pytest.mark.asyncio
async def test_discovery(api_client: TxtApiClient):
    """Test the discovery of the TxtApiClient."""
    devices = await api_client.discover_devices()
    assert len(devices) > 0, "No devices found"
