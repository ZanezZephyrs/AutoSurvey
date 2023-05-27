from abc import ABC, abstractmethod
class Filter(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def filter_sm(self, query: str):
        pass

    