# Convenções compartilhadas entre agentes

Regras não-funcionais do PRD (`../PRD.md`, seção 6) que valem para **todos**
os agentes, independentemente da camada em que atuam. Nenhum agente deve
duplicar esta seção em seu próprio arquivo — apenas referenciá-la.

## Linguagem

- **RNF01**: identificadores de código (nomes de módulos, classes, funções,
  variáveis) sempre em **inglês**.
- **RNF02**: toda saída visível ao usuário (mensagens de log, resumo de
  execução, relatório, README) sempre em **português brasileiro**.
- Docstrings de classes e funções públicas: em português brasileiro,
  explicando apenas o que não é óbvio a partir do nome (evitar redundância).

## Estilo de código

- **RNF03**: aspas simples (`'...'`) de forma consistente em todo o código
  Python.
- **RNF04**: aderência ao PEP 8 (nomes, espaçamento, imports, comprimento de
  linha).
- **RNF13**: simplicidade — não introduzir abstrações, camadas, parâmetros ou
  tratamentos além do estritamente necessário para atender ao PRD. Preferir
  código explícito e direto a generalizações especulativas.

## Arquitetura

- **RNF05**: manter a separação em camadas definida em `../PRD.md` §7:
  `domain/`, `infrastructure/`, `application/`, `presentation/`. O sentido de
  dependência é sempre apresentação → aplicação → domínio, com infraestrutura
  implementando os contratos (interfaces) definidos no domínio. O domínio
  nunca importa de infraestrutura, aplicação ou apresentação.
- **RNF06**: o único banco de dados permitido é **SQLite**, via módulo
  `sqlite3` da biblioteca padrão — nenhuma dependência externa de banco de
  dados.

## Escopo negativo (o que não fazer nesta entrega)

- **RNF07**: não criar testes automatizados.
- **RNF08**: não criar containerização (Docker ou similar).
- Não adicionar funcionalidades, endpoints, comandos ou parâmetros que não
  estejam descritos no PRD, mesmo que pareçam úteis.

## Confiabilidade e operação

- **RNF09**: qualquer reexecução (total ou parcial) deve ser idempotente —
  nunca duplicar registros na tabela `items`.
- **RNF10**: timeout de requisição HTTP deve ser configurável, com valor
  padrão razoável.
- **RNF11**: logs estruturados (nível, timestamp, mensagem) via módulo
  `logging` padrão do Python — nenhuma biblioteca de logging externa.

## Controle de versão

- **RNF12**: nenhum agente deve executar `git commit`, `git push` ou qualquer
  ação de versionamento. Toda alteração aguarda revisão humana explícita.

## Definição de pronto comum a todos os agentes

Um agente só deve considerar sua etapa concluída quando, cumulativamente:

1. Todas as subtarefas do PRD (§10) correspondentes ao seu escopo estiverem
   implementadas.
2. O código não introduzir dependência de camadas que ainda serão
   implementadas por agentes futuros na ordem de execução.
3. Todas as regras desta página forem respeitadas.
4. Nenhum commit tiver sido criado.
5. O "Handoff" descrito no arquivo do agente estiver satisfeito, permitindo
   que o próximo agente da sequência comece sem ambiguidade.
