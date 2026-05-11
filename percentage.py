from .base import SplitStrategy


class PercentageSplitStrategy(SplitStrategy):
    def split(self, amount, percentages):
        if not percentages:
            raise ValueError("No percentages provided")

        total_percentage = sum(percentages.values())
        if total_percentage != 100:
            raise ValueError("Percentages must sum to 100")

        splits = {}
        for user_id, percent in percentages.items():
            splits[user_id] = round(amount * percent / 100, 2)

        return splits
