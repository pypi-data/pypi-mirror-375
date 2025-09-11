from typing import NamedTuple
from ece241_submission_static_analyzer.rules.rule import RuleType
from ece241_submission_static_analyzer.types.severity_type import SeverityType


class ViolationResult(NamedTuple):
    file_path: str
    line_number: int
    message: str
    rule: RuleType
    severity: SeverityType  # Updated to use SeverityType


class ViolationRaw(NamedTuple):
    line_number: int
    message: str
