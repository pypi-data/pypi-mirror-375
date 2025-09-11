from enum import Enum


class RuleType(Enum):
    REQUIRE_FILE = "require_file"
    REQUIRE_CLASS = "require_class"
    REQUIRE_FUNCTION = "require_function"
    FUNCTION_MUST_RETURN = "function_must_return"
    NO_INPUT_FUNC = "no_input_FUNC"
    NO_ROOT_STATEMENTS = "no_root_statements"
