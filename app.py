"""Flask web interface for the API Workflow Validator."""
from flask import Flask, render_template, request, jsonify
from pathlib import Path
from lexer import tokenize, LexError
from parser import parse, ParseError, Request, Save
from semantic import validate_semantics

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
EXAMPLE_META = [
    ("valid_user_management", "Valid — User Management", "valid"),
    ("valid_simple_session", "Valid — Simple Session", "valid"),
    ("invalid_order", "Invalid — Authentication Order", "semantic"),
    ("invalid_syntax", "Invalid — Missing Closing Brace", "syntax"),
    ("invalid_lexical", "Invalid — Unexpected Character", "lexical"),
    ("invalid_variable", "Invalid — Undefined Token", "semantic"),
    ("invalid_operation", "Invalid — Unknown API Operation", "semantic"),
    ("invalid_after_logout", "Invalid — Request After Logout", "semantic"),
]

def load_examples():
    examples = []
    for key, label, category in EXAMPLE_META:
        path = BASE_DIR / "examples" / f"{key}.awl"
        examples.append({"id": key, "label": label, "category": category, "source": path.read_text(encoding="utf-8")})
    return examples

DEFAULT_WORKFLOW = """# Example valid workflow
WORKFLOW UserManagement {
    REQUEST LOGIN
    SAVE token FROM LOGIN.access_token
    REQUEST GET_PROFILE USING token
    REQUEST UPDATE_PROFILE USING token
    REQUEST LOGOUT USING token
}"""

def validate_source(source: str) -> dict:
    result = {
        "lexical": {"status": "not_run", "message": "", "tokens": []},
        "syntax": {"status": "not_run", "message": ""},
        "semantic": {"status": "not_run", "message": "", "errors": []},
        "ast": [],
        "workflow_name": None,
        "statement_count": 0,
        "valid": False,
    }

    try:
        tokens = tokenize(source)
        visible_tokens = [t for t in tokens if t.kind != "EOF"]
        result["lexical"] = {
            "status": "passed",
            "message": f"Lexical analysis passed ({len(visible_tokens)} tokens).",
            "tokens": [
                {"kind": t.kind, "value": t.value, "line": t.line, "column": t.column}
                for t in visible_tokens
            ],
        }
    except LexError as exc:
        result["lexical"] = {"status": "failed", "message": str(exc), "tokens": []}
        result["semantic"]["message"] = "Skipped because lexical analysis failed."
        return result

    try:
        workflow = parse(tokens)
        result["syntax"] = {
            "status": "passed",
            "message": "Syntax analysis passed. The workflow follows the grammar.",
        }
        result["workflow_name"] = workflow.name
        result["statement_count"] = len(workflow.statements)
    except ParseError as exc:
        result["syntax"] = {"status": "failed", "message": str(exc)}
        result["semantic"]["message"] = "Skipped because syntax analysis failed."
        return result

    semantic_errors = validate_semantics(workflow)
    if semantic_errors:
        result["semantic"] = {
            "status": "failed",
            "message": f"Semantic analysis found {len(semantic_errors)} issue(s).",
            "errors": semantic_errors,
        }
    else:
        result["semantic"] = {
            "status": "passed",
            "message": "Semantic analysis passed. No semantic issues were found.",
            "errors": [],
        }

    for statement in workflow.statements:
        if isinstance(statement, Request):
            result["ast"].append({
                "kind": "REQUEST",
                "line": statement.line,
                "operation": statement.operation,
                "variable": statement.variable,
            })
        elif isinstance(statement, Save):
            result["ast"].append({
                "kind": "SAVE",
                "line": statement.line,
                "variable": statement.variable,
                "source_operation": statement.source_operation,
                "field": statement.field,
            })

    result["valid"] = (
        result["lexical"]["status"] == "passed"
        and result["syntax"]["status"] == "passed"
        and result["semantic"]["status"] == "passed"
    )
    return result

@app.get("/")
def index():
    return render_template("index.html", default_workflow=DEFAULT_WORKFLOW, examples=load_examples())

@app.post("/validate")
def validate():
    payload = request.get_json(silent=True) or {}
    source = payload.get("source", "")
    if not isinstance(source, str):
        return jsonify({"error": "Workflow source must be text."}), 400
    if not source.strip():
        return jsonify({"error": "Enter a workflow before validating."}), 400
    return jsonify(validate_source(source))

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
