import mysql.connector
from mysql.connector import Error

from backend.config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE
)


def get_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )


def test_connection():
    connection = None

    try:
        connection = get_connection()

        if connection.is_connected():
            return True

        return False

    except Error:
        return False

    finally:
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass


def execute_query(
    query,
    params=None,
    fetch=False,
    dictionary=True
):
    connection = None
    cursor = None

    try:
        connection = get_connection()

        cursor = connection.cursor(
            dictionary=dictionary
        )

        cursor.execute(
            query,
            params or ()
        )

        if fetch:
            result = cursor.fetchall()
            return result

        connection.commit()

        return cursor.lastrowid

    except Exception:
        if connection:
            connection.rollback()

        raise

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def execute_one(
    query,
    params=None
):
    connection = None
    cursor = None

    try:
        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            query,
            params or ()
        )

        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()