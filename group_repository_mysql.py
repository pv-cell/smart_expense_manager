import logging
from app.database import get_connection
from mysql.connector import Error

logger = logging.getLogger(__name__)


class GroupRepositoryMySQL:

    def __init__(self, conn):
        self.conn = conn

    def create_group(self, group):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO `groups` (name) VALUES (%s)", (group.name,))
            conn.commit()
            group.id = cursor.lastrowid
            logger.info(f"Group persisted in MySQL: {group.name} (ID={group.id})")
            return group.id
        except Exception as e:
            logger.error(f"Failed to create group {group.name}: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def get_group(self, group_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT id,name FROM `groups` WHERE id =%s", (group_id,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"Failed to fetch group {group_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def add_user_to_group(self, group_id, user_id):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
                (group_id, user_id),
            )
            conn.commit()
            logger.info(f"User {user_id} added to group {group_id} in DB")
        except Exception as e:
            logger.error(f"Failed to add user {user_id} to group {group_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def remove_user_from_group(self, group_id, user_id):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, user_id),
            )
            conn.commit()
            logger.info(f"User {user_id} removed from group {group_id} in DB")
        except Exception as e:
            logger.error(f"Failed to remove user {user_id} from group {group_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_group_members(self, group_id):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT user_id FROM group_members WHERE group_id = %s", (group_id,)
            )
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch members for group {group_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def list_groups(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT id, name FROM `groups`")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def list_group_members(self, group_id):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT u.id, u.name
            FROM users u
            JOIN group_members gm ON gm.user_id = u.id
            WHERE gm.group_id = %s
            ORDER BY u.id
        """,
            (group_id,),
        )
        return cursor.fetchall()

    def get_group_by_name(self, name):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT id, name FROM `groups` WHERE name = %s", (name,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
