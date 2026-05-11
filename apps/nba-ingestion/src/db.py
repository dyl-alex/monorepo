from contextlib import contextmanager
import psycopg
from config import get_settings


@contextmanager
def get_connection():
    settings = get_settings()

    with psycopg.connect(settings.database_url) as conn:
        yield conn