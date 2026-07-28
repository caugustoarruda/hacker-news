# Agente de Aplicação

> Antes de começar, leia `../PRD.md`, `shared-conventions.md` e os
> resultados de `domain-agent.md` e `infrastructure-agent.md`.

## Papel

Orquestrar domínio e infraestrutura, concentrando as regras de negócio do
projeto: cálculo de intervalo de IDs, cálculo de watermark, contabilização
do resumo de execução. Esta é a camada que decide *o quê* fazer; a
infraestrutura decide *como*.

## Objetivo

Entregar os quatro casos de uso do PRD — processamento de intervalo, carga
inicial, carga incremental e relatório — totalmente funcionais e
consumíveis pela CLI, encapsulando toda a lógica de RF01–RF13.

## Pré-requisitos

- `domain-agent.md` e `infrastructure-agent.md` concluídos.

## Escopo (PRD §10, Sprint 3)

### 3.1. Processamento central de intervalo (`process_range_use_case.py`)
- Função/classe `process_range(start_id, end_id, http_client,
  item_repository)`, iterando sequencialmente de `start_id` a `end_id`.
- Para cada ID: consultar via `http_client.get_item`; `None` conta como
  ignorado (item nulo/removido — RF06).
- Para cada item válido: converter para `Item` e delegar a
  `item_repository.upsert`, coletando o `ProcessOutcome`.
- Capturar `ItemFetchError` por ID individualmente, registrar como
  `FAILED`, e **continuar o loop** sem interromper os próximos IDs (RF08).
- Acumular contadores: `queried_count`, `inserted_count`, `updated_count`,
  `skipped_count`, `failed_count`.
- Calcular `last_success_id`: o maior ID, a partir de `start_id`, tal que
  todos os IDs entre `start_id` e ele não resultaram em `FAILED`. O avanço
  para no **primeiro** `FAILED` encontrado na sequência, mesmo que IDs
  posteriores tenham sido processados com sucesso (RF09 — regra crítica,
  não simplificar).
- Retornar um objeto de resultado com os contadores e o `last_success_id`.

### 3.2. Carga inicial (`initial_load_use_case.py`)
- Verificar via `StateRepository` se já existe `last_item_id`; se existir,
  retornar indicação de que a carga inicial já foi feita (sem processar
  nada).
- Consultar `http_client.get_max_item_id()`.
- Calcular `start_id = max(1, maxitem - limit + 1)`, `end_id = maxitem`.
- Registrar `started_at` antes de processar.
- Invocar `process_range` no intervalo calculado.
- Persistir `last_item_id = last_success_id` apenas se `last_success_id >=
  start_id`.
- Montar `RunSummary` (tipo `initial`) com contadores, `range_start`,
  `range_end`, `duration_seconds`, `finished_at`.
- Persistir o `RunSummary` via `RunLogRepository`.
- Retornar o `RunSummary` para a apresentação.

### 3.3. Carga incremental (`incremental_load_use_case.py`)
- Ler `last_item_id`; se não existir, retornar indicação de que a carga
  inicial precisa rodar primeiro.
- Consultar `http_client.get_max_item_id()`.
- Se `maxitem <= last_item_id`, retornar "nenhum item novo" **sem** chamar
  `get_item` nenhuma vez (critério de aceite #2 do PRD).
- Calcular `start_id = last_item_id + 1`, `end_id = maxitem`.
- Reaproveitar `process_range`.
- Persistir novo `last_item_id` apenas se `last_success_id >= start_id`.
- Montar e persistir `RunSummary` (tipo `incremental`), mesma estrutura da
  carga inicial.
- Retornar o `RunSummary` (ou indicação de "nenhum item novo").

### 3.4. Relatório (`report_use_case.py`)
- `get_latest_summary()`: delega a `RunLogRepository.get_latest()`.
- `get_history()`: delega a `RunLogRepository.list_all()`.
- `get_current_state()`: retorna `last_item_id` atual via
  `StateRepository`.

## Não-objetivos

- Não fazer parsing de argumentos de linha de comando nem formatação de
  texto para o usuário — isso é do Agente de Apresentação.
- Não acessar `sqlite3` ou `requests` diretamente — sempre através das
  interfaces/implementações de infraestrutura recebidas por injeção.

## Critérios de conclusão

1. `process_range` nunca interrompe o loop por causa de uma falha
   individual (RF08).
2. O cálculo de `last_success_id` respeita estritamente a regra de
   contiguidade (RF09) — validar mentalmente com um caso onde o meio do
   intervalo falha e o fim tem sucesso: o watermark deve parar antes da
   falha.
3. `incremental_load_use_case` não realiza nenhuma chamada de item quando
   não há itens novos.
4. Os três casos de uso de carga tratam corretamente os casos de borda:
   carga inicial já realizada, carga inicial ausente ao tentar incremental,
   nenhum item novo.

## Handoff

Ao final, o Agente de Apresentação deve encontrar prontos e chamáveis:
`initial_load_use_case`, `incremental_load_use_case`, `report_use_case`
(com seus três métodos), todos recebendo as dependências de infraestrutura
por injeção (nenhuma instanciação implícita dentro dos casos de uso).
