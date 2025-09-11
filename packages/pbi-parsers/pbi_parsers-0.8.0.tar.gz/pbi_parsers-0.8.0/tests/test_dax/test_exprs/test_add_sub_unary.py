import pytest

from pbi_parsers.base.tokens import TextSlice
from pbi_parsers.dax import Expression, Parser, Token, TokenType
from pbi_parsers.dax.exprs import AddSubUnaryExpression

num1 = Token(TokenType.NUMBER_LITERAL, TextSlice("1", start=0, end=1))
num2 = Token(TokenType.NUMBER_LITERAL, TextSlice("2", start=0, end=1))
operator_add = Token(TokenType.PLUS_SIGN, TextSlice("+", start=0, end=1))
operator_sub = Token(TokenType.MINUS_SIGN, TextSlice("-", start=0, end=1))

args = [
    [
        [operator_add, num1],
        """Number (
    sign: +,
    number: Number (1),
)""",
    ],
    [
        [operator_sub, num2],
        """Number (
    sign: -,
    number: Number (2),
)""",
    ],
]


@pytest.mark.parametrize(
    ("input_tokens", "output"),
    args,
)
def test_add_sub(input_tokens: list[Token], output: Expression) -> None:
    parser = Parser(input_tokens)
    result = AddSubUnaryExpression.match(parser)
    assert result is not None
    assert not parser.remaining()
    assert result.pprint() == output
