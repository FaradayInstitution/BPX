from __future__ import annotations

import copy
import tempfile
from importlib import util
from typing import TYPE_CHECKING, Any

from pydantic_core import CoreSchema, core_schema

from bpx import ExpressionParser

if TYPE_CHECKING:
    from collections.abc import Callable

    from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler


class Function(str):
    """
    An expression in Python syntax. Only contains:
        - numbers
        - operators: * / - + **
        - math functions: exp, tanh,
        - single variable 'x'
    """

    __slots__ = ()

    parser = ExpressionParser()
    default_preamble = "from math import exp, tanh, cosh"

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["examples"] = ["1 + x", "1.9793 * exp(-39.3631 * x)" "2 * x**2"]
        return handler.resolve_ref_schema(json_schema)

    @classmethod
    def validate(cls, v: str) -> Function:
        if not isinstance(v, str):
            error_msg = "string required"
            raise TypeError(error_msg)
        try:
            cls.parser.parse_string(v)
        except ExpressionParser.ParseException as e:
            raise ValueError(str(e)) from e
        return cls(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: str,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            handler(str),
        )

    def __repr__(self) -> str:
        return f"Function({super().__repr__()})"

    def to_python_function(self, preamble: str | None = None) -> Callable:
        """
        Return a python function that can be called with a single argument 'x'

        Parameters
        ----------
            preamble: str, optional
                A string of python code to be prepended to the function
                definition. This can be used to import modules or define
                helper functions.
        """
        if preamble is None:
            preamble = copy.copy(self.default_preamble)
        preamble += "\n\n"
        arg_names = ["x"]
        arg_str = ",".join(arg_names)
        function_name = "reconstructed_function"
        function_def = f"def {function_name}({arg_str}):\n"
        function_body = f"  return {self}"
        source_code = preamble + function_def + function_body

        with tempfile.NamedTemporaryFile(suffix=f"{function_name}.py", delete=False) as tmp:
            tmp.write(source_code.encode())
            tmp.flush()
            spec = util.spec_from_file_location("tmp", tmp.name)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)

        return getattr(module, function_name)
