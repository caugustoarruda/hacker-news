"""Implementação SQLite do repositório de estado incremental (watermark)."""

import sqlite3
from datetime import datetime, timezone
from typing import Optional

from hn_ingest.domain.repositories import StateRepository

_LAST_ITEM_ID_KEY = 'last_item_id'

_UPSERT_SQL = '''
    INSERT INTO run_state (key, value, updated_at)
    VALUES (:key, :value, :now)
    ON CONFLICT(key) DO UPDATE SET
        value = excluded.value,
        updated_at = excluded.updated_at
'''


class SqliteStateRepository(StateRepository):
    """Persiste o watermark (`last_item_id`) na tabela `run_state`."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_last_item_id(self) -> Optional[int]:
        row = self._connection.execute(
            'SELECT value FROM run_state WHERE key = ?', (_LAST_ITEM_ID_KEY,)
        ).fetchone()
        return int(row['value']) if row is not None else None

    def set_last_item_id(self, value: int) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._connection.execute(
            _UPSERT_SQL,
            {'key': _LAST_ITEM_ID_KEY, 'value': str(value), 'now': now},
        )
        self._connection.commit()
