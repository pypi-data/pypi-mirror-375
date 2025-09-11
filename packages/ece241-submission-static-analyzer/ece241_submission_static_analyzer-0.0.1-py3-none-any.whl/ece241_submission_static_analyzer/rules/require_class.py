from ece241_submission_static_analyzer.rules.rule import Rule, RuleType
from ece241_submission_static_analyzer.types.violation_result import ViolationRaw
from ece241_submission_static_analyzer.types.severity_type import SeverityType
from ece241_submission_static_analyzer.rules.helpers.ast_helper import parse_file_to_ast, ASTWithChildren
from ece241_submission_static_analyzer.rules.helpers.find_classes import find_class_defs
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


def _find_class_names(node: ASTWithChildren) -> list[str]:
    """Recursively find all class names in the AST.

    Args:
        node (ASTWithChildren): The AST node to search.

    Returns:
        list[str]: A list of class names found in the AST.
    """
    class_defs = find_class_defs(node)
    return list(class_defs.keys())


class RequireClassRule(Rule):
    rule_type = RuleType.REQUIRE_CLASS
    severity = SeverityType.ERROR

    @classmethod
    def _check(cls, file: str, **kwargs: Dict[str, Any]) -> list[ViolationRaw]:
        """Check for required files.

        Args:
            file (str): The file to check.

        Returns:
            ViolationResult | None: The result of the check or None if no violation is found.
        """
        if "class_names" not in kwargs:
            raise ValueError(
                "class_names argument is required for RequiredClassRule")
        class_names = kwargs["class_names"]

        ast = parse_file_to_ast(file)
        found_class_names = _find_class_names(ast)
        logger.info(f"Found class names: {found_class_names}")
        if all(name in found_class_names for name in class_names):
            return []
        missing_classes = [
            name for name in class_names if name not in found_class_names]
        messages = [
            f"Class '{name}' not found in file {file}." for name in missing_classes]

        return [ViolationRaw(
            line_number=0,
            message="\n".join(messages)
        )]
