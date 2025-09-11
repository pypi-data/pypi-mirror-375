from pyparsing import CaselessKeyword, Literal, Group
from .extended_grammar import ExtendedGrammar


class ThreeVLGrammar(ExtendedGrammar):
    """
    A parser that recognizes a three-valued logic relational algebra grammar.

    The rules are annotated with their BNF equivalents. For a complete
    specification refer to the associated grammar file.
    """

    @property
    def defined_op(self):
        return CaselessKeyword(self.syntax.defined_op)

    @property
    def defined_condition(self):
        """
        defined_condition ::= defined_op "(" operand ")"
        """
        return Group(
            self.defined_op
            + Literal(self.syntax.paren_left).suppress()
            + self.operand
            + Literal(self.syntax.paren_right).suppress()
        )

    @property
    def condition(self):
        """
        condition ::= condition | defined_condition
        """
        return super().condition | self.defined_condition
