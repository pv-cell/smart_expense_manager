from .base import SplitStrategy


class CustomSplitStrategy(SplitStrategy):
    def split(self, amount, splits):
        if not splits:
            raise ValueError("No splits provided")

        total = round(sum(splits.values()), 2)
        if total != round(amount, 2):
            raise ValueError(
                f"Custom splits ({total}) do not sum to total amount ({amount})"
            )

        return splits
