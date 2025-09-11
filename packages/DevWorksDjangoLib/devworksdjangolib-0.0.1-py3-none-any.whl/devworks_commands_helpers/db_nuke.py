import logging

from django.conf import settings
from django.db import connection
from psycopg2 import sql

log = logging.getLogger(__name__)


class NonTestableEnvException(Exception):
    pass


def delete_table(cursor, table_name):
    try:
        sql_raw_query = "DROP TABLE {table_name} CASCADE;"
        sql_object = sql.SQL(
            sql_raw_query
        ).format(
            table_name=sql.Identifier(table_name)
        )
        log.info("removing table {} data".format(table_name))
        cursor.execute(sql_object)
    except Exception as err:
        log.warning("cursor.execute() ERROR:", err)
        raise err


def nuke_db():
    if not settings.TESTABLE_ENV:
        raise NonTestableEnvException

    cursor = connection.cursor()
    try:
        cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        for table in cursor.fetchall():
            table_name, = table
            delete_table(cursor, table_name)
    except Exception as err:
        connection.rollback()
        cursor.close()
        log.warning("cursor.execute() get all table names ERROR:", err)
        raise err
    connection.commit()
    cursor.close()
