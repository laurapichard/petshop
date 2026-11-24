import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "dbname=petshop_amigo_fiel user=postgres password=postgres host=localhost",
)


def _conectar():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


@contextmanager
def transaction():
    """Abre uma transação: commit ao sair com sucesso, rollback em erro."""
    conn = _conectar()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def run(sql, params=None, one=False):
    """Executa uma instrução. Retorna linhas quando houver resultado (SELECT/RETURNING)."""
    with transaction() as cur:
        cur.execute(sql, params)
        if cur.description is None:
            return None
        return cur.fetchone() if one else cur.fetchall()
