import pytest

from tests import create_message

@pytest.mark.asyncio
async def test_success(plugin, read):
    request = {
        "jsonrpc": "2.0",
        "method": "launch_platform_client"
    }

    read.side_effect = [create_message(request), b""]
    plugin.launch_platform_client.return_value = None
    await plugin.run()
    await plugin.wait_closed()
    plugin.launch_platform_client.assert_called_with()
