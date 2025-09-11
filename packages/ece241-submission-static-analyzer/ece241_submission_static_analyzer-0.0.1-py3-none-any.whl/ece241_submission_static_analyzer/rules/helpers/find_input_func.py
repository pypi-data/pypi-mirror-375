from ece241_submission_static_analyzer.rules.helpers.ast_helper import ASTWithChildren
from typing import Optional
import ast


def find_input_func(node: ASTWithChildren, is_inside_main: bool) -> list[ASTWithChildren]:
    """Recursively find all input function calls in the AST.

    Args:
        node (ASTWithChildren): The AST node to search.

    Returns:
        list[str]: A list of function names found in the AST.
    """
    input_func_calls = []
    if isinstance(node.node, ast.Call):
        if isinstance(node.node.func, ast.Name) and node.node.func.id == "input":
            if not is_inside_main:
                input_func_calls.append(node)
        elif isinstance(node.node.func, ast.Attribute) and node.node.func.attr == "input":
            if not is_inside_main:
                input_func_calls.append(node)
    if isinstance(node.node, ast.Expr):
        if isinstance(node.node.value, ast.Call):
            if isinstance(node.node.value.func, ast.Name) and node.node.value.func.id == "input":
                if not is_inside_main:
                    input_func_calls.append(node)
            elif isinstance(node.node.value.func, ast.Attribute) and node.node.value.func.attr == "input":
                if not is_inside_main:
                    input_func_calls.append(node)
    if isinstance(node.node, ast.If):
        if (isinstance(node.node.test, ast.Compare) and
                isinstance(node.node.test.left, ast.Name) and
                node.node.test.left.id == "__name__" and
                any(isinstance(operand, ast.Constant) and operand.value == "__main__"
                    for operand in node.node.test.comparators)):
            is_inside_main = True
    for child in node.children:
        input_func_calls.extend(find_input_func(child, is_inside_main))
    return input_func_calls
