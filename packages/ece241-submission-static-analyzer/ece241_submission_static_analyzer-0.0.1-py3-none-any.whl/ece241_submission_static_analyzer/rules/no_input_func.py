from ece241_submission_static_analyzer.rules.rule import Rule, RuleType
from ece241_submission_static_analyzer.types.violation_result import ViolationRaw
from ece241_submission_static_analyzer.types.severity_type import SeverityType
from ece241_submission_static_analyzer.rules.helpers.ast_helper import parse_file_to_ast, ASTWithChildren
from ece241_submission_static_analyzer.rules.helpers.find_input_func import find_input_func
import os
from typing import Any, Dict


class NoInputFuncRule(Rule):
    rule_type = RuleType.NO_INPUT_FUNC
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
        input_function_calls = find_input_func(ast_node, False)
        violations = []
        for call in input_function_calls:
            violations.append(ViolationRaw(
                line_number=call.node.lineno,  # type: ignore
                message=f"Usage of 'input' function is not allowed outside of 'if __name__ == \"__main__\"' block."
            ))
        return violations
