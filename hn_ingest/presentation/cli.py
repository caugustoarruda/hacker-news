"""Interface de linha de comando (CLI) do processo de ingestão do HN.

Traduz os comandos do usuário em chamadas aos casos de uso da camada de
aplicação e formata toda a saída em português brasileiro (RNF02). É a única
camada que conhece `argparse` e monta a árvore de dependências concretas
(conexão SQLite, repositórios e cliente HTTP).
"""

import argparse
import logging
import sys

from hn_ingest import config
from hn_ingest.application.dto import LoadResult, LoadStatus
from hn_ingest.application.incremental_load_use_case import (
    run_incremental_load,
)
from hn_ingest.application.initial_load_use_case import run_initial_load
from hn_ingest.application.report_use_case import (
    get_current_state,
    get_history,
    get_latest_summary,
)
from hn_ingest.domain.entities import RunSummary
from hn_ingest.domain.repositories import (
    ItemRepository,
    RunLogRepository,
    StateRepository,
)
from hn_ingest.infrastructure import database
from hn_ingest.infrastructure.http_client import HackerNewsClient
from hn_ingest.infrastructure.sqlite_item_repository import (
    SqliteItemRepository,
)
from hn_ingest.infrastructure.sqlite_run_log_repository import (
    SqliteRunLogRepository,
)
from hn_ingest.infrastructure.sqlite_state_repository import (
    SqliteStateRepository,
)

logger = logging.getLogger(__name__)

_ALREADY_INITIALIZED_MESSAGE = (
    'A carga inicial já foi realizada anteriormente. '
    'Utilize o comando \'incremental-load\' para buscar itens novos.'
)
_NOT_INITIALIZED_MESSAGE = (
    'A carga inicial ainda não foi realizada. '
    'Execute o comando \'initial-load\' antes de rodar a carga incremental.'
)
_NO_NEW_ITEMS_MESSAGE = (
    'Nenhum item novo para processar: o watermark já está atualizado em '
    'relação ao maior ID disponível na API.'
)
_UNEXPECTED_ERROR_MESSAGE = (
    'Ocorreu um erro inesperado durante a execução. '
    'Consulte os logs acima para mais detalhes.'
)


