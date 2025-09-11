from ece241_submission_static_analyzer.rules.rule import Rule, RuleType
from ece241_submission_static_analyzer.types.violation_result import ViolationRaw
from ece241_submission_static_analyzer.types.severity_type import SeverityType
from ece241_submission_static_analyzer.rules.helpers.ast_helper import parse_file_to_ast, ASTWithChildren
from ece241_submission_static_analyzer.rules.helpers.find_root_statement import find_root_statement
from typing import Any, Dict


class NoRootStatementsRule(Rule):
    rule_type = RuleType.NO_ROOT_STATEMENTS
    severity = SeverityType.ERROR

    @classmethod
    def _check(cls, file: str, **kwargs: Dict[str, Any]) -> list[ViolationRaw]:
        """Check for required files.

        Args:
            file (str): The file to check.

        Returns:
            ViolationResult | None: The result of the check or None if no violation is found.
        """
        ast_node = parse_file_to_ast(file)
        root_statements = find_root_statement(ast_node)
        violations = []
        for stmt in root_statements:
            violations.append(ViolationRaw(
                line_number=stmt.node.lineno,  # type: ignore
                message=f"Root level statement found. You must only have class/function definitions, imports, or 'if __name__ == \"__main__\"' block at the root level."
            ))
        return violations
