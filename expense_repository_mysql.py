import logging
from app.database import get_connection
from app.domain.models.expense import Expense

logger = logging.getLogger(__name__)


class ExpenseRepositoryMySQL:
    def __init__(self, conn):
        self.conn = conn

    def create_expense(self, expense):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO expenses (group_id, amount, paid_by, description, expense_date)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    expense.group_id,
                    expense.amount,
                    expense.paid_by,
                    expense.description,
                    expense.expense_date,
                ),
            )

            expense.id = cursor.lastrowid

            for user_id, share in expense.splits.items():
                cursor.execute(
                    """
                    INSERT INTO expense_splits (expense_id, user_id, amount)
                    VALUES (%s, %s, %s)
                    """,
                    (expense.id, user_id, share),
                )
            conn.commit()
            return expense.id
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to persist expense {expense.id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def list_expenses_for_group(self, group_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT 
                    e.id AS expense_id,
                    e.group_id,
                    e.amount,
                    e.paid_by,
                    e.description,
                    e.expense_date
                FROM expenses e
                JOIN `groups` g ON e.group_id = g.id
                JOIN users u ON e.paid_by = u.id
                WHERE e.group_id = %s
                ORDER BY e.id
                """,
                (group_id,),
            )
            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()

    def get_balances_by_group(self, group_id):
        cursor = self.conn.cursor(dictionary=True)

        query = """
        SELECT 
            u.name,
            SUM(
                CASE
                    WHEN e.paid_by = u.id THEN e.amount
                    ELSE - (e.amount / ec.user_count)
                END
            ) AS balance
        FROM expenses e
        JOIN users u ON u.id = e.paid_by
        JOIN (
            SELECT expense_id, COUNT(*) AS user_count
            FROM expense_users
            GROUP BY expense_id
        ) ec ON ec.expense_id = e.id
        WHERE e.group_id = %s
        GROUP BY u.name
        """

        cursor.execute(query, (group_id,))
        return cursor.fetchall()

    def get_expense_splits(self, expense_id):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, amount FROM expense_splits WHERE expense_id = %s",
            (expense_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        return {row["user_id"]: row["amount"] for row in rows}
