import re
functions = {}
# Лексер
token_specs = [
    ("NUMBER", r"\d+"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("PR", r"pr"),
    ("IND", r"ind"),
    ("ST", r"st"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("WHITESPACE", r"\s+"),
    ("Sr", r"sr"),
    ("STRING", r'"[^"]*"'),
    ("COLON", r":"),
    ("DEF", r"def"),
    ("ID", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("Dev", r"!"),
    ("COMMA", r","),

]

def tokenize(code):
    tokens = []
    while code:
        for name, pattern in token_specs:
            match = re.match(pattern, code)
            if match:
                value = match.group(0)
                if name != "WHITESPACE":
                    tokens.append((name, value))
                code = code[len(value):]
                break
        else:
            raise SyntaxError(f"Неизвестный символ: {code[0]}")
    return tokens

# AST узел
class Node:
    def __init__(self, type, value=None, left=None, right=None):
        self.type = type
        self.value = value
        self.left = left
        self.right = right