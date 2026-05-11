from .base import SplitStrategy


class EqualSplitStrategy(SplitStrategy):
    def split(self, amount, user_ids):
        if not user_ids:
            raise ValueError("No user to split the amount")
        share = round(amount / len(user_ids), 2)
        splits = {user_id: share for user_id in user_ids}

        total_assigned = sum(splits.values())
        difference = round(amount - total_assigned, 2)
        if difference != 0:
            last_user = user_ids[-1]
            splits[last_user] += difference

        return splits
