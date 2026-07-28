"""Objetos de transferência de dados usados pela camada de aplicação.

`RunSummary` já é definido em `domain/entities.py` e é reutilizado aqui sem
duplicação. Este módulo concentra apenas os objetos específicos da camada de
aplicação: o resultado interno de `process_range` e o resultado exposto
pelos casos de uso de carga (que precisam representar tanto o sucesso quanto
os casos de borda descritos no PRD).
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from hn_ingest.domain.entities import RunSummary


@dataclass
class ProcessRangeResult:
    """Resultado da varredura de um intervalo de IDs por `process_range`."""

    queried_count: int
    inserted_count: int
    updated_count: int
    skipped_count: int
    failed_count: int
    last_success_id: int


class LoadStatus(Enum):
    """Situação final de uma execução de carga inicial ou incremental."""

    COMPLETED = auto()
    ALREADY_INITIALIZED = auto()
    NOT_INITIALIZED = auto()
    NO_NEW_ITEMS = auto()


@dataclass
class LoadResult:
    """Resultado de uma carga (inicial ou incremental).

    `summary` só é preenchido quando `status` for `LoadStatus.COMPLETED`; nos
    demais casos, a apresentação deve usar apenas `status` para decidir a
    mensagem a exibir.
    """

    status: LoadStatus
    summary: Optional[RunSummary] = None
