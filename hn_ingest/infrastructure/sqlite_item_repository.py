"""Implementação SQLite do repositório de itens."""

import sqlite3
from datetime import datetime, timezone

from hn_ingest.domain.entities import Item, ProcessOutcome
from hn_ingest.domain.repositories import ItemRepository

_COMPARABLE_COLUMNS = (
    'type', 'by', 'time', 'title', 'url', 'score', 'descendants',
    'parent', 'text', 'deleted', 'dead', 'raw_json',
)
_COMPARABLE_COLUMNS_SQL = ', '.join(_COMPARABLE_COLUMNS)

_UPSERT_SQL = '''
    INSERT INTO items (
        id, type, by, time, title, url, score, descendants, parent, text,
        deleted, dead, raw_json, inserted_at, updated_at
    ) VALUES (
        :id, :type, :by, :time, :title, :url, :score, :descendants, :parent,
        :text, :deleted, :dead, :raw_json, :now, :now
    )
    ON CONFLICT(id) DO UPDATE SET
        type = excluded.type,
        by = excluded.by,
        time = excluded.time,
        title = excluded.title,
        url = excluded.url,
        score = excluded.score,
        descendants = excluded.descendants,
        parent = excluded.parent,
        text = excluded.text,
        deleted = excluded.deleted,
        dead = excluded.dead,
        raw_json = excluded.raw_json,
        updated_at = excluded.updated_at
'''


class SqliteItemRepository(ItemRepository):
    """Persiste itens do Hacker News na tabela `items` via SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def upsert(self, item: Item) -> ProcessOutcome:
        """Insere ou atualiza o item, evitando escrita quando não há mudança.

        A decisão entre `INSERTED`/`UPDATED`/`SKIPPED` é tomada comparando o
        item recebido com a linha já persistida antes de executar o
        `INSERT ... ON CONFLICT(id) DO UPDATE`.
        """
        existing = self._connection.execute(
            f'SELECT {_COMPARABLE_COLUMNS_SQL} FROM items WHERE id = ?',
            (item.id,),
        ).fetchone()

        if existing is not None and self._is_unchanged(existing, item):
            return ProcessOutcome.SKIPPED

        now = datetime.now(timezone.utc).isoformat()
        self._connection.execute(
            _UPSERT_SQL,
            {
                'id': item.id,
                'type': item.type,
                'by': item.by,
                'time': item.time,
                'title': item.title,
                'url': item.url,
                'score': item.score,
                'descendants': item.descendants,
                'parent': item.parent,
                'text': item.text,
                'deleted': int(item.deleted),
                'dead': int(item.dead),
                'raw_json': item.raw_json,
                'now': now,
            },
        )
        self._connection.commit()
        if existing is not None:
            return ProcessOutcome.UPDATED
        return ProcessOutcome.INSERTED

    def exists(self, item_id: int) -> bool:
        row = self._connection.execute(
            'SELECT 1 FROM items WHERE id = ?', (item_id,)
        ).fetchone()
        return row is not None

    @staticmethod
    def _is_unchanged(existing: sqlite3.Row, item: Item) -> bool:
        new_values = (
            item.type, item.by, item.time, item.title, item.url, item.score,
            item.descendants, item.parent, item.text, int(item.deleted),
            int(item.dead), item.raw_json,
        )
        existing_values = tuple(
            existing[column] for column in _COMPARABLE_COLUMNS
        )
        return existing_values == new_values
