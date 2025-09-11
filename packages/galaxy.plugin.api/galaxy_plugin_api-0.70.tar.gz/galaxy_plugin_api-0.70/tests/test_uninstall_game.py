import pytest

from tests import create_message

@pytest.mark.asyncio
async def test_success(plugin, read):
    request = {
        "jsonrpc": "2.0",
        "method": "uninstall_game",
        "params": {
            "game_id": "3"
        }
    }
    read.side_effect = [create_message(request), b""]
    plugin.get_owned_games.return_value = None
    await plugin.run()
    await plugin.wait_closed()
    plugin.uninstall_game.assert_called_with(game_id="3")
