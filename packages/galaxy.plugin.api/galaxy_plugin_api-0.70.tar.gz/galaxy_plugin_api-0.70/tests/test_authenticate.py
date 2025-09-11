import pytest

from galaxy.api.types import Authentication
from galaxy.api.errors import (
    UnknownError,
    BackendNotAvailable,
    BackendTimeout,
    BackendError,
    InvalidCredentials,
    NetworkError,
    ProtocolError,
    TemporaryBlocked,
    Banned,
    AccessDenied,
)
from galaxy.unittest.mock import skip_loop

from tests import create_message, get_messages


@pytest.mark.asyncio
async def test_success(plugin, read, write):
    request = {
        "jsonrpc": "2.0",
        "id": "3",
        "method": "init_authentication"
    }
    read.side_effect = [create_message(request), b""]
    plugin.authenticate.return_value = Authentication("132", "Zenek")
    await plugin.run()
    await plugin.wait_closed()
    plugin.authenticate.assert_called_with()

    assert get_messages(write) == [
        {
            "jsonrpc": "2.0",
            "id": "3",
            "result": {
                "user_id": "132",
                "user_name": "Zenek"
            }
        }
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("error,code,message, internal_type", [
    pytest.param(UnknownError, 0, "Unknown error", "UnknownError"),
    pytest.param(BackendNotAvailable, 2, "Backend not available", "BackendNotAvailable"),
    pytest.param(BackendTimeout, 3, "Backend timed out", "BackendTimeout"),
    pytest.param(BackendError, 4, "Backend error", "BackendError"),
    pytest.param(InvalidCredentials, 100, "Invalid credentials", "InvalidCredentials"),
    pytest.param(NetworkError, 101, "Network error", "NetworkError"),
    pytest.param(ProtocolError, 103, "Protocol error", "ProtocolError"),
    pytest.param(TemporaryBlocked, 104, "Temporary blocked", "TemporaryBlocked"),
    pytest.param(Banned, 105, "Banned", "Banned"),
    pytest.param(AccessDenied, 106, "Access denied", "AccessDenied"),
])
async def test_failure(plugin, read, write, error, code, message, internal_type):
    request = {
        "jsonrpc": "2.0",
        "id": "3",
        "method": "init_authentication"
    }

    read.side_effect = [create_message(request), b""]
    plugin.authenticate.side_effect = error()
    await plugin.run()
    await plugin.wait_closed()
    plugin.authenticate.assert_called_with()

    assert get_messages(write) == [
        {
            "jsonrpc": "2.0",
            "id": "3",
            "error": {
                "code": code,
                "message": message,
                "data" : {"internal_type" : internal_type}
            }
        }
    ]


@pytest.mark.asyncio
async def test_stored_credentials(plugin, read, write):
    request = {
        "jsonrpc": "2.0",
        "id": "3",
        "method": "init_authentication",
        "params": {
            "stored_credentials": {
                "token": "ABC"
            }
        }
    }
    read.side_effect = [create_message(request), b""]
    plugin.authenticate.return_value = Authentication("132", "Zenek")
    await plugin.run()
    await plugin.wait_closed()
    plugin.authenticate.assert_called_with(stored_credentials={"token": "ABC"})
    write.assert_called()


@pytest.mark.asyncio
async def test_store_credentials(plugin, write):
    credentials = {
        "token": "ABC"
    }
    plugin.store_credentials(credentials)
    await skip_loop()

    assert get_messages(write) == [
        {
            "jsonrpc": "2.0",
            "method": "store_credentials",
            "params": credentials
        }
    ]


@pytest.mark.asyncio
async def test_lost_authentication(plugin, write):
    plugin.lost_authentication()
    await skip_loop()

    assert get_messages(write) == [
        {
            "jsonrpc": "2.0",
            "method": "authentication_lost",
            "params": None
        }
    ]
