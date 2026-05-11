from datetime import date


class Expense:
    def __init__(
        self, expense_id, group_id, amount, paid_by, splits, description, expense_date
    ):
        self.id = expense_id
        self.group_id = group_id
        self.amount = amount
        self.paid_by = paid_by
        self.splits = splits
        self.description = description
        self.expense_date = expense_date

    def __repr__(self):
        return (
            f"Expense(id={self.id}, amount={self.amount},"
            f"paid_by={self.paid_by}, splits={self.splits})"
        )
