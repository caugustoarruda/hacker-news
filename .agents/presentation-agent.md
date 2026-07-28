# Agente de Apresentação (CLI)

> Antes de começar, leia `../PRD.md`, `shared-conventions.md` e o resultado
> de `application-agent.md`.

## Papel

Traduzir comandos do usuário em chamadas aos casos de uso e formatar toda a
saída em português brasileiro (RNF02). É a única camada que conhece
`argparse` e monta a árvore de dependências concretas (conexão SQLite,
repositórios, cliente HTTP).

## Objetivo

Entregar uma CLI funcional com os três comandos exigidos
(`initial-load`, `incremental-load`, `report`), com composição de
dependências centralizada e saída legível em português.

## Pré-requisitos

- `application-agent.md` concluído: os quatro casos de uso disponíveis e
  funcionando.

## Escopo (PRD §10, Sprint 4 — itens 4.1 a 4.3)

### 4.1. Interface de linha de comando (`presentation/cli.py`)
- `argparse` com subcomandos: `initial-load`, `incremental-load`, `report`.
- `--limit` (inteiro, opcional, padrão `DEFAULT_INITIAL_LOAD_LIMIT`) em
  `initial-load`.
- `--history` (opcional) em `report`, para exibir todo o histórico em vez
  de apenas a última execução.
- Montagem das dependências (conexão SQLite via `database.get_connection` +
  `initialize_schema`, repositórios concretos, `HackerNewsClient`) e
  injeção nos casos de uso, a partir de `main.py`/`cli.py`.
- Configurar `logging` básico (nível `INFO`, formato com timestamp) no
  início da execução da CLI.

### 4.2. Formatação de saída em português brasileiro
- Função de formatação do `RunSummary` em texto legível: faixa processada,
  consultados, inseridos, atualizados, ignorados, falhas, duração.
- Mensagens específicas para os casos de borda: carga inicial já realizada,
  nenhum item novo no incremental, carga inicial ainda não realizada ao
  tentar incremental.
- Formatação do histórico de execuções para `report --history` (tabela
  simples em texto).
- Código de saída (`exit code`) diferente de zero em erro não tratado, com
  mensagem amigável em português — nunca vazar stack trace bruta ao
  usuário final.

### 4.3. Revisão de padronização do código
- Aspas simples de forma consistente em todo o projeto (não só nesta
  camada — revisão de todo o código escrito pelos agentes anteriores).
- Aderência ao PEP 8 em todo o projeto.
- Todo identificador em inglês; toda saída ao usuário em português
  brasileiro, em todo o projeto.
- Docstrings de classes e funções públicas em português brasileiro,
  explicando apenas o não óbvio.

## Não-objetivos

- Não implementar regra de negócio nova (cálculo de intervalo, watermark,
  contadores) — apenas consumir o que os casos de uso já retornam.
- Não acessar `sqlite3` ou `requests` diretamente fora da composição de
  dependências em `cli.py`.

## Critérios de conclusão

1. Os três comandos funcionam de ponta a ponta contra um banco SQLite
   real.
2. Toda mensagem impressa ao usuário está em português brasileiro.
3. Erros não tratados resultam em exit code != 0 com mensagem amigável.
4. Revisão de padronização (4.3) aplicada a **todo** o código-fonte do
   projeto, não apenas à camada de apresentação.

## Handoff

Ao final, o projeto deve ser executável via `python main.py <comando>
[opções]`, pronto para o Agente de Documentação escrever o README com
exemplos reais de uso, e para o Agente de QA validar manualmente os
critérios de aceite do PRD §8.
