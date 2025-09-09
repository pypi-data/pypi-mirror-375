"""
Contains a tokenizer for morethon language: tokenize(), etc.

NOTE: this module is private. All functions and objects are available in the main
`morethon` namespace - use that instead.

"""

import re
from itertools import chain
from typing import TYPE_CHECKING, Iterator, NamedTuple, Self

from . import error

if TYPE_CHECKING:
    from ._typing import TokenType

__all__ = ["UqToken", "UqTokenizer"]


class UqToken(NamedTuple):
    """Token for morethon language."""

    type: "TokenType"
    value: str
    lineno: int
    code: str

    def __bool__(self) -> bool:
        return self.type != "NULL"

    @classmethod
    def default(cls) -> Self:
        """Return a default instance."""
        return cls("NULL", "", 1, "")


class UqTokenizer:
    """Parser of UqTokens."""

    def __init__(self) -> None:
        self.token_spec = {
            "NUM": r"\d+(\.\d*)?",  # Integer or decimal numbers
            "DOUBLEARROW": r"=>",  # Double arrows
            "TYPEASSIGN": r":=",  # Type-assignment operators
            "ASSIGN": r"=",  # Assignment operators
            "END": r";",  # Statement terminators
            "ELLIPSIS": r"\.\.\.",  # Ellipsis
            "ID": r"[A-Za-z._]+",  # Identifiers
            "OP": r"[+\-*/^]",  # Arithmetic operators
            "NEWLINE": r"\n",  # Line endings
            "SKIP": r"[ \t]+",  # Skip over spaces and tabs
            "COMMENT": r"#.*",  # Comments
            "LPAR": r"\(",  # Left parentheses
            "RPAR": r"\)",  # Right parentheses
            "LSQUARE": r"\[",  # Left square brackets
            "RSQUARE": r"\]",  # Right square brackets
            "LBRACE": r"{",  # Left braces
            "RBRACE": r"}",  # Right braces
            "DOUBLECOLON": r"::",  # Double Colons
            "COLON": r":",  # Colons
            "COMMA": r",",  # Commas
            "TYPEJOIN": r"\$",  # Type join
            "ILLEGAL": r".",  # Any other character
        }
        self.token_pattern = "|".join(
            f"(?P<{k}>{v})" for k, v in self.token_spec.items()
        )
        self.keywords = {
            "using",
            "function",
            "str",
            "field",
            "factor",
            "int",
            "float",
            "bool",
            "True",
            "False",
        }
        self.iter = iter(())
        self.last_token = self.default_token = UqToken.default()

    def next(self) -> UqToken:
        """Return the next token if exists."""
        self.last_token = next(self.iter, self.default_token)
        return self.last_token

    def expect(self, token_type: "TokenType") -> UqToken:
        """Return the next token if is of token_type."""
        self.last_token = next(self.iter, self.default_token)
        if self.last_token.type != token_type:
            error.mismatched_token(self.last_token, self.token_spec[token_type])
        return self.last_token

    def consume(self, token_type: "TokenType") -> None:
        """Consume a token of token_type if exists."""
        self.last_token = next(self.iter, self.default_token)
        if self.last_token.type != token_type:
            error.mismatched_token(self.last_token, self.token_spec[token_type])

    def parse_code(self, code: str) -> None:
        """Parse the code."""
        self.iter = chain(self.iter, self.tokenize(code))

    def tokenize(self, code: str) -> Iterator[UqToken]:
        """Tokenize the code."""
        lineno = 1
        for m in re.finditer(self.token_pattern, code):
            ttype: "TokenType" = m.lastgroup
            value = m.group()
            match ttype:
                case "ID" if value in self.keywords:
                    ttype = value.upper()
                case "NEWLINE":
                    lineno += 1
                case "SKIP":
                    continue
            token = UqToken(ttype, value, lineno, code)
            if ttype == "ILLEGAL":
                error.illegal_token(token)
            yield token
