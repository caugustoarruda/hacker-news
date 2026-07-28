"""Entidades e enums do domínio de ingestão do Hacker News."""

import json
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


@dataclass
class Item:
    """Representa um item do Hacker News (story, comment, job, poll, etc.)."""

    id: int
    type: Optional[str]
    by: Optional[str]
    time: Optional[int]
    title: Optional[str]
    url: Optional[str]
    score: Optional[int]
    descendants: Optional[int]
    parent: Optional[int]
    text: Optional[str]
    deleted: bool
    dead: bool
    raw_json: str

    @classmethod
    def from_api_response(cls, data: dict) -> 'Item':
        """Constrói um `Item` a partir do JSON retornado pela API do HN."""
        return cls(
            id=data['id'],
            type=data.get('type'),
            by=data.get('by'),
            time=data.get('time'),
            title=data.get('title'),
            url=data.get('url'),
            score=data.get('score'),
            descendants=data.get('descendants'),
            parent=data.get('parent'),
            text=data.get('text'),
            deleted=bool(data.get('deleted', False)),
            dead=bool(data.get('dead', False)),
            raw_json=json.dumps(data),
        )


@dataclass
class RunSummary:
    """Resumo de uma execução de carga (inicial ou incremental)."""

    run_type: str
    range_start: int
    range_end: int
    queried_count: int
    inserted_count: int
    updated_count: int
    skipped_count: int
    failed_count: int
    duration_seconds: float
    started_at: str
    finished_at: str


class ProcessOutcome(Enum):
    """Resultado do processamento de um único ID de item."""

    INSERTED = auto()
    UPDATED = auto()
    SKIPPED = auto()
    FAILED = auto()
