from pyparsing import ParseException
from rapt2.treebrd.grammars.threevl_grammar import ThreeVLGrammar
from tests.treebrd.grammars.grammar_test_case import GrammarTestCase


class TestThreeVLGrammarRules(GrammarTestCase):
    def setUp(self):
        self.parser = ThreeVLGrammar()

    def test_op(self):
        parse = self.parse_function(self.parser.defined_op)
        self.assertEqual(parse("defined"), ["defined"])
        self.assertEqual(parse("DEFINED"), ["defined"])

    def test_condition(self):
        parse = self.parse_function(self.parser.defined_condition)
        self.assertEqual(parse("defined( apple )"), [["defined", "apple"]])

    def test_condition_fragments(self):
        parse = self.parse_function(self.parser.defined_condition)
        self.assertRaises(ParseException, parse, "defined (")
        self.assertRaises(ParseException, parse, "defined ( )")

    def test_conditions_single(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [["defined", "apple"]]
        actual = parse("defined(apple)")
        self.assertEqual(actual, expected)

    def test_conditions_par(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [["defined", "apple"]]
        actual = parse("(defined(apple))")
        self.assertEqual(actual, expected)

    def test_conditions_not(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [["not", ["defined", "apple"]]]
        actual = parse("not defined(apple)")
        self.assertEqual(actual, expected)

    def test_conditions_and(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [[["defined", "apple"], "and", ["defined", "pear"]]]
        actual = parse("defined(apple) and defined(pear)")
        self.assertEqual(actual, expected)

    def test_conditions_and_par(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [[["defined", "apple"], "and", ["defined", "pear"]]]
        actual = parse("(defined(apple)) and (defined(pear))")
        self.assertEqual(actual, expected)

    def test_conditions_or(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [[["defined", "apple"], "or", ["defined", "pear"]]]
        actual = parse("(defined(apple)) or (defined(pear))")
        self.assertEqual(actual, expected)

    def test_conditions_unary_binary_simple(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [[["not", ["defined", "apple"]], "and", ["defined", "pear"]]]
        actual = parse("not defined(apple) and defined(pear)")
        self.assertEqual(actual, expected)

    def test_conditions_unary_binary_simple_forced(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [["not", [["defined", "apple"], "and", ["defined", "pear"]]]]
        actual = parse("not (defined(apple) and defined(pear))")
        self.assertEqual(actual, expected)

    def test_conditions_binary_unary_simple(self):
        parse = self.parse_function(self.parser.conditions)
        expected = [[["defined", "pear"], "or", ["not", ["defined", "apple"]]]]
        actual = parse("defined(pear) or not defined(apple)")
        self.assertEqual(expected, actual)
