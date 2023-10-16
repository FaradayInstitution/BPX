# based on fourFn.py example from pyparsing
# (https://github.com/pyparsing/pyparsing/blob/master/examples/fourFn.py)
# Copyright 2003-2019 by Paul McGuire
#

import pyparsing as pp
import pyparsing.common as ppc


class ExpressionParser:
    """
    An expression parser for mathematical expressions. For valid expressions,
    please see :class:`bpx.Function`.
    """

    ParseException = pp.ParseException

    def __init__(self):
        fnumber = ppc.number()
        ident = pp.Literal("x")
        fn_ident = pp.Literal("x")

        fn_ident = pp.Word(pp.alphas, pp.alphanums)
        plus, minus, mult, div = map(pp.Literal, "+-*/")
        lpar, rpar = map(pp.Suppress, "()")
        addop = plus | minus
        multop = mult | div
        expop = pp.Literal("**")

        expr = pp.Forward()

        expr_list = pp.delimitedList(pp.Group(expr))

        def insert_fn_argcount_tuple(t):
            fn = t.pop(0)
            num_args = len(t[0])
            t.insert(0, (fn, num_args))

        fn_call = (fn_ident + lpar - pp.Group(expr_list) + rpar).setParseAction(
            insert_fn_argcount_tuple
        )

        atom = (
            addop[...]
            + (
                (fn_call | fnumber | ident).set_parse_action(self.push_first)
                | pp.Group(lpar + expr + rpar)
            )
        ).set_parse_action(self.push_unary_minus)

        # by defining exponentiation as "atom [ ^ factor ]..." instead of "atom
        # [ ^ atom ]...", we get right-to-left exponents, instead of
        # left-to-right that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = pp.Forward()
        factor <<= atom + (expop + factor).set_parse_action(self.push_first)[...]
        term = factor + (multop + factor).set_parse_action(self.push_first)[...]
        expr <<= term + (addop + term).set_parse_action(self.push_first)[...]

        self.expr_stack = []
        self.parser = expr

    def push_first(self, toks):
        self.expr_stack.append(toks[0])

    def push_unary_minus(self, toks):
        for t in toks:
            if t == "-":
                self.expr_stack.append("unary -")
            else:
                break

    def parse_string(self, model_str, parse_all=True):
        self.expr_stack = []
        self.parser.parseString(model_str, parseAll=parse_all)
