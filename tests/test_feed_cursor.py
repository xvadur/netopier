from uuid import UUID

from netopier_v1.feed import _decode_cursor, _encode_cursor


def test_cursor_round_trip() -> None:
    story_id = UUID("00000000-0000-0000-0000-000000000042")
    cursor = _encode_cursor(story_id, 42)
    assert _decode_cursor(cursor) == (story_id, 42)
