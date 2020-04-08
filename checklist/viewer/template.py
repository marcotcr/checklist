from typing import List, Tuple
from .token import Token

class Template(object):
    def __init__(self, target: str, tokens: List[Token]):
        self.tokens = tokens
        self.target = target
    
    def __repr__(self):
        return f"[{self.target}] {self.tokens}"
    
    def get_to_fill_pieces(self, token_idx: int) -> Tuple[str, str]:
        piece1 =  " ".join([t.default for t in self.tokens[:token_idx]])
        piece2 =  " ".join([t.default for t in self.tokens[token_idx+1:]])
        return piece1, piece2
    
    def serialize(self):
        return {
            "tokens": [t.serialize() for t in self.tokens],
            "target": self.target
        }