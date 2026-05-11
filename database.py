import logging
import mysql.connector
from mysql.connector import Error

logger = logging.getLogger(__name__)


def get_connection():
    try:
        connection = mysql.connector.connect(
            host="mysql",
            user="appuser",
            password="apppassword",
            database="expense_manager",
            port=3306,
        )
        logger.info("Successfully connected to MySQL")
        return connection
    except Error as e:
        logger.error(f"Error connecting to MYSql: {e}")
        raise
