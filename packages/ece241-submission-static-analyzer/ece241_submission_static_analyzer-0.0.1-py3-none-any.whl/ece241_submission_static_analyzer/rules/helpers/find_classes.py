from ece241_submission_static_analyzer.rules.helpers.ast_helper import ASTWithChildren
import ast


def find_class_defs(node: ASTWithChildren) -> dict[str, ASTWithChildren]:
    """Recursively find all class names in the AST.

    Args:
        node (ASTWithChildren): The AST node to search.

    Returns:
        dict[str, ASTWithChildren]: A dictionary of class names to their definitions found in the AST.
    """
    class_defs = {}
    if isinstance(node.node, ast.ClassDef):
        class_defs[node.node.name] = node
    for child in node.children:
        class_defs.update(find_class_defs(child))
    return class_defs
