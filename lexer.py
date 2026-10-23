"""Lexical analyzer for the API Workflow Language (AWL)."""
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int

TOKEN_SPEC = [
    ("COMMENT",   r"\#[^\n]*"),
    ("NEWLINE",   r"\n"),
    ("SKIP",      r"[ \t\r]+"),
    ("LBRACE",    r"\{"),
    ("RBRACE",    r"\}"),
    ("DOT",       r"\."),
    ("IDENT",     r"[A-Za-z_][A-Za-z0-9_]*"),
    ("MISMATCH",  r"."),
]
TOKEN_RE = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))

KEYWORDS = {"WORKFLOW", "REQUEST", "SAVE", "FROM", "USING"}

class LexError(Exception):
    pass

def tokenize(source: str) -> list[Token]:
    """Convert source text to tokens, preserving line and column positions."""
    tokens = []
    line = 1
    line_start = 0

    for match in TOKEN_RE.finditer(source):
        kind = match.lastgroup
        value = match.group()
        column = match.start() - line_start + 1

        if kind == "NEWLINE":
            tokens.append(Token("NEWLINE", "\\n", line, column))
            line += 1
            line_start = match.end()
        elif kind in ("SKIP", "COMMENT"):
            continue
        elif kind == "IDENT" and value in KEYWORDS:
            tokens.append(Token(value, value, line, column))
        elif kind == "IDENT":
            tokens.append(Token("IDENT", value, line, column))
        elif kind == "MISMATCH":
            raise LexError(f"Line {line}, column {column}: unexpected character {value!r}")
        else:
            tokens.append(Token(kind, value, line, column))

    tokens.append(Token("EOF", "", line, 1))
    return tokens
