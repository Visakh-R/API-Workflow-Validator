"""Command-line entry point for API Workflow Validator."""
import argparse
from pathlib import Path
from lexer import tokenize, LexError
from parser import parse, ParseError
from semantic import validate_semantics

def validate_file(path: Path) -> int:
    print("=" * 58)
    print("          API WORKFLOW VALIDATOR")
    print("=" * 58)
    print(f"Input file: {path}\n")

    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"FILE ERROR: Could not read '{path}': {exc}")
        return 2

    try:
        tokens = tokenize(source)
    except LexError as exc:
        print("LEXICAL ANALYSIS: FAILED")
        print(f"  {exc}")
        return 1

    print(f"LEXICAL ANALYSIS: PASSED ({sum(t.kind != 'EOF' for t in tokens)} tokens)")

    try:
        workflow = parse(tokens)
    except ParseError as exc:
        print("SYNTAX ANALYSIS: FAILED")
        print(f"  {exc}")
        print("\nSemantic analysis skipped because the syntax is invalid.")
        return 1

    print("SYNTAX ANALYSIS: PASSED")
    print(f"Workflow name: {workflow.name}")
    print(f"Statements found: {len(workflow.statements)}")

    errors = validate_semantics(workflow)
    if errors:
        print("SEMANTIC ANALYSIS: FAILED")
        for error in errors:
            print(f"  - {error}")
        print(f"\nRESULT: FAILED ({len(errors)} semantic issue(s))")
        return 1

    print("SEMANTIC ANALYSIS: PASSED")
    print("\nABSTRACT SYNTAX TREE (AST)")
    print(f"Workflow({workflow.name})")
    for statement in workflow.statements:
        if hasattr(statement, "operation"):
            suffix = f" USING {statement.variable}" if statement.variable else ""
            print(f"  └── REQUEST {statement.operation}{suffix}")
        else:
            print(
                f"  └── SAVE {statement.variable} FROM "
                f"{statement.source_operation}.{statement.field}"
            )

    print("\nRESULT: VALID WORKFLOW")
    return 0

def main():
    cli = argparse.ArgumentParser(
        description="Validate an API Workflow Language (.awl) file."
    )
    cli.add_argument(
        "file", nargs="?", default="workflow.awl",
        help="workflow file path (default: workflow.awl)"
    )
    args = cli.parse_args()
    raise SystemExit(validate_file(Path(args.file)))

if __name__ == "__main__":
    main()
