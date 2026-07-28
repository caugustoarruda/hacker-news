"""Processamento central de um intervalo de IDs do Hacker News.

Concentra as regras RF06 (itens nulos), RF08 (falha isolada não interrompe o
processamento) e RF09 (cálculo do watermark contíguo).
"""

import logging

from hn_ingest.application.dto import ProcessRangeResult
from hn_ingest.domain.entities import Item, ProcessOutcome
from hn_ingest.domain.repositories import ItemRepository
from hn_ingest.infrastructure.http_client import (
    HackerNewsClient,
    ItemFetchError,
)

logger = logging.getLogger(__name__)


def process_range(
    start_id: int,
    end_id: int,
    http_client: HackerNewsClient,
    item_repository: ItemRepository,
) -> ProcessRangeResult:
    """Processa sequencialmente os IDs de `start_id` a `end_id` (inclusive).

    Falhas individuais (`ItemFetchError`) nunca interrompem o loop (RF08).
    O `last_success_id` avança apenas enquanto a sequência, a partir de
    `start_id`, não tiver encontrado nenhum `FAILED`: o avanço para
    definitivamente no primeiro ID com falha, mesmo que IDs posteriores
    tenham sido processados com sucesso (RF09).
    """
    queried_count = 0
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    failed_count = 0

    last_success_id = start_id - 1
    watermark_blocked = False

    for item_id in range(start_id, end_id + 1):
        queried_count += 1
        outcome = _process_single_item(item_id, http_client, item_repository)

        if outcome == ProcessOutcome.INSERTED:
            inserted_count += 1
        elif outcome == ProcessOutcome.UPDATED:
            updated_count += 1
        elif outcome == ProcessOutcome.SKIPPED:
            skipped_count += 1
        else:
            failed_count += 1
            watermark_blocked = True

        if not watermark_blocked:
            last_success_id = item_id

    return ProcessRangeResult(
        queried_count=queried_count,
        inserted_count=inserted_count,
        updated_count=updated_count,
        skipped_count=skipped_count,
        failed_count=failed_count,
        last_success_id=last_success_id,
    )


def _process_single_item(
    item_id: int,
    http_client: HackerNewsClient,
    item_repository: ItemRepository,
) -> ProcessOutcome:
    """Consulta e persiste um único item, retornando o `ProcessOutcome`.

    Um item nulo (removido/inexistente) é tratado como ignorado (RF06). Uma
    falha de rede/timeout, após esgotar as tentativas do cliente HTTP, é
    tratada como `FAILED` sem propagar a exceção (RF08).
    """
    try:
        data = http_client.get_item(item_id)
    except ItemFetchError:
        logger.warning('Falha ao consultar o item %s.', item_id)
        return ProcessOutcome.FAILED

    if data is None:
        return ProcessOutcome.SKIPPED

    item = Item.from_api_response(data)
    return item_repository.upsert(item)
