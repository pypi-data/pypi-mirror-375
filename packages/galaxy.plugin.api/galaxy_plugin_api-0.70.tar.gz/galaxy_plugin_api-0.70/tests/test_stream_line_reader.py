import pytest

from galaxy.reader import StreamLineReader


@pytest.fixture()
def stream_line_reader(reader):
    return StreamLineReader(reader)


@pytest.mark.asyncio
async def test_message(stream_line_reader, read):
    read.return_value = b"a\n"
    assert await stream_line_reader.readline() == b"a"
    read.assert_called_once()


@pytest.mark.asyncio
async def test_separate_messages(stream_line_reader, read):
    read.side_effect = [b"a\n", b"b\n"]
    assert await stream_line_reader.readline() == b"a"
    assert await stream_line_reader.readline() == b"b"
    assert read.call_count == 2


@pytest.mark.asyncio
async def test_connected_messages(stream_line_reader, read):
    read.return_value = b"a\nb\n"
    assert await stream_line_reader.readline() == b"a"
    assert await stream_line_reader.readline() == b"b"
    read.assert_called_once()


@pytest.mark.asyncio
async def test_cut_message(stream_line_reader, read):
    read.side_effect = [b"a", b"b\n"]
    assert await stream_line_reader.readline() == b"ab"
    assert read.call_count == 2


@pytest.mark.asyncio
async def test_half_message(stream_line_reader, read):
    read.side_effect = [b"a", b""]
    assert await stream_line_reader.readline() == b""
    assert read.call_count == 2
