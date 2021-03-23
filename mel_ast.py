from abc import ABC, abstractmethod
from typing import Callable, Tuple, Optional, Union
from enum import Enum


class AstNode(ABC):
    @property
    def childs(self)->Tuple['AstNode', ...]:
        return ()

    @abstractmethod
    def __str__(self)->str:
        pass

    @property
    def tree(self)->[str, ...]:
        res = [str(self)]
        childs = self.childs
        for i, child in enumerate(childs):
            ch0, ch = '├', '│'
            if i == len(childs) - 1:
                ch0, ch = '└', ' '
            res.extend(((ch0 if j == 0 else ch) + ' ' + s for j, s in enumerate(child.tree)))
        return res

    def visit(self, func: Callable[['AstNode'], None])->None:
        func(self)
        map(func, self.childs)

    def __getitem__(self, index):
        return self.childs[index] if index < len(self.childs) else None


class ExprNode(AstNode):
    pass


class NumNode(ExprNode):
    def __init__(self, num: float):
        super().__init__()
        self.num = float(num)

    def __str__(self)->str:
        return str(self.num)


class VartypeNode(ExprNode):
    def __init__(self, type: str):
        super().__init__()
        self.type = str(type)

    def __str__(self)->str:
        return str(self.type)

class IdentNode(ExprNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = str(name)

    def __str__(self)->str:
        return str(self.name)


class BinOp(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'


class BinOpNode(ExprNode):
    def __init__(self, op: BinOp, arg1: ExprNode, arg2: ExprNode):
        super().__init__()
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

    @property
    def childs(self) -> Tuple[ExprNode, ExprNode]:
        return self.arg1, self.arg2

    def __str__(self)->str:
        return str(self.op.value)


class InputNode(AstNode):
    def __init__(self, var: IdentNode):
        self.var = var

    @property
    def childs(self) -> Tuple[IdentNode]:
        return self.var,

    def __str__(self)->str:
        return 'input'


class OutputNode(AstNode):
    def __init__(self, arg: ExprNode):
        self.arg = arg

    @property
    def childs(self) -> Tuple[ExprNode]:
        return self.arg,

    def __str__(self)->str:
        return 'output'


class StmtNode(AstNode):
    pass

class StmtListNode(AstNode):
    def __init__(self, *exprs: AstNode):
        super().__init__()
        self.exprs = exprs

    @property
    def childs(self) -> Tuple[AstNode]:
        return self.exprs

    def __str__(self)->str:
        return '...'


class AssignNode(StmtNode):
    def __init__(self, var: IdentNode, val: ExprNode):
        super().__init__()
        self.var = var
        self.val = val

    @property
    def childs(self) -> Tuple[IdentNode, ExprNode]:
        return self.var, self.val

    def __str__(self)->str:
        return '='

class DeclareNode(StmtNode):
    def __init__(self, vartype: VartypeNode, val: AssignNode):
        super().__init__()
        self.vartype = vartype
        self.val = val

    @property
    def childs(self) -> Tuple[VartypeNode, AssignNode]:
        return (self.vartype, self.val)

    def __str__(self)->str:
        return 'let'


class IfNode(StmtNode):
    def __init__(self, cond: ExprNode, then_stmt: StmtListNode, *opt_stmt: Union[ExprNode, StmtListNode]):
        super().__init__()
        self.cond = cond
        self.then_stmt = then_stmt
        self.opt_stmt = opt_stmt

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode, Union[ExprNode, StmtListNode]]:
        return (self.cond, self.then_stmt) + (self.opt_stmt if self.opt_stmt else tuple())

    def __str__(self) -> str:
        return 'if'


class LoopNode(StmtNode):
    def __init__(self, body: StmtListNode):
        super().__init__()
        self.body = body

    @property
    def childs(self) -> Tuple[StmtListNode]:
        return (self.body,)

    def __str__(self) -> str:
        return 'loop'


class WhileNode(StmtNode):
    def __init__(self, cond: ExprNode, body: StmtListNode):
        super().__init__()
        self.cond = cond
        self.body = body

    @property
    def childs(self) -> Tuple[ExprNode, StmtListNode]:
        return (self.cond, self.body)

    def __str__(self) -> str:
        return 'while'

class ForNode(StmtNode):
    def __init__(self, init: ExprNode, cond: ExprNode, incr: ExprNode, body: StmtListNode):
        super().__init__()
        self.init = init
        self.cond = cond
        self.incr = incr
        self.body = body

    @property
    def childs(self) -> Tuple[ExprNode, ExprNode, ExprNode, StmtListNode]:
        return (self.init, self.cond, self.incr, self.body)

    def __str__(self) -> str:
        return 'for'


class ScopeNode(StmtNode):
    def __init__(self, body: StmtListNode):
        super().__init__()
        self.body = body

    @property
    def childs(self) -> Tuple[StmtListNode]:
        return (self.body,)

    def __str__(self) -> str:
        return 'scope'


