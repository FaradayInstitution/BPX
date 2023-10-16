from __future__ import annotations
import copy
from importlib import util
import tempfile
from typing import Callable

from bpx import ExpressionParser


class Function(str):
    """
    An expression in Python syntax. Only contains:
        - numbers
        - operators: * / - + **
        - math functions: exp, tanh,
        - single variable 'x'
    """

    parser = ExpressionParser()
    default_preamble = "from math import exp, tanh, cosh"

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(examples=["1 + x", "1.9793 * exp(-39.3631 * x)" "2 * x**2"])

    @classmethod
    def validate(cls, v: str) -> Function:
        if not isinstance(v, str):
            raise TypeError("string required")
        try:
            cls.parser.parse_string(v)
        except ExpressionParser.ParseException as e:
            raise ValueError(str(e))
        return cls(v)

    def __repr__(self):
        return f"Function({super().__repr__()})"

    def to_python_function(self, preamble: str = None) -> Callable:
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

        with tempfile.NamedTemporaryFile(
            suffix="{}.py".format(function_name), delete=False
        ) as tmp:
            # write to a tempory file so we can
            # get the source later on using inspect.getsource
            # (as long as the file still exists)
            tmp.write((source_code).encode())
            tmp.flush()

            # Now load that file as a module
            spec = util.spec_from_file_location("tmp", tmp.name)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)

        # return the new function object
        value = getattr(module, function_name)
        return value
