"""Recursive-descent parser and AST nodes for AWL."""
from dataclasses import dataclass, field
from lexer import Token

@dataclass
class Statement:
    kind: str
    line: int

@dataclass
class Request(Statement):
    operation: str
    variable: str | None = None

@dataclass
class Save(Statement):
    variable: str
    source_operation: str
    field: str

@dataclass
class Workflow:
    name: str
    line: int
    statements: list[Statement] = field(default_factory=list)

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        token = self.current()
        if token.kind != "EOF":
            self.pos += 1
        return token

    def match(self, kind: str) -> bool:
        if self.current().kind == kind:
            self.advance()
            return True
        return False

    def expect(self, kind: str, description: str | None = None) -> Token:
        token = self.current()
        if token.kind != kind:
            wanted = description or kind
            actual = repr(token.value) if token.kind != "EOF" else "end of file"
            raise ParseError(
                f"Line {token.line}, column {token.column}: expected {wanted}, found {actual}"
            )
        return self.advance()

    def skip_newlines(self):
        while self.match("NEWLINE"):
            pass

    def parse(self) -> Workflow:
        self.skip_newlines()
        self.expect("WORKFLOW", "'WORKFLOW'")
        name = self.expect("IDENT", "workflow name")
        self.expect("LBRACE", "'{' after workflow name")
        self.skip_newlines()

        statements = []
        while self.current().kind not in ("RBRACE", "EOF"):
            statements.append(self.parse_statement())
            if self.current().kind == "NEWLINE":
                self.skip_newlines()
            elif self.current().kind != "RBRACE":
                token = self.current()
                raise ParseError(
                    f"Line {token.line}, column {token.column}: expected a new line or '}}'"
                )

        self.expect("RBRACE", "'}' to close workflow")
        self.skip_newlines()
        self.expect("EOF", "end of file (only one workflow is supported)")
        return Workflow(name.value, name.line, statements)

    def parse_statement(self) -> Statement:
        token = self.current()
        if self.match("REQUEST"):
            operation = self.expect("IDENT", "API operation name")
            variable = None
            if self.match("USING"):
                variable = self.expect("IDENT", "variable name").value
            return Request("REQUEST", token.line, operation.value, variable)

        if self.match("SAVE"):
            variable = self.expect("IDENT", "variable name")
            self.expect("FROM", "'FROM'")
            source = self.expect("IDENT", "source operation name")
            self.expect("DOT", "'.' between operation and response field")
            field = self.expect("IDENT", "response field name")
            return Save("SAVE", token.line, variable.value, source.value, field.value)

        raise ParseError(
            f"Line {token.line}, column {token.column}: expected REQUEST or SAVE statement"
        )

def parse(tokens: list[Token]) -> Workflow:
    return Parser(tokens).parse()
