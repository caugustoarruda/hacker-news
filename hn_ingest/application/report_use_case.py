"""Caso de uso de relatório (RF12)."""

from typing import Optional

from hn_ingest.domain.entities import RunSummary
from hn_ingest.domain.repositories import RunLogRepository, StateRepository


def get_latest_summary(
    run_log_repository: RunLogRepository,
) -> Optional[RunSummary]:
    """Retorna o resumo da execução mais recente, ou `None` se não houver."""
    return run_log_repository.get_latest()


def get_history(run_log_repository: RunLogRepository) -> list[RunSummary]:
    """Retorna o histórico completo, da execução mais recente à mais antiga."""
    return run_log_repository.list_all()


def get_current_state(state_repository: StateRepository) -> Optional[int]:
    """Retorna o `last_item_id` atual (watermark), ou `None` se ausente."""
    return state_repository.get_last_item_id()
