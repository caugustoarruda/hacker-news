"""Conexão SQLite e criação do schema do banco local.

Implementa o modelo de dados descrito no PRD §7.1 (tabelas `items`,
`run_state` e `run_log`).
"""

import sqlite3

from hn_ingest import config


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão SQLite configurada para uso pelos repositórios."""
    connection = sqlite3.connect(config.DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Cria as tabelas e índices do banco, caso ainda não existam.

    Seguro para ser chamado em toda inicialização da aplicação, pois usa
    `CREATE TABLE IF NOT EXISTS`.
    """
    connection.execute(
        '''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            type TEXT,
            by TEXT,
            time INTEGER,
            title TEXT,
            url TEXT,
            score INTEGER,
            descendants INTEGER,
            parent INTEGER,
            text TEXT,
            deleted INTEGER,
            dead INTEGER,
            raw_json TEXT,
            inserted_at TEXT,
            updated_at TEXT
        )
        '''
    )
    connection.execute(
        '''
        CREATE TABLE IF NOT EXISTS run_state (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        )
        '''
    )
    connection.execute(
        '''
        CREATE TABLE IF NOT EXISTS run_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_type TEXT,
            range_start INTEGER,
            range_end INTEGER,
            queried_count INTEGER,
            inserted_count INTEGER,
            updated_count INTEGER,
            skipped_count INTEGER,
            failed_count INTEGER,
            duration_seconds REAL,
            started_at TEXT,
            finished_at TEXT
        )
        '''
    )
    connection.execute(
        'CREATE INDEX IF NOT EXISTS idx_items_type ON items (type)'
    )
    connection.execute(
        'CREATE INDEX IF NOT EXISTS idx_items_time ON items (time)'
    )
    connection.commit()
