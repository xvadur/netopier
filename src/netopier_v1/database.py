from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, cast

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from netopier_v1.config import get_settings

type DbRow = dict[str, Any]
type DbConnection = Connection[DbRow]

_pool: ConnectionPool[DbConnection] | None = None


def get_pool() -> ConnectionPool[DbConnection]:
    global _pool
    if _pool is None:
        _pool = cast(
            ConnectionPool[DbConnection],
            ConnectionPool(
                conninfo=get_settings().database_url,
                min_size=1,
                max_size=8,
                kwargs={"row_factory": dict_row},
                open=True,
            ),
        )
    return _pool


@contextmanager
def connection() -> Iterator[DbConnection]:
    with get_pool().connection() as conn:
        yield conn


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
