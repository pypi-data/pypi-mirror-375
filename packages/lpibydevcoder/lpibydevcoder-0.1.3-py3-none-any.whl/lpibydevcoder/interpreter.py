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
            raise Exception(f"Variable '{node.value}' is not defined")
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
    else:
        raise Exception(f"Unknown node type: {node.type}")








