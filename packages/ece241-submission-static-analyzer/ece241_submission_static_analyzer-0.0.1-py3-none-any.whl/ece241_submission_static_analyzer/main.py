from ece241_submission_static_analyzer.rules.rule import Rule, ViolationResult
from typing import NamedTuple


class StaticAnalysisItem(NamedTuple):
    rule: Rule
    kwargs: dict[str, list[str]]
    file: str


def check(static_analysis_request: list[StaticAnalysisItem]) -> list[ViolationResult]:
    """Check a list of static analysis requests."""
    results = []
    for item in static_analysis_request:
        results.extend(item.rule.check(item.file, **item.kwargs))
    return results
