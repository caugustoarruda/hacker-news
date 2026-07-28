"""Cliente HTTP para a API pública do Hacker News, com retry e backoff."""

import time
from typing import Optional

import requests

from hn_ingest import config


class ItemFetchError(Exception):
    """Levantada quando um item não pôde ser obtido após esgotar as tentativas."""


class HackerNewsClient:
    """Encapsula as chamadas HTTP à API Firebase do Hacker News."""

    def __init__(self, base_url: str = config.BASE_URL) -> None:
        self._base_url = base_url.rstrip('/')

    def get_max_item_id(self) -> int:
        """Consulta `GET /maxitem.json` e retorna o maior ID disponível."""
        return self._request_with_retry(f'{self._base_url}/maxitem.json')

    def get_item(self, item_id: int) -> Optional[dict]:
        """Consulta `GET /item/{id}.json`, retornando `None` quando a API
        responde `null` (item removido ou inexistente).
        """
        return self._request_with_retry(
            f'{self._base_url}/item/{item_id}.json'
        )

    def get_updates(self) -> dict:
        """Consulta `GET /updates.json`, retornando os itens alterados (RF13)."""
        return self._request_with_retry(f'{self._base_url}/updates.json')

    def _request_with_retry(self, url: str):
        """Executa a requisição com retry e backoff exponencial.

        Tenta até `MAX_RETRIES` vezes em caso de timeout ou erro de conexão,
        aguardando `BACKOFF_BASE_SECONDS * 2 ** tentativa` entre elas. Ao
        esgotar as tentativas, propaga `ItemFetchError`.
        """
        last_error: Optional[Exception] = None
        for attempt in range(config.MAX_RETRIES):
            try:
                response = requests.get(
                    url, timeout=config.REQUEST_TIMEOUT_SECONDS
                )
                response.raise_for_status()
                return response.json()
            except (requests.Timeout, requests.ConnectionError) as error:
                last_error = error
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(config.BACKOFF_BASE_SECONDS * 2 ** attempt)
        raise ItemFetchError(
            f'Falha ao consultar {url} após {config.MAX_RETRIES} tentativas.'
        ) from last_error
