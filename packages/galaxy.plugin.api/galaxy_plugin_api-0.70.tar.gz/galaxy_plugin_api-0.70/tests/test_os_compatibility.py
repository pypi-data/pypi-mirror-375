from unittest.mock import call

import pytest
from galaxy.api.consts import OSCompatibility
from galaxy.api.errors import BackendError

from tests import create_message, get_messages


@pytest.mark.asyncio
async def test_get_os_compatibility_success(plugin, read, write):
    context = "abc"
    plugin.prepare_os_compatibility_context.return_value = context
    request = {
        "jsonrpc": "2.0",
        "id": "11",
        "method": "start_os_compatibility_import",
        "params": {"game_ids": ["666", "13", "42"]}
    }
    read.side_effect = [create_message(request), b""]
    plugin.get_os_compatibility.side_effect = [
        OSCompatibility.Linux,
        None,
        OSCompatibility.Windows | OSCompatibility.MacOS,
    ]
    await plugin.run()
    await plugin.wait_closed()
    plugin.get_os_compatibility.assert_has_calls([
        call("666", context),
        call("13", context),
        call("42", context),
    ])
    plugin.os_compatibility_import_complete.assert_called_once_with()

    assert get_messages(write) == [
        {
            "jsonrpc": "2.0",
            "id": "11",
            "result": None
        },
        {
            "jsonrpc": "2.0",
            "method": "os_compatibility_import_success",
            "params": {
                "game_id": "666",
                "os_compatibility": OSCompatibility.Linux.value
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "os_compatibility_import_success",
            "params": {
                "game_id": "13",
                "os_compatibility": None
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "os_compatibility_import_success",
            "params": {
                "game_id": "42",
                "os_compatibility": (OSCompatibility.Windows | OSCompatibility.MacOS).value
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "os_compatibility_import_finished",
            "params": None
        }
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("exception,code,message,internal_type", [
    (BackendError, 4, "Backend error", "BackendError"),
    (KeyError, 0, "Unknown error", "UnknownError")
])
async def test_get_os_compatibility_error(exception, code, message, internal_type, plugin, read, write):
    game_id = "6"
    request_id = "55"
    plugin.prepare_os_compatibility_context.return_value = None
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "start_os_compatibility_import",
        "params": {"game_ids": [game_id]}
    }
    read.side_effect = [create_message(request), b""]
    plugin.get_os_compatibility.side_effect = exception
    await plugin.run()
    await plugin.wait_closed()
    plugin.get_os_compatibility.assert_called()
    plugin.os_compatibility_import_complete.assert_called_once_with()

    assert get_messages(write) == [
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": None
        },
        {
            "jsonrpc": "2.0",
            "method": "os_compatibility_import_failure",
            "params": {
                "game_id": game_id,
                "error": {
                    "code": code,
                    "message": message,
                    "data": {"internal_type": internal_type}
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "os_compatibility_import_finished",
            "params": None
        }
    ]


@pytest.mark.asyncio
async def test_prepare_get_os_compatibility_context_error(plugin, read, write):
    request_id = "31415"
    plugin.prepare_os_compatibility_context.side_effect = BackendError()
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "start_os_compatibility_import",
        "params": {"game_ids": ["6"]}
    }
    read.side_effect = [create_message(request), b""]
    await plugin.run()
    await plugin.wait_closed()

    assert get_messages(write) == [
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": 4,
                "message": "Backend error",
                "data": {"internal_type": "BackendError"}
            }
        }
    ]


@pytest.mark.asyncio
async def test_import_already_in_progress_error(plugin, read, write):
    plugin.prepare_os_compatibility_context.return_value = None
    requests = [
        {
            "jsonrpc": "2.0",
            "id": "3",
            "method": "start_os_compatibility_import",
            "params": {
                "game_ids": ["42"]
            }
        },
        {
            "jsonrpc": "2.0",
            "id": "4",
            "method": "start_os_compatibility_import",
            "params": {
                "game_ids": ["666"]
            }
        }
    ]
    read.side_effect = [
        create_message(requests[0]),
        create_message(requests[1]),
        b""
    ]

    await plugin.run()
    await plugin.wait_closed()

    responses = get_messages(write)
    assert {
        "jsonrpc": "2.0",
        "id": "3",
        "result": None
    } in responses
    assert {
        "jsonrpc": "2.0",
        "id": "4",
        "error": {
            "code": 600,
            "message": "Import already in progress",
            "data": {"internal_type": "ImportInProgress"}
        }
    } in responses

