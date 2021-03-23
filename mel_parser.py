from contextlib import suppress
import inspect

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from mel_ast import *


def _make_parser():
    num = ppc.fnumber
    ident = ppc.identifier
    vartype = pp.oneOf(('int real bool char'))

    LPAR, RPAR = pp.Literal('(').suppress(), pp.Literal(')').suppress()
    ASSIGN = pp.Literal('=')
    MULT, ADD = pp.oneOf(('* /')), pp.oneOf(('+ -'))

    INPUT = pp.Keyword('input')
    OUTPUT = pp.Keyword('output')

    add = pp.Forward()

    group = ident | num | LPAR + add + RPAR
    mult = group + pp.ZeroOrMore(MULT + group)
    add << mult + pp.ZeroOrMore(ADD + mult)

    expr = add

    stmt_list = pp.Forward()

    input = INPUT.suppress() + ident
    output = OUTPUT.suppress() + add
    assign = ident + ASSIGN.suppress() + add
    declare = vartype + assign

    if_ = pp.Keyword("if").suppress() + expr + pp.Keyword("then").suppress() + stmt_list + \
          pp.ZeroOrMore(pp.Keyword("elif").suppress() + expr + pp.Keyword("then").suppress() + stmt_list) + \
            pp.Optional(pp.Keyword("else").suppress() + stmt_list) + pp.Keyword("end if").suppress()

    loop_ = pp.Keyword("loop").suppress() + stmt_list + pp.Keyword("end loop").suppress()

    while_ = pp.Keyword("while").suppress() + expr + loop_

    for_ = pp.Keyword("for").suppress() + expr + \
             pp.Literal(",").suppress() + expr + \
             pp.Literal(",").suppress() + expr + loop_

    scope = pp.Keyword("begin").suppress() + stmt_list + pp.Keyword("end").suppress()

    stmt = ( input | output | assign | declare | if_ | loop_ | while_ | for_ | scope)

    #scope = pp.Keyword('begin').suppress(), pp.Literal('end').suppress()

    stmt_list << pp.ZeroOrMore(stmt)
    program = stmt_list.ignore(pp.cStyleComment).ignore(pp.dblSlashComment) + pp.StringEnd()

    start = program

    def set_parse_action_magic(rule_name: str, parser: pp.ParserElement)->None:
        if rule_name == rule_name.upper():
            return
        if rule_name in ('mult', 'add'):
            def bin_op_parse_action(s, loc, tocs):
                node = tocs[0]
                for i in range(1, len(tocs) - 1, 2):
                    node = BinOpNode(BinOp(tocs[i]), node, tocs[i + 1])
                return node
            parser.setParseAction(bin_op_parse_action)
        else:
            cls = ''.join(x.capitalize() for x in rule_name.split('_')) + 'Node'
            with suppress(NameError):
                cls = eval(cls)
                if not inspect.isabstract(cls):
                    def parse_action(s, loc, tocs):
                        return cls(*tocs)

                    parser.setParseAction(parse_action)

    for var_name, value in locals().copy().items():
        if isinstance(value, pp.ParserElement):
            set_parse_action_magic(var_name, value)

    return start


parser = _make_parser()


def parse(prog: str)->StmtListNode:
    return parser.parseString(str(prog))[0]
