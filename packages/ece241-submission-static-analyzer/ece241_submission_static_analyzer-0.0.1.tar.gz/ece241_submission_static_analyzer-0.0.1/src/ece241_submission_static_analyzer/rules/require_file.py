from ece241_submission_static_analyzer.rules.rule import Rule, RuleType
from ece241_submission_static_analyzer.types.violation_result import ViolationRaw
from ece241_submission_static_analyzer.types.severity_type import SeverityType
import os
from typing import Any, Dict


def _is_file_exist(file: str) -> bool:
    """Check if a file exists.

    Args:
        file (str): The file to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.isfile(file)


class RequireFileRule(Rule):
    rule_type = RuleType.REQUIRE_FILE
    severity = SeverityType.ERROR

    @classmethod
    def _check(cls, file: str, **kwargs: Dict[str, Any]) -> list[ViolationRaw]:
        """Check for required files.

        Args:
            file (str): The file to check.

        Returns:
            ViolationResult | None: The result of the check or None if no violation is found.
        """
        if _is_file_exist(file):
            return []
        return [ViolationRaw(
            line_number=0,
            message=f"File '{file}' not found in your submission."
        )]
