import logging

logger = logging.getLogger(__name__)


class BalanceService:
    def __init__(self, group_service, expense_service):
        self.group_service = group_service
        self.expense_service = expense_service

    def compute_balances(self, group_id):
        group = self.group_service.get_group(group_id)

        if not group:
            logger.error(f"Group {group_id} not found for balance calculation")
            raise ValueError(f"Group {group_id} not found")

        balances = {user_id: 0 for user_id in group.members}

        expenses = self.expense_service.list_expenses_for_group(group_id)

        for expense in expenses:
            paid_by = expense.paid_by
            amount = expense.amount
            splits = expense.splits

            if paid_by not in balances:

                raise RuntimeError(
                    f"Invalid DB state: payer {paid_by} not in group {group_id}"
                )

            for user_id, share in splits.items():
                if user_id not in balances:
                    raise RuntimeError(
                        f"Invalid DB state: user {user_id} not in group {group_id}"
                    )
                balances[user_id] -= share

            balances[paid_by] += amount

        logger.info(f"Balances computed for group {group_id}: {balances}")
        return balances

    def generate_settlement(self, group_id):

        balances = self.compute_balances(group_id)
        debtors = []
        creditors = []

        # Separate debtors and creditors
        for user_id, balance in balances.items():
            if balance < 0:
                debtors.append([user_id, -balance])  # owe money
            elif balance > 0:
                creditors.append([user_id, balance])  # to receive money

        # Sort to make settlements easier
        debtors.sort(key=lambda x: x[1])
        creditors.sort(key=lambda x: x[1], reverse=True)

        settlements = []

        i, j = 0, 0
        while i < len(debtors) and j < len(creditors):
            debtor_id, debt_amount = debtors[i]
            creditor_id, credit_amount = creditors[j]

            pay_amount = min(debt_amount, credit_amount)
            settlements.append((debtor_id, creditor_id, round(pay_amount, 2)))

            debtors[i][1] -= pay_amount
            creditors[j][1] -= pay_amount

            if debtors[i][1] == 0:
                i += 1
            if creditors[j][1] == 0:
                j += 1

        logger.info(f"Settlement suggestions for group {group_id}: {settlements}")
        return settlements

    def show_balances(self, group_name):
        group = self.group_service.get_group_by_name(group_name)
        if not group:
            raise ValueError("Group not found")

        return self.compute_balances(group.id)
