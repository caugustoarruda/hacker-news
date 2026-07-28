# Agente de Documentação

> Antes de começar, leia `../PRD.md`, `shared-conventions.md` e confirme que
> `presentation-agent.md` foi concluído (a CLI precisa estar funcional para
> documentar exemplos reais).

## Papel

Escrever o `README.md` do projeto, em português brasileiro, explicando como
qualquer pessoa (humana ou outro agente de IA) pode instalar, executar e
entender o comportamento do sistema sem precisar ler o PRD inteiro.

## Objetivo

Entregar um README completo, correto e testável — os comandos documentados
devem poder ser copiados e colados com sucesso contra o código já
implementado.

## Pré-requisitos

- `presentation-agent.md` concluído: os três comandos da CLI funcionando.

## Escopo (PRD §10, item 4.4)

- **4.4.1.** Visão geral do projeto e requisitos (Python 3.11+, `pip
  install -r requirements.txt`).
- **4.4.2.** Instruções de execução da carga inicial (exemplo de comando
  com `--limit`).
- **4.4.3.** Instruções de execução da carga incremental (exemplo de
  comando).
- **4.4.4.** Instruções de execução do relatório (última execução e
  histórico via `--history`).
- **4.4.5.** Estrutura de camadas do projeto e localização do arquivo
  SQLite gerado.
- **4.4.6.** Política de watermark (avanço apenas até o maior ID contíguo
  sem falha) e comportamento de idempotência.
- **4.4.7.** Limitações conhecidas: execução única por vez (sem
  concorrência), sem testes automatizados, sem containerização — conforme
  escopo do desafio (PRD §9).

## Não-objetivos

- Não alterar código de produção para "fazer a documentação funcionar" —
  qualquer divergência encontrada entre o comportamento real e o PRD deve
  ser sinalizada, não silenciosamente corrigida via mudança de escopo.
- Não copiar trechos inteiros do PRD; o README é um guia prático de uso, o
  PRD é a especificação completa.

## Critérios de conclusão

1. Cada comando de exemplo no README foi de fato executado contra o
   projeto e produziu a saída esperada.
2. As sete subseções listadas acima estão presentes.
3. README inteiramente em português brasileiro (RNF02).

## Handoff

Ao final, o Agente de QA deve poder seguir o README do zero (banco de dados
limpo) para validar os critérios de aceite do PRD §8.
