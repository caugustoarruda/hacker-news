# Diretório `.agents`

Este diretório descreve o fluxo de trabalho de implementação deste projeto de
forma **agnóstica a modelo/ferramenta de LLM**. Qualquer assistente de IA
(Claude, GPT, Gemini, ou outro) pode seguir estes documentos, na ordem
indicada, para implementar o que está especificado em `../PRD.md`, sem
depender de configurações específicas de uma ferramenta (ex.: subagentes de
uma CLI em particular, arquivos de configuração proprietários, etc.).

A fonte da verdade dos **requisitos** é sempre `../PRD.md`. Os arquivos deste
diretório traduzem esses requisitos em um **plano de execução por papéis
(agentes)**, cada um responsável por uma fatia vertical do trabalho.

## Como usar

1. Leia `../PRD.md` por completo antes de iniciar qualquer agente.
2. Leia `shared-conventions.md` — regras válidas para **todos** os agentes.
3. Execute os agentes na ordem da tabela abaixo. Cada agente parte do
   trabalho concluído pelo anterior e não deve reabrir escopo já fechado por
   um agente anterior, exceto para corrigir um defeito real.
4. Ao final de cada agente, confira os "Critérios de conclusão" do seu
   arquivo antes de prosseguir para o próximo.
5. Nenhum agente deve executar `git commit`, `git push` ou qualquer ação de
   versionamento — RNF12 exige revisão humana antes de qualquer commit.

## Ordem de execução

| Ordem | Agente                        | Arquivo                     | Corresponde a (PRD §10) |
|-------|-------------------------------|------------------------------|--------------------------|
| 1     | Agente de Domínio             | `domain-agent.md`            | Sprint 1                 |
| 2     | Agente de Infraestrutura      | `infrastructure-agent.md`    | Sprint 2                 |
| 3     | Agente de Aplicação           | `application-agent.md`       | Sprint 3                 |
| 4     | Agente de Apresentação (CLI)  | `presentation-agent.md`      | Sprint 4 — itens 4.1–4.3 |
| 5     | Agente de Documentação        | `documentation-agent.md`     | Sprint 4 — item 4.4      |
| 6     | Agente de QA / Validação      | `qa-agent.md`                | Sprint 4 — item 4.5      |

## Princípio geral

Cada agente é responsável por uma camada (ou fatia transversal, no caso de
documentação/QA) definida pela arquitetura do PRD (§7), respeitando a
separação de responsabilidades exigida por RNF05:

```
apresentação → aplicação → domínio ← infraestrutura
```

- Nenhum agente deve implementar responsabilidade de outra camada.
- Se um agente perceber a necessidade de algo fora do seu escopo, ele deve
  **documentar a dependência** (ex.: em comentário de handoff ou anotação
  pontual) e deixar para o agente responsável, em vez de implementar fora de
  ordem.
- Todos os agentes compartilham as mesmas convenções não-funcionais —
  descritas uma única vez em `shared-conventions.md` para evitar repetição.
