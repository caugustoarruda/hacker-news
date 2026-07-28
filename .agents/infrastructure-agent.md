# Agente de Infraestrutura

> Antes de começar, leia `../PRD.md`, `shared-conventions.md` e o resultado
> do `domain-agent.md` (interfaces e entidades já definidas).

## Papel

Implementar os detalhes concretos de acesso a dados (SQLite) e de acesso à
API pública do Hacker News (HTTP), incluindo a resiliência exigida pelo PRD
(retry/backoff). Esta camada implementa os contratos definidos pelo domínio
— nunca o contrário.

## Objetivo

Entregar implementações completas e testáveis manualmente de:
`HackerNewsClient`, `SqliteItemRepository`, `SqliteStateRepository`,
`SqliteRunLogRepository` e o bootstrap do banco (`database.py`), prontas
para serem orquestradas pelo Agente de Aplicação.

## Pré-requisitos

- `domain-agent.md` concluído: `Item`, `RunSummary`, `ProcessOutcome`,
  `ItemRepository`, `StateRepository`, `RunLogRepository` disponíveis.

## Escopo (PRD §10, Sprint 2)

### 2.1. Bootstrap do banco (`hn_ingest/infrastructure/database.py`)
- `get_connection()`: retorna uma conexão `sqlite3` configurada
  (`row_factory`, `PRAGMA foreign_keys`).
- `initialize_schema(connection)`: cria as tabelas `items`, `run_state` e
  `run_log` caso não existam (`CREATE TABLE IF NOT EXISTS`), conforme o
  modelo de dados do PRD §7.1.
- Índices em `items.type` e `items.time`.

### 2.2. Cliente HTTP (`hn_ingest/infrastructure/http_client.py`)
- `HackerNewsClient.get_max_item_id() -> int`: `GET /maxitem.json`.
- `HackerNewsClient.get_item(item_id: int) -> dict | None`: `GET
  /item/{id}.json`, retornando `None` quando a API responde `null`.
- Retry interno com backoff exponencial (`MAX_RETRIES` tentativas, espera
  `BACKOFF_BASE_SECONDS * 2 ** tentativa`), aplicado a timeouts e erros de
  conexão.
- Ao esgotar as tentativas, levantar `ItemFetchError` (exceção específica,
  capturada depois pelo caso de uso — não pela infraestrutura).
- Aplicar `REQUEST_TIMEOUT_SECONDS` (de `config.py`) em toda chamada HTTP.
- (Opcional — RF13) `get_updates() -> dict`: `GET /updates.json`, retornando
  a lista de itens alterados.

### 2.3. Repositório de itens (`sqlite_item_repository.py`)
- `SqliteItemRepository` recebe a conexão SQLite no construtor.
- `upsert(item)` via `INSERT ... ON CONFLICT(id) DO UPDATE ...`, comparando
  campos relevantes antes de decidir entre `ProcessOutcome.INSERTED`,
  `UPDATED` ou `SKIPPED` (sem mudança).
- Preencher `inserted_at` na criação e `updated_at` a cada upsert.
- `exists(item_id)` via `SELECT 1 FROM items WHERE id = ?`.

### 2.4. Repositório de estado (`sqlite_state_repository.py`)
- `SqliteStateRepository` usando a tabela `run_state` (chave/valor).
- `get_last_item_id()`: `None` quando a chave `last_item_id` ainda não
  existir.
- `set_last_item_id(value)`: upsert da chave `last_item_id`, atualizando
  `updated_at`.

### 2.5. Repositório de execuções (`sqlite_run_log_repository.py`)
- `save(summary)`: insere uma linha em `run_log`.
- `get_latest()`: registro mais recente por `finished_at`.
- `list_all()`: todas as execuções, da mais recente para a mais antiga.

## Não-objetivos

- Não decidir *quando* processar um intervalo de IDs, nem calcular
  watermark — isso é regra de negócio do Agente de Aplicação. A
  infraestrutura apenas executa operações de leitura/escrita e comunicação
  HTTP.
- Não capturar `ItemFetchError` dentro da própria infraestrutura — ela deve
  propagar para quem chamou (o caso de uso), conforme RF08.

## Critérios de conclusão

1. Todas as classes implementam exatamente as interfaces do domínio, sem
   métodos adicionais não previstos.
2. `initialize_schema` é idempotente (pode ser chamado múltiplas vezes sem
   erro).
3. `upsert` nunca duplica linhas — reexecuções com o mesmo `id` resultam em
   `UPDATED` ou `SKIPPED`, nunca em novo registro.
4. Timeouts/erros de rede são isolados dentro do cliente HTTP e resultam em
   `ItemFetchError` após `MAX_RETRIES` tentativas — nunca em exceção não
   tratada subindo para o chamador de forma inesperada.

## Handoff

Ao final, o Agente de Aplicação deve encontrar prontos:
- `database.get_connection()` e `database.initialize_schema()`.
- `HackerNewsClient` completo, incluindo `ItemFetchError`.
- `SqliteItemRepository`, `SqliteStateRepository`,
  `SqliteRunLogRepository`, todos instanciáveis a partir de uma conexão
  SQLite e prontos para injeção nos casos de uso.
