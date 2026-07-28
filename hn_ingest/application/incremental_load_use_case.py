"""Caso de uso de carga incremental (RF03)."""

import time
from datetime import datetime, timezone

from hn_ingest.application.dto import LoadResult, LoadStatus
from hn_ingest.application.process_range_use_case import process_range
from hn_ingest.domain.entities import RunSummary
from hn_ingest.domain.repositories import (
    ItemRepository,
    RunLogRepository,
    StateRepository,
)
from hn_ingest.infrastructure.http_client import HackerNewsClient


def run_incremental_load(
    http_client: HackerNewsClient,
    item_repository: ItemRepository,
    state_repository: StateRepository,
    run_log_repository: RunLogRepository,
) -> LoadResult:
    """Executa a carga incremental, processando apenas itens após o watermark.

    Requer que a carga inicial já tenha sido executada. Quando não há itens
    novos em relação ao `maxitem` atual, nenhuma chamada de item é feita
    (apenas a consulta a `maxitem`).
    """
    last_item_id = state_repository.get_last_item_id()
    if last_item_id is None:
        return LoadResult(status=LoadStatus.NOT_INITIALIZED)

    max_item_id = http_client.get_max_item_id()
    if max_item_id <= last_item_id:
        return LoadResult(status=LoadStatus.NO_NEW_ITEMS)

    start_id = last_item_id + 1
    end_id = max_item_id

    started_at = datetime.now(timezone.utc)
    start_time = time.monotonic()

    result = process_range(start_id, end_id, http_client, item_repository)

    duration_seconds = time.monotonic() - start_time
    finished_at = datetime.now(timezone.utc)

    if result.last_success_id >= start_id:
        state_repository.set_last_item_id(result.last_success_id)

    summary = RunSummary(
        run_type='incremental',
        range_start=start_id,
        range_end=end_id,
        queried_count=result.queried_count,
        inserted_count=result.inserted_count,
        updated_count=result.updated_count,
        skipped_count=result.skipped_count,
        failed_count=result.failed_count,
        duration_seconds=duration_seconds,
        started_at=started_at.isoformat(),
        finished_at=finished_at.isoformat(),
    )
    run_log_repository.save(summary)

    return LoadResult(status=LoadStatus.COMPLETED, summary=summary)
