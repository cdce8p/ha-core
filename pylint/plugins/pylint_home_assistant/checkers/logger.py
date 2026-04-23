"""Checker for logger message formatting.

Ensures logger messages start with a capital letter and do not end with a
period, enforcing a consistent style across the codebase.
"""

from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.lint import PyLinter

LOGGER_NAMES = ("LOGGER", "_LOGGER")
LOG_LEVEL_ALLOWED_LOWER_START = ("debug",)


class HassLoggerFormatChecker(BaseChecker):
    """Checker for logger invocations."""

    name = "home_assistant_logger"
    priority = -1
    msgs = {
        "C7401": (
            "User visible logger messages must not end with a period",
            "home-assistant-logger-period",
            "Periods are not permitted at the end of logger messages",
        ),
        "C7402": (
            "User visible logger messages must start with a capital letter or downgrade to debug",
            "home-assistant-logger-capital",
            "All logger messages must start with a capital letter",
        ),
    }
    options = ()

    def visit_call(self, node: nodes.Call) -> None:
        """Check for improper log messages."""
        match node:
            case nodes.Call(
                func=nodes.Attribute(attrname=attrname, expr=nodes.Name(name=name)),
                args=[nodes.Const(value=log_message), *_],
            ) if name in LOGGER_NAMES and len(log_message) > 0:
                if log_message[-1] == ".":
                    self.add_message("home-assistant-logger-period", node=node)

                if (
                    attrname not in LOG_LEVEL_ALLOWED_LOWER_START
                    and log_message[0].upper() != log_message[0]
                ):
                    self.add_message("home-assistant-logger-capital", node=node)


def register(linter: PyLinter) -> None:
    """Register the checker."""
    linter.register_checker(HassLoggerFormatChecker(linter))
