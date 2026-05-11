from .equal import EqualSplitStrategy
from .custom import CustomSplitStrategy
from .percentage import PercentageSplitStrategy


class SplitStrategyFactory:
    @staticmethod
    def get(strategy_type):
        strategy_type = strategy_type.lower()
        if strategy_type == "equal":
            return EqualSplitStrategy()
        elif strategy_type == "custom":
            return CustomSplitStrategy()
        elif strategy_type == "percentage":
            return PercentageSplitStrategy()
        else:
            raise ValueError(f"unknown split strategy: {strategy_type}")

    @staticmethod
    def get_strategy(strategy_type):
        return SplitStrategyFactory.get(strategy_type)
