
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from mypy.options import Options
from mypy.plugin import FunctionContext, Plugin, ReportConfigContext
from mypy.types import Instance, TupleType, Type, get_proper_type


class DeprecatedConstantPlugin(Plugin):
    """Help better infer Literal values of DeprecatedConstant."""

    def __init__(self, options: Options) -> None:
        super().__init__(options)
        self.fullname = "homeassistant.helpers.deprecation.DeprecatedConstant"
        self.attr_name_name = "value"

    def report_config_data(self, ctx: ReportConfigContext) -> dict[str, Any]:
        return {
            "fullname": self.fullname,
            "attr": self.attr_name_name
        }

    def enum_function_hook(self, ctx: FunctionContext) -> Type:
        ret_type = get_proper_type(ctx.default_return_type)
        if not isinstance(ret_type, TupleType):
            return ctx.default_return_type
        try:
            idx = ctx.callee_arg_names.index(self.attr_name_name)
        except ValueError:
            return ctx.default_return_type
        arg_type = get_proper_type(ctx.arg_types[0][idx])
        if not isinstance(arg_type, Instance) or arg_type.last_known_value is None:
            return ctx.default_return_type
        arg_type = arg_type.last_known_value
        items = ret_type.items
        items[idx] = arg_type
        fallback = ret_type.partial_fallback.copy_modified(
            args=[arg_type]
        )

        return TupleType(
            items=items,
            fallback=fallback,
            line=ret_type.line,
            column=ret_type.column,
        )

    def get_function_hook(self, fullname: str) -> Callable[[FunctionContext], Type] | None:
        if fullname == self.fullname:
            return self.enum_function_hook
        return None


def plugin(version: str) -> type[Plugin]:
    return DeprecatedConstantPlugin


if TYPE_CHECKING:
    def _test_deprecated_constant_plugin() -> None:
        from typing import Final, Literal, assert_type, reveal_type

        from homeassistant.helpers.deprecation import DeprecatedConstant

        # help better infer literal value for 'value' attribute
        _DEPRECATED_ATTR_KELVIN: Final = DeprecatedConstant(
            "kelvin", "ATTR_COLOR_TEMP_KELVIN", "2026.1"
        )
        assert_type(_DEPRECATED_ATTR_KELVIN.value, Literal["kelvin"])
        reveal_type(_DEPRECATED_ATTR_KELVIN)        # should be DeprecatedConstant[Literal["kelvin"]]
        reveal_type(_DEPRECATED_ATTR_KELVIN.value)  # should be "Literal['kelvin']"

        # Plugin should not effect concrete instances
        _DEPRECATED_ATTR_COLOR_TEMP: Final[DeprecatedConstant[Literal["color_temp"]]] = DeprecatedConstant(
            "color_temp", "kelvin equivalent (ATTR_COLOR_TEMP_KELVIN)", "2026.1"
        )
        assert_type(_DEPRECATED_ATTR_COLOR_TEMP.value, Literal["color_temp"])
        reveal_type(_DEPRECATED_ATTR_COLOR_TEMP)        # should be DeprecatedConstant[Literal["color_temp"]]
        reveal_type(_DEPRECATED_ATTR_COLOR_TEMP.value)  # should be "Literal['color_temp']"
