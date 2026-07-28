"""Contratos (interfaces) de persistência do domínio."""

from abc import ABC, abstractmethod
from typing import Optional

from hn_ingest.domain.entities import Item, ProcessOutcome, RunSummary


class ItemRepository(ABC):
    """Contrato de persistência de itens do Hacker News."""

    @abstractmethod
    def upsert(self, item: Item) -> ProcessOutcome:
        """Insere ou atualiza um item, retornando o resultado da operação."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, item_id: int) -> bool:
        """Verifica se um item com o `item_id` informado já está persistido."""
        raise NotImplementedError


class StateRepository(ABC):
    """Contrato de persistência do estado incremental (watermark)."""

    @abstractmethod
    def get_last_item_id(self) -> Optional[int]:
        """Retorna o último ID processado com sucesso, ou `None` se ausente."""
        raise NotImplementedError

    @abstractmethod
    def set_last_item_id(self, value: int) -> None:
        """Atualiza o último ID processado com sucesso."""
        raise NotImplementedError


class RunLogRepository(ABC):
    """Contrato de persistência do histórico de execuções."""

    @abstractmethod
    def save(self, summary: RunSummary) -> None:
        """Registra o resumo de uma execução no histórico."""
        raise NotImplementedError

    @abstractmethod
    def get_latest(self) -> Optional[RunSummary]:
        """Retorna o resumo da execução mais recente, ou `None` se não houver."""
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[RunSummary]:
        """Retorna todas as execuções registradas."""
        raise NotImplementedError
