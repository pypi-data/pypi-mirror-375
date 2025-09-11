from ece241_submission_static_analyzer.rules.helpers.ast_helper import ASTWithChildren
import ast


def find_root_statement(node: ASTWithChildren) -> list[ASTWithChildren]:
    """Recursively find all any statements at root level in the AST.
    Allowed statements are ClassDef, FunctionDef, Import, ImportFrom, and If.
    Any other statements at the root level will be considered a violation.
    Note: only if statement allowed is `if __name__ == "__main__":`

    Args:
        node (ASTWithChildren): The AST node to search.

    Returns:
        list[ASTWithChildren]: A list of statements found at the root level in the AST.
    """
    root_statements = []
    if isinstance(node.node, ast.ClassDef):
        return []
    if isinstance(node.node, ast.FunctionDef):
        return []
    if isinstance(node.node, ast.Import):
        return []
    if isinstance(node.node, ast.ImportFrom):
        return []
    if isinstance(node.node, ast.If):
        if (isinstance(node.node.test, ast.Compare) and
                isinstance(node.node.test.left, ast.Name) and
                node.node.test.left.id == "__name__" and
                any(isinstance(operand, ast.Constant) and operand.value == "__main__"
                    for operand in node.node.test.comparators)):
            return []
    if not isinstance(node.node, ast.Module):
        # module is OK, as it is the root of the AST
        root_statements.append(node)

    for child in node.children:
        root_statements.extend(find_root_statement(child))
    return root_statements
