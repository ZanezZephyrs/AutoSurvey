from abc import ABC, abstractmethod
class LLMInference(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def complete(self, messages):
        pass

    def messages_to_plain_text(self, messages, prefix=""):
        plain_text=prefix
        for message in messages:
            plain_text+=message["role"]+ ":"
            plain_text+=message["content"]+"\n"
        return plain_text