def configure_logging() -> None:
    """Configura o `logging` padrão da aplicação (nível INFO, com
    timestamp).
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )


def build_arg_parser() -> argparse.ArgumentParser:
    """Monta o parser da CLI com os três subcomandos suportados."""
    parser = argparse.ArgumentParser(
        prog='hn_ingest',
        description='Ingestão incremental de itens do Hacker News.',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    initial_parser = subparsers.add_parser(
        'initial-load', help='Executa a carga inicial limitada de itens.'
    )
    initial_parser.add_argument(
        '--limit',
        type=int,
        default=config.DEFAULT_INITIAL_LOAD_LIMIT,
        help=(
            'Quantidade de itens mais recentes a processar na carga '
            f'inicial (padrão: {config.DEFAULT_INITIAL_LOAD_LIMIT}).'
        ),
    )

    subparsers.add_parser(
        'incremental-load',
        help='Executa a carga incremental a partir do watermark salvo.',
    )

    report_parser = subparsers.add_parser(
        'report', help='Exibe o relatório de execuções.'
    )
    report_parser.add_argument(
        '--history',
        action='store_true',
        help=(
            'Exibe o histórico completo de execuções em vez de apenas a '
            'última.'
        ),
    )

    return parser


def format_summary(summary: RunSummary) -> str:
    """Formata um `RunSummary` em texto legível, em português brasileiro."""
    run_type_label = _run_type_label(summary.run_type)
    return (
        f'Tipo da carga: {run_type_label}\n'
        f'Faixa processada: {summary.range_start} a {summary.range_end}\n'
        f'Itens consultados: {summary.queried_count}\n'
        f'Itens inseridos: {summary.inserted_count}\n'
        f'Itens atualizados: {summary.updated_count}\n'
        f'Itens ignorados: {summary.skipped_count}\n'
        f'Itens com falha: {summary.failed_count}\n'
        f'Duração: {summary.duration_seconds:.2f} segundos\n'
        f'Concluída em: {summary.finished_at}'
    )


def format_history(summaries: list[RunSummary]) -> str:
    """Formata o histórico de execuções em uma tabela simples de texto."""
    if not summaries:
        return 'Nenhuma execução registrada ainda.'

    header = '{:<12}{:<23}{:>9}{:>8}{:>8}{:>8}{:>8}{:>12}  {}'.format(
        'Tipo', 'Faixa', 'Consult.', 'Inser.', 'Atual.', 'Ignor.',
        'Falhas', 'Duração(s)', 'Concluída em',
    )
    lines = [header, '-' * len(header)]
    for summary in summaries:
        run_type_label = _run_type_label(summary.run_type)
        range_label = f'{summary.range_start}-{summary.range_end}'
        lines.append(
            f'{run_type_label:<12}{range_label:<23}'
            f'{summary.queried_count:>9}{summary.inserted_count:>8}'
            f'{summary.updated_count:>8}{summary.skipped_count:>8}'
            f'{summary.failed_count:>8}{summary.duration_seconds:>12.2f}'
            f'  {summary.finished_at}'
        )
    return '\n'.join(lines)


def _run_type_label(run_type: str) -> str:
    return 'inicial' if run_type == 'initial' else 'incremental'


def handle_initial_load(
    limit: int,
    http_client: HackerNewsClient,
    item_repository: ItemRepository,
    state_repository: StateRepository,
    run_log_repository: RunLogRepository,
) -> None:
    """Executa o subcomando `initial-load` e imprime o resultado."""
    result = run_initial_load(
        limit=limit,
        http_client=http_client,
        item_repository=item_repository,
        state_repository=state_repository,
        run_log_repository=run_log_repository,
    )
    if result.status == LoadStatus.ALREADY_INITIALIZED:
        print(_ALREADY_INITIALIZED_MESSAGE)
        return

    print('Carga inicial concluída com sucesso.')
    print(format_summary(result.summary))


def handle_incremental_load(
    http_client: HackerNewsClient,
    item_repository: ItemRepository,
    state_repository: StateRepository,
    run_log_repository: RunLogRepository,
) -> None:
    """Executa o subcomando `incremental-load` e imprime o resultado."""
    result: LoadResult = run_incremental_load(
        http_client=http_client,
        item_repository=item_repository,
        state_repository=state_repository,
        run_log_repository=run_log_repository,
    )
    if result.status == LoadStatus.NOT_INITIALIZED:
        print(_NOT_INITIALIZED_MESSAGE)
        return
    if result.status == LoadStatus.NO_NEW_ITEMS:
        print(_NO_NEW_ITEMS_MESSAGE)
        return

    print('Carga incremental concluída com sucesso.')
    print(format_summary(result.summary))


def handle_report(
    show_history: bool,
    state_repository: StateRepository,
    run_log_repository: RunLogRepository,
) -> None:
    """Executa o subcomando `report` e imprime o resultado."""
    watermark = get_current_state(state_repository)
    watermark_label = (
        str(watermark)
        if watermark is not None
        else 'nenhum (carga inicial ainda não realizada)'
    )
    print(f'Watermark atual (último ID processado): {watermark_label}')
    print()

    if show_history:
        summaries = get_history(run_log_repository)
        print(format_history(summaries))
        return

    latest = get_latest_summary(run_log_repository)
    if latest is None:
        print('Nenhuma execução registrada ainda.')
        return
    print(format_summary(latest))


def main() -> None:
    """Ponto de entrada da CLI.

    Faz o parsing dos argumentos, monta as dependências concretas, executa o
    comando solicitado e garante que qualquer erro não tratado resulte em
    mensagem amigável e código de saída diferente de zero.
    """
    configure_logging()
    parser = build_arg_parser()
    args = parser.parse_args()

    connection = None
    try:
        connection = database.get_connection()
        database.initialize_schema(connection)

        http_client = HackerNewsClient()
        item_repository = SqliteItemRepository(connection)
        state_repository = SqliteStateRepository(connection)
        run_log_repository = SqliteRunLogRepository(connection)

        if args.command == 'initial-load':
            handle_initial_load(
                args.limit,
                http_client,
                item_repository,
                state_repository,
                run_log_repository,
            )
        elif args.command == 'incremental-load':
            handle_incremental_load(
                http_client,
                item_repository,
                state_repository,
                run_log_repository,
            )
        elif args.command == 'report':
            handle_report(args.history, state_repository, run_log_repository)
    except Exception as error:
        logger.error('Falha não tratada durante a execução da CLI: %s', error)
        print(_UNEXPECTED_ERROR_MESSAGE, file=sys.stderr)
        sys.exit(1)
    finally:
        if connection is not None:
            connection.close()
