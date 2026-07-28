# Ingestão Incremental do Hacker News

Utilitário de linha de comando (CLI) em Python que consulta a API pública do
Hacker News (Firebase API), persiste os itens em um banco SQLite local e
garante que execuções repetidas não gerem duplicidade de registros, mantendo
um estado incremental (watermark) entre execuções.

Este README é um guia prático de uso. Para a especificação completa de
requisitos, arquitetura e critérios de aceite, consulte [`PRD.md`](PRD.md).

## 1. Visão geral e requisitos

O sistema oferece três comandos:

- `initial-load`: carga inicial limitada dos itens mais recentes.
- `incremental-load`: carga incremental, buscando apenas itens novos desde a
  última execução bem-sucedida.
- `report`: relatório da última execução ou do histórico completo.

Não é um serviço contínuo (daemon) nem uma API web — é executado sob demanda,
uma vez por vez.

**Requisitos:**

- Python 3.11 ou superior.
- Dependência externa única: [`requests`](https://pypi.org/project/requests/).

**Instalação:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Carga inicial

Executa a carga inicial, processando os `N` itens mais recentes em relação ao
maior ID disponível na API (`maxitem`) no momento da execução, em ordem
crescente de ID. O parâmetro `--limit` é opcional (padrão: `1000`, definido
em `hn_ingest/config.py` via `DEFAULT_INITIAL_LOAD_LIMIT`).

```bash
python3 main.py initial-load --limit 20
```

Saída esperada (valores variam conforme os itens disponíveis no momento):

```
Carga inicial concluída com sucesso.
Tipo da carga: inicial
Faixa processada: 49087675 a 49087694
Itens consultados: 20
Itens inseridos: 20
Itens atualizados: 0
Itens ignorados: 0
Itens com falha: 0
Duração: 8.09 segundos
Concluída em: 2026-07-28T18:06:34.911492+00:00
```

A carga inicial só pode ser executada uma vez. Reexecutá-la (com watermark já
salvo) não processa nada e apenas informa:

```
A carga inicial já foi realizada anteriormente. Utilize o comando 'incremental-load' para buscar itens novos.
```

## 3. Carga incremental

Processa apenas o intervalo de IDs maior que o watermark salvo (`last_item_id`)
até o `maxitem` atual. Não recebe argumentos além dos globais.

```bash
python3 main.py incremental-load
```

Se houver itens novos, a saída é semelhante a:

```
Carga incremental concluída com sucesso.
Tipo da carga: incremental
Faixa processada: 49087695 a 49087697
Itens consultados: 3
Itens inseridos: 3
Itens atualizados: 0
Itens ignorados: 0
Itens com falha: 0
Duração: 1.21 segundos
Concluída em: 2026-07-28T18:07:06.188616+00:00
```

Se não houver itens novos desde a última execução (situação comum ao rodar
duas vezes seguidas em um curto intervalo), nenhuma chamada de item é feita e
o sistema apenas informa:

```
Nenhum item novo para processar: o watermark já está atualizado em relação ao maior ID disponível na API.
```

Se a carga inicial ainda não tiver sido executada, o comando informa que ela
é um pré-requisito:

```
A carga inicial ainda não foi realizada. Execute o comando 'initial-load' antes de rodar a carga incremental.
```

## 4. Relatório

Exibe o watermark atual e o resumo da última execução:

```bash
python3 main.py report
```

Saída de exemplo:

```
Watermark atual (último ID processado): 49087697

Tipo da carga: incremental
Faixa processada: 49087695 a 49087697
Itens consultados: 3
Itens inseridos: 3
Itens atualizados: 0
Itens ignorados: 0
Itens com falha: 0
Duração: 1.21 segundos
Concluída em: 2026-07-28T18:07:06.188616+00:00
```

Use `--history` para exibir todas as execuções registradas (mais recente
primeiro), em formato de tabela:

```bash
python3 main.py report --history
```

Saída de exemplo:

```
Watermark atual (último ID processado): 49087697

Tipo        Faixa                   Consult.  Inser.  Atual.  Ignor.  Falhas  Duração(s)  Concluída em
------------------------------------------------------------------------------------------------------
incremental 49087695-49087697              3       3       0       0       0        1.21  2026-07-28T18:07:06.188616+00:00
inicial     49087675-49087694             20      20       0       0       0        8.09  2026-07-28T18:06:34.911492+00:00
```

Se nenhuma execução tiver sido registrada ainda, o watermark é exibido como
`nenhum (carga inicial ainda não realizada)` e a mensagem
`Nenhuma execução registrada ainda.` é exibida no lugar do resumo.

## 5. Estrutura de camadas e localização do SQLite

O projeto segue separação em camadas (domínio, infraestrutura, aplicação e
apresentação), com o sentido de dependência sempre
apresentação → aplicação → domínio, e a infraestrutura implementando os
contratos definidos no domínio:

```
hacker-news/
├── hn_ingest/
│   ├── config.py                       # Configurações e constantes (URLs, timeout, retries, caminho do banco)
│   ├── domain/
│   │   ├── entities.py                 # Item, RunSummary, ProcessOutcome
│   │   └── repositories.py             # Interfaces de persistência (ItemRepository, StateRepository, RunLogRepository)
│   ├── infrastructure/
│   │   ├── database.py                 # Conexão SQLite e criação de schema
│   │   ├── http_client.py              # Cliente HTTP com retry/backoff (HackerNewsClient)
│   │   ├── sqlite_item_repository.py   # Implementação do repositório de itens
│   │   ├── sqlite_state_repository.py  # Implementação do repositório de estado (watermark)
│   │   └── sqlite_run_log_repository.py# Implementação do repositório de execuções
│   ├── application/
│   │   ├── dto.py                      # ProcessRangeResult, LoadStatus, LoadResult
│   │   ├── process_range_use_case.py   # Processamento central de um intervalo de IDs
│   │   ├── initial_load_use_case.py    # Orquestra a carga inicial
│   │   ├── incremental_load_use_case.py# Orquestra a carga incremental
│   │   └── report_use_case.py          # Orquestra a geração de relatório
│   └── presentation/
│       └── cli.py                      # Interface de linha de comando (argparse)
├── main.py                             # Ponto de entrada
├── requirements.txt
├── README.md
└── PRD.md
```

O banco SQLite é criado automaticamente na primeira execução de qualquer
comando (`database.initialize_schema`), no caminho definido por
`DATABASE_PATH` em `hn_ingest/config.py`. O valor padrão é `hacker_news.db`
(caminho **relativo ao diretório a partir do qual `main.py` é executado**) e
pode ser sobrescrito com a variável de ambiente `HN_DATABASE_PATH`, por
exemplo:

```bash
HN_DATABASE_PATH=/caminho/absoluto/hacker_news.db python3 main.py initial-load
```

O arquivo `.db` já está listado no `.gitignore` e não deve ser versionado.

O banco contém três tabelas: `items` (campos estruturados do item — `id`,
`type`, `by`, `time`, `title`, `url`, `score`, `descendants`, `parent`,
`text`, `deleted`, `dead` — mais o JSON bruto original em `raw_json`),
`run_state` (par chave/valor, usado para o watermark `last_item_id`) e
`run_log` (histórico de execuções, consultado pelo comando `report`).

Outras constantes configuráveis via variável de ambiente (com fallback para
os valores padrão em `hn_ingest/config.py`): `HN_BASE_URL`,
`HN_REQUEST_TIMEOUT_SECONDS` (padrão `10`), `HN_MAX_RETRIES` (padrão `3`),
`HN_BACKOFF_BASE_SECONDS` (padrão `1`) e `HN_DEFAULT_INITIAL_LOAD_LIMIT`
(padrão `1000`).

## 6. Política de watermark e idempotência

O watermark (`last_item_id`, persistido na tabela `run_state`) representa o
maior ID já processado com sucesso de forma **contígua** a partir do início
do intervalo de uma execução. Ao processar um intervalo `start_id..end_id`:

- Cada ID é consultado individualmente na API. Um item `null` (removido ou
  inexistente) conta como "ignorado", sem interromper o processamento nem
  bloquear o avanço do watermark.
- Uma falha de rede/timeout, após esgotar as tentativas de retry com backoff
  exponencial, conta como "falha" para aquele ID **e passa a bloquear o
  avanço do watermark a partir dali**: mesmo que IDs posteriores no mesmo
  intervalo sejam processados com sucesso, o watermark avança apenas até o
  ID imediatamente anterior à primeira falha da sequência.
- O watermark só é persistido ao final do processamento completo do
  intervalo (nunca parcialmente), evitando estado inconsistente em caso de
  interrupção abrupta do processo.

Essa política garante idempotência: como o watermark nunca avança além de um
ID com falha não resolvida, uma reexecução (`incremental-load`) sempre
reprocessa a partir do ponto exato em que a execução anterior parou de
avançar — e como a persistência de itens usa `upsert` por `id` (chave
única), reprocessar um ID já salvo nunca cria duplicidade: o registro é
apenas atualizado (ou mantido, se não houver mudança).

Pela mesma razão, reexecutar `initial-load` depois que o watermark já foi
definido não processa nada (mensagem de "carga inicial já realizada"), e
reexecutar `incremental-load` sem que o `maxitem` tenha avançado além do
watermark não faz nenhuma chamada de item (mensagem de "nenhum item novo").

## 7. Limitações conhecidas

- **Execução única por vez**: a ferramenta foi projetada para não ser
  executada concorrentemente (duas instâncias em paralelo sobre o mesmo
  banco). O SQLite serializa escritas, mas o risco de condição de corrida em
  uso concorrente é aceito e documentado como limitação, dado o escopo do
  desafio.
- **Sem testes automatizados**: esta entrega não inclui suíte de testes
  (unitários, integração ou end-to-end).
- **Sem containerização**: não há `Dockerfile` nem `docker-compose`; a
  execução é feita diretamente com o interpretador Python local, em um
  ambiente virtual (`venv`).
- **Sem processamento de todo o histórico**: a carga inicial é
  deliberadamente limitada por `--limit`; não é objetivo deste utilitário
  baixar a totalidade do histórico do Hacker News.

## 8. Uso de IA generativa no desenvolvimento

Este projeto foi construído com apoio do Claude Code (Anthropic) ao longo de
todo o ciclo, de forma assistida e revisada pelo autor, não
autônoma/sem supervisão:

- Elaboração do [`PRD.md`](PRD.md) (escopo, requisitos, arquitetura em
  camadas e roadmap de sprints) a partir da descrição do desafio fornecida
  pelo autor.
- Estrutura inicial do repositório (`hn_ingest/`, `main.py`,
  `requirements.txt`, `.gitignore`).
- Implementação dos módulos de domínio, infraestrutura, aplicação e
  apresentação (`hn_ingest/domain`, `hn_ingest/infrastructure`,
  `hn_ingest/application`, `hn_ingest/presentation`), sprint a sprint,
  seguindo as decisões técnicas documentadas no PRD.
- Esta própria documentação final (README).
