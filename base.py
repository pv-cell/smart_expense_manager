from abc import ABC, abstractmethod


class SplitStrategy(ABC):
    @abstractmethod
    def split(self, amount, user_ids):
        pass
