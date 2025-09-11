from ece241_submission_static_analyzer.rules.helpers.ast_helper import ASTWithChildren
from typing import Optional
import ast


def find_function_defs(node: ASTWithChildren, parent: Optional[ASTWithChildren]) -> dict[str, ASTWithChildren]:
    """Recursively find all function defs in the AST.

    Args:
        node (ASTWithChildren): The AST node to search.

    Returns:
        list[str]: A list of function names found in the AST.
    """
    function_defs = {}
    if isinstance(node.node, ast.FunctionDef):
        function_name = node.node.name
        if parent and isinstance(parent.node, ast.ClassDef):
            function_name = f"{parent.node.name}.{function_name}"
        function_defs[function_name] = node
    for child in node.children:
        function_defs.update(find_function_defs(child, node))
    return function_defs
