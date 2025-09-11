from ece241_submission_static_analyzer.rules.rule import Rule, RuleType
from ece241_submission_static_analyzer.types.violation_result import ViolationRaw
from ece241_submission_static_analyzer.types.severity_type import SeverityType
from ece241_submission_static_analyzer.rules.helpers.ast_helper import parse_file_to_ast, ASTWithChildren
from ece241_submission_static_analyzer.rules.helpers.find_functions import find_function_defs
from typing import Any, Dict
import ast

import logging
logger = logging.getLogger(__name__)


def _get_last_statement(node: ASTWithChildren) -> ASTWithChildren:
    """Get the last statement of a function block.

    Args:
        node (ASTWithChildren): The AST node to search.

    Returns:
        ast.stmt: The last statement found in the function block, or None if not found.
    """
    if not isinstance(node.node, ast.FunctionDef):
        raise ValueError("Node must be a FunctionDef")

    last_child = node.children[-1]
    return last_child


class FunctionMustReturnRule(Rule):
    rule_type = RuleType.FUNCTION_MUST_RETURN
    severity = SeverityType.WARNING

    @classmethod
    def _check(cls, file: str, **kwargs: Dict[str, Any]) -> list[ViolationRaw]:
        """Check for print statements as the last command in the file.

        Args:
            file (str): The file to check.

        Returns:
            ViolationResult | None: The result of the check or None if no violation is found.
        """
        ast_node = parse_file_to_ast(file)
        checking_functions = kwargs.get("functions", [])
        found_functions = find_function_defs(ast_node, None)
        checking_functions = [
            f for name, f in found_functions.items() if name in checking_functions]
        violations = []
        for func in checking_functions:
            function_name = func.node.name  # type: ignore
            last_command = _get_last_statement(func)
            logger.info(
                f"Last command in function {function_name}: {ast.dump(last_command.node)}")
            if isinstance(last_command.node, ast.Return):
                continue
            violations.append(ViolationRaw(
                line_number=last_command.node.lineno,  # type: ignore
                message="Function {} must return a value (at file: {}).".format(
                    function_name, file)
            ))

        # last_command = ast_node.body[-1] if ast_node.body else None
        # if isinstance(last_command, ast.Expr) and isinstance(last_command.value, ast.Call):
        #     func = last_command.value.func
        #     if isinstance(func, ast.Name) and func.id == "print":
        #         return ViolationRaw(
        #             line_number=last_command.lineno,
        #             message="Print statement found as the last command."
        #         )
        return violations
