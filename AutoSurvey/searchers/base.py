from abc import ABC, abstractmethod
class Searcher(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def search(self, query: str):
        pass    