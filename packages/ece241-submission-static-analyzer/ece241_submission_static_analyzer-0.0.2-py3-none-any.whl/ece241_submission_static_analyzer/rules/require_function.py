from ece241_submission_static_analyzer.rules.rule import Rule, RuleType
from ece241_submission_static_analyzer.types.violation_result import ViolationRaw
from ece241_submission_static_analyzer.types.severity_type import SeverityType
from ece241_submission_static_analyzer.rules.helpers.find_functions import find_function_defs
from ece241_submission_static_analyzer.rules.helpers.ast_helper import parse_file_to_ast, ASTWithChildren
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def _find_function_names(node: ASTWithChildren, parent: Optional[ASTWithChildren]) -> list[str]:
    """Recursively find all function names in the AST.

    Args:
        node (ASTWithChildren): The AST node to search.

    Returns:
        list[str]: A list of function names found in the AST.
    """
    function_defs = find_function_defs(node, parent)
    return list(function_defs.keys())


class RequireFunctionRule(Rule):
    rule_type = RuleType.REQUIRE_FUNCTION
    severity = SeverityType.ERROR

    @classmethod
    def _check(cls, file: str, **kwargs: Dict[str, Any]) -> list[ViolationRaw]:
        """Check for required files.

        Args:
            file (str): The file to check.

        Returns:
            ViolationResult | None: The result of the check or None if no violation is found.
        """
        if "function_names" not in kwargs:
            raise ValueError(
                "function_names argument is required for RequiredFunctionRule")
        function_names = kwargs["function_names"]

        ast = parse_file_to_ast(file)
        found_function_names = _find_function_names(ast, None)
        logger.info(f"Found function names: {found_function_names}")
        if all(name in found_function_names for name in function_names):
            return []
        missing_functions = [
            name for name in function_names if name not in found_function_names]
        messages = [
            f"Function '{name}' not found in file {file}." for name in missing_functions]

        return [ViolationRaw(
            line_number=0,
            message="\n".join(messages)
        )]
