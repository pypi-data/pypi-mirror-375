"""
ChatGPT did not unfortunately succeed
"""

import ast
import hashlib


def normalize_expression(node):
    """ Normalize expressions to make some commutative operations consistent. """
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mult)):
        left_hash = hash_ast(node.left)
        right_hash = hash_ast(node.right)
        if left_hash > right_hash:
            node.left, node.right = node.right, node.left  # Swap to maintain order
    return node


def hash_ast(node):
    """ Hash an AST node into a digest that uniquely represents its structure and contents. """
    hasher = hashlib.sha256()

    def hash_node(n):
        if isinstance(n, ast.AST):
            hasher.update(type(n).__name__.encode('utf-8'))
            for field, value in ast.iter_fields(n):
                if field == 'ctx':
                    continue  # Ignore context field
                hasher.update(field.encode('utf-8'))
                hash_node(value)
        elif isinstance(n, list):
            for item in n:
                hash_node(item)
        else:
            hasher.update(str(n).encode('utf-8'))
    hash_node(node)
    return hasher.hexdigest()


def find_common_subexpressions(formulas):
    subexpressions = {}
    for i, formula in enumerate(formulas):
        tree = ast.parse(formula, mode='eval')
        normalize_expression(tree.body)  # Normalize the entire expression tree
        for node in ast.walk(tree):
            if not isinstance(node, ast.Name):  # Focus on composite nodes
                node_hash = hash_ast(node)
                if node_hash in subexpressions:
                    subexpressions[node_hash].append((i, ast.unparse(node)))
                else:
                    subexpressions[node_hash] = [(i, ast.unparse(node))]
    return subexpressions


"""
# Find common subexpressions
common_subexpressions = find_common_subexpressions(formulas)
for h, occurrences in common_subexpressions.items():
    if len(occurrences) > 1:
        print(f"Common subexpression found in: {occurrences}")
"""
