from galaxy.api.types import UserInfo
from galaxy.api.errors import UnknownError
from galaxy.unittest.mock import skip_loop

import pytest

from tests import create_message, get_messages


@pytest.mark.asyncio
async def test_get_friends_success(plugin, read, write):
    request = {
        "jsonrpc": "2.0",
        "id": "3",
        "method": "import_friends"
    }

    read.side_effect = [create_message(request), b""]
    plugin.get_friends.return_value = [
        UserInfo("3", "Jan", "https://avatar.url/u3", None),
        UserInfo("5", "Ola", None, "https://profile.url/u5"),
        UserInfo("6", "Ola2", None),
        UserInfo("7", "Ola3"),
    ]
    await plugin.run()
    await plugin.wait_closed()
    plugin.get_friends.assert_called_with()

    assert get_messages(write) == [
        {
            "jsonrpc": "2.0",
            "id": "3",
            "result": {
                "friend_info_list": [
                    {"user_id": "3", "user_name": "Jan", "avatar_url": "https://avatar.url/u3"},
                    {"user_id": "5", "user_name": "Ola", "profile_url": "https://profile.url/u5"},
                    {"user_id": "6", "user_name": "Ola2"},
                    {"user_id": "7", "user_name": "Ola3"},
                ]
            }
        }
    ]


@pytest.mark.asyncio
async def test_get_friends_failure(plugin, read, write):
    request = {
        "jsonrpc": "2.0",
        "id": "3",
        "method": "import_friends"
    }

    read.side_effect = [create_message(request), b""]
    plugin.get_friends.side_effect = UnknownError()
    await plugin.run()
    await plugin.wait_closed()
    plugin.get_friends.assert_called_with()

    assert get_messages(write) == [
        {
            "jsonrpc": "2.0",
            "id": "3",
            "error": {
                "code": 0,
                "message": "Unknown error",
                "data": {"internal_type": "UnknownError"}
            }
        }
    ]


@pytest.mark.asyncio
async def test_add_friend(plugin, write):
    friend = UserInfo("7", "Kuba", avatar_url="https://avatar.url/kuba.jpg", profile_url="https://profile.url/kuba")

    plugin.add_friend(friend)
    await skip_loop()
    await plugin.wait_closed()

    assert get_messages(write) == [
        {
            "jsonrpc": "2.0",
            "method": "friend_added",
            "params": {
                "friend_info": {
                    "user_id": "7",
                    "user_name": "Kuba",
                    "avatar_url": "https://avatar.url/kuba.jpg",
                    "profile_url": "https://profile.url/kuba"
                }
            }
        }
    ]


@pytest.mark.asyncio
async def test_remove_friend(plugin, write):
    plugin.remove_friend("5")
    await skip_loop()
    await plugin.wait_closed()
    assert get_messages(write) == [
        {
            "jsonrpc": "2.0",
            "method": "friend_removed",
            "params": {
                "user_id": "5"
            }
        }
    ]


@pytest.mark.asyncio
async def test_update_friend_info(plugin, write):
    plugin.update_friend_info(
        UserInfo("7", "Jakub", avatar_url="https://new-avatar.url/kuba2.jpg", profile_url="https://profile.url/kuba")
    )
    await skip_loop()
    await plugin.wait_closed()
    assert get_messages(write) == [
        {
            "jsonrpc": "2.0",
            "method": "friend_updated",
            "params": {
                "friend_info": {
                    "user_id": "7",
                    "user_name": "Jakub",
                    "avatar_url": "https://new-avatar.url/kuba2.jpg",
                    "profile_url": "https://profile.url/kuba"
                }
            }
        }
    ]
