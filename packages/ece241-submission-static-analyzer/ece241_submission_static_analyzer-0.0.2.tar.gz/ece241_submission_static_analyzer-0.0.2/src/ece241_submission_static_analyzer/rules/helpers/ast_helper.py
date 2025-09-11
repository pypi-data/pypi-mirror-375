import ast
from typing import NamedTuple


class ASTWithChildren(NamedTuple):
    node: ast.AST
    children: list['ASTWithChildren']


def _read_file(file_path: str) -> str:
    """Read the content of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    with open(file_path, "r") as f:
        return f.read()


def _parse_ast(source: str) -> ast.AST:
    """Parse the source code into an Abstract Syntax Tree (AST).

    Args:
        source (str): The source code to parse.

    Returns:
        ast.AST: The parsed AST.
    """
    return ast.parse(source)


def build_wrapped_tree(node: ast.AST) -> ASTWithChildren:
    # 查找当前原始节点的逻辑子节点（这部分逻辑和之前一样）
    raw_children: list[ast.AST] = []

    # 检查包含语句列表的常见属性
    if hasattr(node, 'body') and isinstance(node.body, list):  # type: ignore
        raw_children.extend(node.body)  # type: ignore

    # if/for/while 循环可能有 'orelse' 代码块
    if hasattr(node, 'orelse') and isinstance(node.orelse, list):  # type: ignore
        raw_children.extend(node.orelse)  # type: ignore

    # Try 块有特殊的 'handlers' 和 'finalbody'
    if isinstance(node, ast.Try):
        if hasattr(node, 'handlers') and isinstance(node.handlers, list):
            raw_children.extend(node.handlers)
        if hasattr(node, 'finalbody') and isinstance(node.finalbody, list):
            raw_children.extend(node.finalbody)

    # ExceptHandler 节点自己也有 body
    if isinstance(node, ast.ExceptHandler):
        if hasattr(node, 'body') and isinstance(node.body, list):
            raw_children.extend(node.body)

    # 递归地为所有找到的原始子节点创建包装后的对象
    wrapped_children = [build_wrapped_tree(child) for child in raw_children]

    # 创建并返回当前节点的包装对象
    return ASTWithChildren(node=node, children=wrapped_children)


def enrich_ast_with_children(node: ast.AST) -> ASTWithChildren:
    """add children to each AST node.

    Args:
        node (ast.AST): The AST node to enrich.

    Returns:
        ASTWithChildren: The enriched AST node with children.
    """
    # 查找当前原始节点的逻辑子节点（这部分逻辑和之前一样）
    raw_children: list[ast.AST] = []

    # 检查包含语句列表的常见属性
    if hasattr(node, 'body') and isinstance(node.body, list):  # type: ignore
        raw_children.extend(node.body)  # type: ignore

    # if/for/while 循环可能有 'orelse' 代码块
    if hasattr(node, 'orelse') and isinstance(node.orelse, list):  # type: ignore
        raw_children.extend(node.orelse)  # type: ignore

    # Try 块有特殊的 'handlers' 和 'finalbody'
    if isinstance(node, ast.Try):
        if hasattr(node, 'handlers') and isinstance(node.handlers, list):
            raw_children.extend(node.handlers)
        if hasattr(node, 'finalbody') and isinstance(node.finalbody, list):
            raw_children.extend(node.finalbody)

    # ExceptHandler 节点自己也有 body
    if isinstance(node, ast.ExceptHandler):
        if hasattr(node, 'body') and isinstance(node.body, list):
            raw_children.extend(node.body)

    # 递归地为所有找到的原始子节点创建包装后的对象
    wrapped_children = [build_wrapped_tree(child) for child in raw_children]

    # 创建并返回当前节点的包装对象
    return ASTWithChildren(node=node, children=wrapped_children)


def parse_file_to_ast(file_path: str) -> ASTWithChildren:
    """Parse a file into an Abstract Syntax Tree (AST).

    Args:
        file_path (str): The path to the file.

    Returns:
        ast.AST: The parsed AST.
    """
    source = _read_file(file_path)
    ast_node = _parse_ast(source)
    return enrich_ast_with_children(ast_node)
