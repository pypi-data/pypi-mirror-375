"""
Processes the morethon abstract syntax grammar.

NOTE: this module is private. All functions and objects are available in the main
`morethon` namespace - use that instead.

"""

import re
from typing import TYPE_CHECKING, Callable, NamedTuple, Self

from . import error
from .tokenize import UqToken, UqTokenizer

if TYPE_CHECKING:
    from ._typing import VarType

__all__ = ["UqParser"]


class Field:
    """Uq field."""

    def __init__(self, *args):
        pass

    def record_as_factor(self) -> None:
        """Factor."""


class UqFuncType(NamedTuple):
    """Defines function type in morethon language."""

    require: "VarType"
    returns: "VarType"


class UqVar(NamedTuple):
    """Defines variables in morethon language."""

    name: str
    type: "VarType"
    value: Callable[[Self], Self] | Field | str | int | float | bool | None

    @classmethod
    def from_token(cls, token: UqToken) -> Self:
        """Init from token."""
        return cls("", token.type, token.value)

    @classmethod
    def default(cls) -> Self:
        """Return a default instance."""
        return cls("", "NULL", None)

    def force_type(self, var_type: "VarType") -> Self:
        """Force to the type."""
        if (self.type == var_type) or (self.is_function() and var_type == "FUNCTION"):
            return self
        error.is_not_type(self, var_type)

    def is_function(self) -> bool:
        """Is self a function."""
        return isinstance(self.type, UqFuncType)

    def is_list(self) -> bool:
        """Is self a list."""
        return self.type == "LIST"

    def eval(self, arg: Self) -> Self:
        """Get value if is function."""
        if not self.is_function():
            error.not_a_function(self)
        return self.value(arg)

    def getitem(self, arg: Self) -> Self:
        """Get item if is list."""
        if not self.is_list():
            error.not_a_list(self)
        return self.value(arg)

    def setname(self, name: str) -> None:
        """Set name."""
        self.name = name


class UqNamespace(NamedTuple):
    """Defines namespaces in morethon language."""

    name: str
    variables: dict[str, UqVar]
    namespaces: dict[str, Self]

    def __contains__(self, key: str, /) -> bool:
        splited = re.split(r"::", key, maxsplit=1)
        if len(splited) == 1:
            return key in self.variables or key in self.namespaces
        sp, name = splited
        return sp in self.namespaces and name in self.namespaces[sp]

    def __getitem__(self, key: str, /) -> UqVar:
        if not key in self:
            error.not_defined(key)
        splited = re.split(r"::", key, maxsplit=1)
        if len(splited) == 1:
            if key in self.namespaces:
                error.getting_namespace(key)
            return self.variables[key]
        sp, name = splited
        return self.namespaces[sp][name]

    def __setitem__(self, key: str, /) -> UqVar:
        if "::" in key:
            splited = re.split(r"::", key, maxsplit=1)
            error.setting_namespace(splited[0])
        if key in self:
            error.already_defined(key)
        return self.variables[key]

    def new(self) -> Self:
        """Renew a namespace."""
        return self.__class__(self.name, self.variables.copy(), self.namespaces)


class UqParser:
    """Processor for morethon language."""

    def __init__(self) -> None:
        self.tokenizer = UqTokenizer()

    def exec(self, code: str) -> None:
        """Execute the code."""
        self.tokenizer.parse_code(code)
        glob = UqNamespace("main", {}, {})
        try:
            lastvar = self.open_loop(glob)
            print(lastvar)
        except error.ErrorFromUq:
            pass

    def open_loop(self, glob: UqNamespace) -> UqVar:
        """Open-loop behaviour."""
        token = self.tokenizer.next()
        match t := token.type:
            case "ID" if token.value in glob:
                return self.eval_var(glob[token.value], glob)
            case "ID":
                return self.define_var(token.value, glob)
            case "LPAR":
                return self.in_parentheses(glob)
            case "LSQUARE":
                raise NotImplementedError()
            case "LBRACE":
                return self.in_braces(glob)
            case "STR" | "TYPE" | "FIELD" | "BOOL" | "INT" | "FLOAT" | "FACTOR":
                return self.force_type(t, glob)
            case "USING":
                raise NotImplementedError()
            case "COMMENT" | "NEWLINE":
                pass
            case "NUM":
                if "." in token.value:
                    return UqVar("FLOAT", float(token.value))
                return UqVar("INT", int(token.value))
            case _:
                error.unexpected_token(token)
        return UqVar.default()

    def force_type(self, var_type: "VarType", glob: UqNamespace) -> UqVar:
        """Compulsively transform the type."""
        var_name = self.tokenizer.expect("ID").value
        var = self.define_var(var_name, glob)
        return var.force_type(var_type)

    def define_var(self, var_name: str, glob: UqNamespace) -> UqVar:
        """Define variable."""
        while token := self.tokenizer.next():
            match token.type:
                case "ID":
                    var = UqVar.default()
                    raise NotImplementedError()
                case "ASSIGN":
                    var = self.open_loop(glob)
                    var.setname(var_name)
        return var

    def eval_var(self, var: UqVar, glob: UqNamespace) -> UqVar:
        """Evaluate variable."""
        if var.is_function():
            token = self.tokenizer.next()
            match token.type:
                case "ID":
                    return self.eval_var(var.eval(glob[token.value]), glob)
                case "LPAR":
                    return var.eval(self.in_parentheses(glob))
                case "LBRACE":
                    return var.eval(self.in_braces(glob))
                case _:
                    error.unexpected_token(token)
        elif var.is_list():
            token = self.tokenizer.next()
            match token.type:
                case "LSQUARE":
                    return var.getitem(self.in_squares(glob))
                case "INT":
                    return var.getitem(UqVar.from_token(token))
                case _:
                    error.unexpected_token(token)
        return var

    def in_parentheses(self, glob: UqNamespace) -> UqVar:
        """Evaluate variable in parentheses."""
        raise NotImplementedError()

    def in_squares(self, glob: UqNamespace) -> UqVar:
        """Evaluate variable in square brackets."""
        raise NotImplementedError()

    def in_braces(self, glob: UqNamespace) -> UqVar:
        """Evaluate variable in braces."""
        raise NotImplementedError()
