import re

token_specs = [
    ("NUMBER", r"\d+"),
    ("PR", r"pr"),
    ("IND", r"ind"),
    ("ST", r"st"),
    ("SR", r"sr"),
    ("SQUARE", r"square"),
    ("SQ", r"nosq"),
    ("DEF", r"def"),
    ("ID", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("WHITESPACE", r"\s+"),
    ("STRING", r'"[^"]*"'),
    ("COLON", r":"),
    ("DEV", r"!"),
    ("COMMA", r","),
    ("RAV", r"="),
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
            raise SyntaxError(f"Unknown symbol: {code[0]}")
    return tokens

