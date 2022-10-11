from bpx import FunctionParser


class Function(str):
    """
    An expression in Python syntax. Only contains:
        - numbers
        - operators: * / - + ^
        - math functions: exp, tanh,
        - single variable 'x'
    """
    parser = FunctionParser()

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            examples=[
                "1 + x",
                "1.9793 * exp(-39.3631 * x)"
                "2 * x^2"
            ]
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        try:
            cls.parser.parse_string(v)
        except FunctionParser.ParseException as e:
            raise ValueError(str(e))
        return cls(v)

    def __repr__(self):
        return f'Function({super().__repr__()})'
