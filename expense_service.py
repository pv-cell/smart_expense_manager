import asyncio
import logging
from datetime import date
from app.domain.models.expense import Expense
from app.domain.splits.factory import SplitStrategyFactory

logger = logging.getLogger(__name__)


class ExpenseService:
    def __init__(self, repo):
        self.repo = repo

    def add_expense(
        self,
        group_id,
        amount,
        paid_by,
        user_ids,
        split_type,
        custom_splits=None,
        description=None,
        expense_date=None,
    ):
        if expense_date is None:
            expense_date = date.today()

        if amount <= 0:
            raise ValueError("Expense amount must be greater than zero")

        if paid_by not in user_ids:
            raise ValueError("Paid-by user must be included in expense users")

        if len(user_ids) != len(set(user_ids)):
            raise ValueError("Duplicate users are not allowed")

        logger.info(f"Adding expense to group {group_id}")

        split_type = split_type.lower()
        strategy = SplitStrategyFactory.get_strategy(split_type)

        # if split_type == "equal":
        #     splits = strategy.split(amount, user_ids)

        # elif split_type in ("custom", "percentage"):
        #     if not custom_splits:
        #         raise ValueError(f"{split_type} splits required")
        #     splits = strategy.split(amount, custom_splits)

        # else:
        #     raise ValueError(f"Unknown split type: {split_type}")
        # -------- SPLIT HANDLING (MIDDLE) --------
        if split_type == "equal":
            splits = strategy.split(amount, user_ids)

            if round(sum(splits.values()), 2) != round(amount, 2):
                raise ValueError("Equal split calculation error")

        elif split_type == "custom":
            if not custom_splits:
                raise ValueError("Custom splits required")

            if sum(custom_splits.values()) != amount:
                raise ValueError("Custom split amounts must sum to total expense")

            if split_type in ("custom", "percentage"):
                if not isinstance(custom_splits, dict):
                    raise ValueError("custom_splits must be a dict")

                for user_id, value in custom_splits.items():
                    if not isinstance(value, (int, float)):
                        raise ValueError("Split values must be numbers")
                    if value <= 0:
                        raise ValueError("Split values must be > 0")

            splits = strategy.split(amount, custom_splits)

        elif split_type == "percentage":
            if not custom_splits:
                raise ValueError("Percentage splits required")

            if sum(custom_splits.values()) != 100:
                raise ValueError("Percentage splits must sum to 100")

            for uid, pct in custom_splits.items():
                if pct <= 0 or pct > 100:
                    raise ValueError("Percentage values must be between 1 and 100")

            splits = strategy.split(amount, custom_splits)

        expense = Expense(
            expense_id=None,
            group_id=group_id,
            amount=amount,
            paid_by=paid_by,
            splits=splits,
            description=description,
            expense_date=expense_date,
        )
        try:
            expense_id = self.repo.create_expense(expense)
            expense.id = expense_id

            logger.info(f"Expense persisted with ID {expense_id}")
            asyncio.create_task(self._notify_users(expense))
            return expense
        except Exception as e:
            logger.error(f"Expense creation failed: {e}")
            raise

    def get_expense(self, expense_id):

        row = self.repo.get_expense(expense_id)
        if not row:
            return None

        splits = self.repo.get_expense_splits(expense_id)

        expense = Expense(
            expense_id=row["id"],
            group_id=row["group_id"],
            amount=row["amount"],
            paid_by=row["paid_by"],
            splits=splits,
            description=row["description"],
            expense_date=row["expense_date"],
        )

        return expense

    def list_expenses_for_group(self, group_id):
        rows = self.repo.list_expenses_for_group(group_id)
        expenses = []

        for row in rows:
            expense_id = row["expense_id"]

            splits = self.repo.get_expense_splits(expense_id)

            expense = Expense(
                expense_id=row["expense_id"],
                group_id=row["group_id"],
                amount=row["amount"],
                paid_by=row["paid_by"],
                splits=splits,
                description=row["description"],
                expense_date=row["expense_date"],
            )

            expenses.append(expense)

        return expenses

    async def _notify_users(self, expense):
        await asyncio.sleep(0)
        logger.info(
            f"[ASYNC NOTIFICATION] Users notified for new expense "
            f"(ID={expense.id}, amount={expense.amount})"
        )
