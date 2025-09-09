from .parser import Parser
from .lexer import tokenize

functions = {}
variables = {}

def evaluate(node):
    if node.type == "NUMBER":
        return node.value
    elif node.type == "ASSIGN":
        value = evaluate(node.right)
        variables[node.value] = value
        return value
    elif node.type == "ID":
        if node.value in variables:
            return variables[node.value]
        else:
            raise Exception(f"Переменная {node.value} не определена")
    elif node.type == "PLUS":
        return evaluate(node.left) + evaluate(node.right)
    elif node.type == "MINUS":
        return evaluate(node.left) - evaluate(node.right)
    elif node.type == "MUL":
        return evaluate(node.left) * evaluate(node.right)
    elif node.type == "DIV":
        return evaluate(node.left) / evaluate(node.right)
    elif node.type == "PR":
        value = evaluate(node.left)
        print(value)
        return value
    elif node.type == "IND":
        return input()
    elif node.type == "SR":
        value = evaluate(node.left)
        return str(value)
    elif node.type == "STRING":
        return node.value
    elif node.type == "TRY_FUNC":
        try:
            return evaluate(node.left)
        except Exception:
            return evaluate(node.right)
    else:
        raise Exception(f"Неизвестный тип узла: {node.type}")

class ParserExtended(Parser):
    def parse_all(self):
        nodes = []
        while self.pos < len(self.tokens):
            node = self.assignment()
            nodes.append(node)
        return nodes

def run_code(code):
    try:
        tokens = tokenize(code)
        parser = ParserExtended(tokens)
        ast_nodes = parser.parse_all()
        result = None
        for node in ast_nodes:
            result = evaluate(node)
        return result
    except Exception as e:
        print("Ошибка:", e)
        return None




