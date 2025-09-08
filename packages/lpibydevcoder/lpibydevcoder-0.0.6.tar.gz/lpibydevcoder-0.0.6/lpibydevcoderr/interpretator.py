def evaluate(node):
    if node.type == "NUMBER":
        return node.value
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
    elif node.type == "IND":
        return input()
    elif node.type == "ST":
        style = evaluate(node.left)
        print(f"Подключён стиль: {style}")
    elif node.type == "Sr":
        value = evaluate(node.left)
        return str(value)
    elif node.type == "STRING":
        return node.value
    elif node.type == "COLON":
        return ":"
    elif node.type == "FUNC_DEF":
        functions[node.value] = node.left
    elif node.type == "FUNC_CALL":
        if node.value in functions:
            return evaluate(functions[node.value])
        else:
            raise Exception(f"Функция {node.value} не найдена")
    elif node.type == "TRY_FUNC":
        try:
            return evaluate(node.left)
        except Exception:
            return evaluate(node.right)

def run_code(code):
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    return evaluate(ast)

# Пример использования
if __name__ == "__main__":
    run_code("pr(3 + 5 - 2)")
    user_input = run_code("ind()")
    run_code(f"pr({user_input})")
    run_code('st(1)')                 # Подключён стиль: 1
    print(run_code("sr(123)"))       # '123'
    run_code("pr(sr(456 + 8))")      # '464'
    run_code('pr(sr("Hello World!"))') # 'Hello World!'
    run_code("pr(2 * 3 + 4 / 2 - 1)")  # 7.0
    run_code('!(pr(1 / 0), pr("Ошибка!"))')  # Функция ! - try: , expect.
