from .BaseTokenizer import BaseTokenizer
import tiktoken

class TikTokenTokenizer(BaseTokenizer):
    def __init__(self, encoding_name: str = "gpt2"):
        self.encoding = tiktoken.get_encoding(encoding_name)

    def encode(self, text: str , special_characters ={"<|endoftext|>"} ) -> list[int]:
        return self.encoding.encode(text, allowed_special=special_characters)

    def decode(self, tokens: list[int]) -> str:
        return self.encoding.decode(tokens)
