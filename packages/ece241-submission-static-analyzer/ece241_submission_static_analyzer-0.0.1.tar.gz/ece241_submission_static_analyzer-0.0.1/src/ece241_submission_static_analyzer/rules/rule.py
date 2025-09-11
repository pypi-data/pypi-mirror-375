from ece241_submission_static_analyzer.types.rule_type import RuleType
from ece241_submission_static_analyzer.types.violation_result import ViolationResult, ViolationRaw
from ece241_submission_static_analyzer.types.severity_type import SeverityType
import pathlib


class Rule:
    rule_type: RuleType
    severity: SeverityType

    @classmethod
    def check(cls, file: str, **kwargs: list[str]) -> list[ViolationResult]:
        """Check for required files.

        Args:
            file (str): The file to check.

        Raises:
            NotImplementedError: If the check logic is not implemented.

        Returns:
            ViolationResult | None: The result of the check or None if no violation is found.
        """
        result = cls._check(file, **kwargs)
        file_name = pathlib.Path(file).name
        return [ViolationResult(
            rule=cls.rule_type,
            line_number=v.line_number,
            file_path=file_name,
            message=v.message,
            severity=cls.severity
        ) for v in result]

    @classmethod
    def _check(cls, file: str, **kwargs: list[str]) -> list[ViolationRaw]:
        """Internal check method to be overridden by subclasses.

        Args:
            file (str): The file to check.

        Returns:
            ViolationResult | None: The result of the check or None if no violation is found.
        """
        raise NotImplementedError(
            "Check logic for {} rule is NOT implemented".format(cls.rule_type))
