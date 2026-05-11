import logging
from app.database import get_connection
from app.domain.models.user import User
from mysql.connector import Error

logger = logging.getLogger(__name__)


class UserRepositoryMySQL:
    def __init__(self):
        pass

    def create_user(self, user: User):
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = "INSERT INTO users (name) VALUES (%s)"
            cursor.execute(query, (user.name,))
            conn.commit()

            user_id = cursor.lastrowid
            user.id = user_id

            logger.info(f"User inserted into MySQL: {user.name} (ID {user.id})")
            return user_id

        except Error as e:
            logger.error(f"Failed to insert user {user.name}: {e}")
            if conn:
                conn.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_user(self, user_id):
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE id=%s"
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            if row:
                user = User(row["id"], row["name"])
                logger.info(f"Fetched user from MySQL: {user.name} (ID {user.id})")
                return user
            else:
                logger.warning(f"User ID {user_id} not found in MySQL")
                return None
        except Error as e:
            logger.error(f"Failed to fetch user {user_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def list_users(self):
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM users"
            cursor.execute(query)
            rows = cursor.fetchall()
            users = [User(row["id"], row["name"]) for row in rows]
            logger.info(f"Fetched all users from MySQL, count: {len(users)}")
            return users
        except Error as e:
            logger.error(f"Failed to list users: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_user_by_name(self, name):
        users = self.list_users()
        for user in users:
            if user.name == name:
                return user
        return None
