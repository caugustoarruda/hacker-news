"""Implementação SQLite do repositório de histórico de execuções."""

import sqlite3
from typing import Optional

from hn_ingest.domain.entities import RunSummary
from hn_ingest.domain.repositories import RunLogRepository

_INSERT_SQL = '''
    INSERT INTO run_log (
        run_type, range_start, range_end, queried_count, inserted_count,
        updated_count, skipped_count, failed_count, duration_seconds,
        started_at, finished_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

_SELECT_COLUMNS = (
    'run_type, range_start, range_end, queried_count, inserted_count, '
    'updated_count, skipped_count, failed_count, duration_seconds, '
    'started_at, finished_at'
)


class SqliteRunLogRepository(RunLogRepository):
    """Persiste o histórico de execuções na tabela `run_log`."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, summary: RunSummary) -> None:
        self._connection.execute(
            _INSERT_SQL,
            (
                summary.run_type,
                summary.range_start,
                summary.range_end,
                summary.queried_count,
                summary.inserted_count,
                summary.updated_count,
                summary.skipped_count,
                summary.failed_count,
                summary.duration_seconds,
                summary.started_at,
                summary.finished_at,
            ),
        )
        self._connection.commit()

    def get_latest(self) -> Optional[RunSummary]:
        row = self._connection.execute(
            f'SELECT {_SELECT_COLUMNS} FROM run_log '
            'ORDER BY finished_at DESC LIMIT 1'
        ).fetchone()
        return self._to_summary(row) if row is not None else None

    def list_all(self) -> list[RunSummary]:
        rows = self._connection.execute(
            f'SELECT {_SELECT_COLUMNS} FROM run_log ORDER BY finished_at DESC'
        ).fetchall()
        return [self._to_summary(row) for row in rows]

    @staticmethod
    def _to_summary(row: sqlite3.Row) -> RunSummary:
        return RunSummary(
            run_type=row['run_type'],
            range_start=row['range_start'],
            range_end=row['range_end'],
            queried_count=row['queried_count'],
            inserted_count=row['inserted_count'],
            updated_count=row['updated_count'],
            skipped_count=row['skipped_count'],
            failed_count=row['failed_count'],
            duration_seconds=row['duration_seconds'],
            started_at=row['started_at'],
            finished_at=row['finished_at'],
        )
