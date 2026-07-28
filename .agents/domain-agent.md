# Agente de Domínio

> Antes de começar, leia `../PRD.md` (fonte da verdade) e
> `shared-conventions.md` (regras válidas para todos os agentes).

## Papel

Estabelecer a fundação do projeto: estrutura de diretórios, configuração e a
camada de domínio — entidades e contratos (interfaces) de persistência, sem
nenhuma dependência de bibliotecas externas ou detalhes de implementação
concreta (SQLite, HTTP, CLI).

## Objetivo

Entregar um domínio estável o suficiente para que os agentes de
Infraestrutura e de Aplicação possam programar contra as interfaces
definidas aqui, sem precisar alterá-las depois.

## Pré-requisitos

Nenhum — este é o primeiro agente da sequência.

## Escopo (PRD §10, Sprint 1)

### 1.1. Estrutura inicial do projeto
- Criar `hn_ingest/` com subpacotes `domain/`, `infrastructure/`,
  `application/` e `presentation/`, cada um com `__init__.py`.
- Criar `requirements.txt` contendo apenas `requests`.
- Criar `main.py` na raiz como ponto de entrada, que apenas importa e invoca
  a função principal da CLI (`presentation/cli.py`) — mesmo que essa função
  ainda não exista de fato; o Agente de Apresentação a implementará depois.
  Se preferir, deixe esse arquivo como último passo de handoff, mas a
  estrutura de pastas deve existir desde já.
- Configurar `.gitignore` básico (arquivo `.db` local, `__pycache__`,
  ambiente virtual).

### 1.2. Módulo de configuração (`hn_ingest/config.py`)
- `BASE_URL` da API do Hacker News
  (`https://hacker-news.firebaseio.com/v0/`).
- Constantes de resiliência: `REQUEST_TIMEOUT_SECONDS`, `MAX_RETRIES`,
  `BACKOFF_BASE_SECONDS`.
- `DEFAULT_INITIAL_LOAD_LIMIT` (quantidade padrão da carga inicial).
- `DATABASE_PATH` (caminho padrão do arquivo SQLite).
- Todas as constantes acima devem poder ser sobrescritas por variáveis de
  ambiente, com fallback para os valores padrão.

### 1.3. Entidades de domínio (`hn_ingest/domain/entities.py`)
- `dataclass Item` com os campos: `id`, `type`, `by`, `time`, `title`, `url`,
  `score`, `descendants`, `parent`, `text`, `deleted`, `dead`, `raw_json`.
- Método de fábrica `Item.from_api_response(data: dict)`, construindo a
  entidade a partir do JSON da API e preenchendo `raw_json` com o JSON
  serializado original.
- `dataclass RunSummary` com: `run_type`, `range_start`, `range_end`,
  `queried_count`, `inserted_count`, `updated_count`, `skipped_count`,
  `failed_count`, `duration_seconds`, `started_at`, `finished_at`.
- `enum ProcessOutcome` com `INSERTED`, `UPDATED`, `SKIPPED`, `FAILED`.

### 1.4. Contratos de repositório (`hn_ingest/domain/repositories.py`)
- `ItemRepository` (interface abstrata): `upsert(item: Item) ->
  ProcessOutcome`, `exists(item_id: int) -> bool`.
- `StateRepository` (interface abstrata): `get_last_item_id() -> int |
  None`, `set_last_item_id(value: int) -> None`.
- `RunLogRepository` (interface abstrata): `save(summary: RunSummary) ->
  None`, `get_latest() -> RunSummary | None`, `list_all() ->
  list[RunSummary]`.

## Não-objetivos

- Não implementar SQLite, HTTP ou CLI — isso é responsabilidade dos agentes
  seguintes.
- Não escrever lógica de negócio (cálculo de intervalo, watermark,
  contabilização) — pertence ao Agente de Aplicação.

## Critérios de conclusão

1. O projeto importa (`import hn_ingest...`) sem erros.
2. `config.py` expõe todas as constantes listadas, com suporte a variáveis
   de ambiente.
3. `entities.py` e `repositories.py` não importam nada de
   `infrastructure/`, `application/` ou `presentation/`.
4. As interfaces definidas cobrem exatamente os métodos usados nos casos de
   uso descritos no PRD (ver `application-agent.md`), sem métodos extras
   especulativos.

## Handoff

Ao final, os agentes seguintes devem encontrar prontos:
- A estrutura de pastas completa (`domain/`, `infrastructure/`,
  `application/`, `presentation/`).
- `config.py` com todas as constantes de configuração.
- `Item`, `RunSummary`, `ProcessOutcome` em `domain/entities.py`.
- `ItemRepository`, `StateRepository`, `RunLogRepository` em
  `domain/repositories.py`, prontos para serem implementados pelo Agente de
  Infraestrutura.
