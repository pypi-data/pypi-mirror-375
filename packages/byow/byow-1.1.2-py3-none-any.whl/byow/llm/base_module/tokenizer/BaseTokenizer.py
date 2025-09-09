from abc import ABC, abstractmethod

class BaseTokenizer(ABC):
    @abstractmethod
    def encode(self, text: str) -> list[int]:
        """Convert text into list of token IDs"""
        pass

    @abstractmethod
    def decode(self, tokens: list[int]) -> str:
        """Convert list of token IDs back to text"""
        pass