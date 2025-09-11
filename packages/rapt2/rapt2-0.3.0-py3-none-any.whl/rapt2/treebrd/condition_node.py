from enum import Enum, auto
from abc import ABC, abstractmethod
from dataclasses import dataclass

from rapt2.treebrd.grammars.condition_grammar import ConditionGrammar
from rapt2.treebrd.grammars.syntax import Syntax


class UnaryConditionalOperator(Enum):
    NOT = auto()
    DEFINED = auto()

    @classmethod
    def from_syntax(cls, syntax: Syntax, instring: str) -> "UnaryConditionalOperator":
        match instring:
            case syntax.not_op:
                return cls.NOT
            case syntax.defined_op:
                return cls.DEFINED
            case _:
                raise ValueError


class BinaryConditionalOperator(Enum):
    AND = auto()
    OR = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    LESS_THAN_EQUAL = auto()
    GREATER_THAN = auto()
    GREATER_THAN_EQUAL = auto()

    @classmethod
    def from_syntax(cls, syntax: Syntax, instring: str) -> "BinaryConditionalOperator":
        match instring:
            case syntax.and_op:
                return cls.AND
            case syntax.or_op:
                return cls.OR
            case syntax.equal_op:
                return cls.EQUAL
            case syntax.not_equal_op | syntax.not_equal_alt_op:
                return cls.NOT_EQUAL
            case syntax.less_than_op:
                return cls.LESS_THAN
            case syntax.less_than_equal_op:
                return cls.LESS_THAN_EQUAL
            case syntax.greater_than_op:
                return cls.GREATER_THAN
            case syntax.greater_than_equal_op:
                return cls.GREATER_THAN_EQUAL
            case _:
                raise ValueError


@dataclass(frozen=True)
class ConditionNode(ABC):
    @abstractmethod
    def to_latex(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def to_sql(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def attribute_references(self) -> list[str]:
        """
        Return a list of attribute references in this condition node.
        """
        raise NotImplementedError()


@dataclass(frozen=True)
class IdentityConditionNode(ConditionNode):
    ident: str

    def to_latex(self) -> str:
        return self.ident

    def to_sql(self) -> str:
        return self.ident

    def attribute_references(self) -> list[str]:
        try:
            ConditionGrammar().attribute_reference.parse_string(self.ident)
            return [self.ident]
        except Exception:
            return []


@dataclass(frozen=True)
class UnaryConditionNode(ConditionNode):
    op: UnaryConditionalOperator
    child: ConditionNode

    def to_latex(self) -> str:
        match self.op:
            case UnaryConditionalOperator.NOT:
                return f"\\neg {self.child.to_latex()}"
            case UnaryConditionalOperator.DEFINED:
                return f"\\text{{defined}}({self.child.to_latex()})"
            case _:
                raise ValueError

    def to_sql(self) -> str:
        match self.op:
            case UnaryConditionalOperator.NOT:
                return f"NOT {self.child.to_sql()}"
            case UnaryConditionalOperator.DEFINED:
                return f"{self.child.to_sql()} IS NOT NULL"
            case _:
                raise ValueError

    def attribute_references(self) -> list[str]:
        return self.child.attribute_references()


@dataclass(frozen=True)
class BinaryConditionNode(ConditionNode):
    op: BinaryConditionalOperator
    left: ConditionNode
    right: ConditionNode

    def to_latex(self) -> str:
        match self.op:
            case BinaryConditionalOperator.AND:
                return f"({self.left.to_latex()} \\land {self.right.to_latex()})"
            case BinaryConditionalOperator.OR:
                return f"({self.left.to_latex()} \\lor {self.right.to_latex()})"
            case BinaryConditionalOperator.EQUAL:
                return f"({self.left.to_latex()} \\eq {self.right.to_latex()})"
            case BinaryConditionalOperator.NOT_EQUAL:
                return f"({self.left.to_latex()} \\neq {self.right.to_latex()})"
            case BinaryConditionalOperator.LESS_THAN:
                return f"({self.left.to_latex()} \\lt {self.right.to_latex()})"
            case BinaryConditionalOperator.LESS_THAN_EQUAL:
                return f"({self.left.to_latex()} \\leq {self.right.to_latex()})"
            case BinaryConditionalOperator.GREATER_THAN:
                return f"({self.left.to_latex()} \\gt {self.right.to_latex()})"
            case BinaryConditionalOperator.GREATER_THAN_EQUAL:
                return f"({self.left.to_latex()} \\geq {self.right.to_latex()})"
            case _:
                raise ValueError

    def to_sql(self) -> str:
        match self.op:
            case BinaryConditionalOperator.AND:
                return f"({self.left.to_sql()} AND {self.right.to_sql()})"
            case BinaryConditionalOperator.OR:
                return f"({self.left.to_sql()} OR {self.right.to_sql()})"
            case BinaryConditionalOperator.EQUAL:
                return f"({self.left.to_sql()} = {self.right.to_sql()})"
            case BinaryConditionalOperator.NOT_EQUAL:
                return f"({self.left.to_sql()} != {self.right.to_sql()})"
            case BinaryConditionalOperator.LESS_THAN:
                return f"({self.left.to_sql()} < {self.right.to_sql()})"
            case BinaryConditionalOperator.LESS_THAN_EQUAL:
                return f"({self.left.to_sql()} <= {self.right.to_sql()})"
            case BinaryConditionalOperator.GREATER_THAN:
                return f"({self.left.to_sql()} > {self.right.to_sql()})"
            case BinaryConditionalOperator.GREATER_THAN_EQUAL:
                return f"({self.left.to_sql()} >= {self.right.to_sql()})"
            case _:
                raise ValueError

    def attribute_references(self) -> list[str]:
        return list(
            self.left.attribute_references() + self.right.attribute_references()
        )
