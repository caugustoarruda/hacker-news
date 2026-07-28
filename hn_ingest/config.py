"""Configuração centralizada do projeto.

Todas as constantes podem ser sobrescritas por variáveis de ambiente,
mantendo o valor padrão como fallback.
"""

import os

BASE_URL = os.environ.get(
    'HN_BASE_URL', 'https://hacker-news.firebaseio.com/v0/'
)

REQUEST_TIMEOUT_SECONDS = float(
    os.environ.get('HN_REQUEST_TIMEOUT_SECONDS', '10')
)

MAX_RETRIES = int(os.environ.get('HN_MAX_RETRIES', '3'))

BACKOFF_BASE_SECONDS = float(
    os.environ.get('HN_BACKOFF_BASE_SECONDS', '1')
)

DEFAULT_INITIAL_LOAD_LIMIT = int(
    os.environ.get('HN_DEFAULT_INITIAL_LOAD_LIMIT', '1000')
)

DATABASE_PATH = os.environ.get('HN_DATABASE_PATH', 'hacker_news.db')
