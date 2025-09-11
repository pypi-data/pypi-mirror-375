import json

import pytest


@pytest.mark.asyncio
async def test_chunked_messages(plugin, read):
    request = {
        "jsonrpc": "2.0",
        "method": "install_game",
        "params": {
            "game_id": "3"
        }
    }

    message = json.dumps(request).encode() + b"\n"
    read.side_effect = [message[:5], message[5:], b""]
    await plugin.run()
    await plugin.wait_closed()
    plugin.install_game.assert_called_with(game_id="3")


@pytest.mark.asyncio
async def test_joined_messages(plugin, read):
    requests = [
        {
            "jsonrpc": "2.0",
            "method": "install_game",
            "params": {
                "game_id": "3"
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "launch_game",
            "params": {
                "game_id": "3"
            }
        }
    ]
    data = b"".join([json.dumps(request).encode() + b"\n" for request in requests])

    read.side_effect = [data, b""]
    await plugin.run()
    await plugin.wait_closed()
    plugin.install_game.assert_called_with(game_id="3")
    plugin.launch_game.assert_called_with(game_id="3")


@pytest.mark.asyncio
async def test_not_finished(plugin, read):
    request = {
        "jsonrpc": "2.0",
        "method": "install_game",
        "params": {
            "game_id": "3"
        }
    }

    message = json.dumps(request).encode() # no new line
    read.side_effect = [message, b""]
    await plugin.run()
    await plugin.wait_closed()
    plugin.install_game.assert_not_called()
