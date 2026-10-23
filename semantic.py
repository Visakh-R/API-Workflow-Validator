"""Semantic validation for API workflow ASTs."""
from parser import Workflow, Request, Save

# Demonstration registry. Extend this to match the APIs in your own workflow.
API_RULES = {
    "LOGIN": {"requires_auth": False, "provides_auth": True},
    "GET_PROFILE": {"requires_auth": True, "provides_auth": False},
    "UPDATE_PROFILE": {"requires_auth": True, "provides_auth": False},
    "LOGOUT": {"requires_auth": True, "provides_auth": False},
    "LIST_PRODUCTS": {"requires_auth": False, "provides_auth": False},
}

def validate_semantics(workflow: Workflow) -> list[str]:
    errors = []
    variables: dict[str, tuple[str, int]] = {}
    executed: set[str] = set()
    authenticated = False
    logged_out = False

    for statement in workflow.statements:
        if isinstance(statement, Request):
            op = statement.operation
            rule = API_RULES.get(op)
            if rule is None:
                errors.append(
                    f"Line {statement.line}: unknown API operation '{op}'. "
                    f"Known operations: {', '.join(API_RULES)}."
                )
                continue

            if statement.variable:
                if statement.variable not in variables:
                    errors.append(
                        f"Line {statement.line}: variable '{statement.variable}' "
                        "is used before it is defined."
                    )
                elif variables[statement.variable][0] != "LOGIN.access_token":
                    errors.append(
                        f"Line {statement.line}: variable '{statement.variable}' "
                        "is not recognized as an authentication token."
                    )

            if rule["requires_auth"] and not authenticated:
                reason = "after LOGOUT" if logged_out else "before LOGIN"
                errors.append(
                    f"Line {statement.line}: {op} requires authentication but appears {reason}."
                )

            if op == "LOGIN":
                authenticated = True
                logged_out = False
            elif op == "LOGOUT":
                if authenticated:
                    authenticated = False
                    logged_out = True
                else:
                    errors.append(
                        f"Line {statement.line}: LOGOUT cannot run before a successful LOGIN."
                    )

            executed.add(op)

        elif isinstance(statement, Save):
            if statement.source_operation not in executed:
                errors.append(
                    f"Line {statement.line}: cannot save '{statement.variable}' from "
                    f"'{statement.source_operation}' because that operation has not run earlier."
                )
                continue

            if statement.source_operation == "LOGIN" and statement.field == "access_token":
                variables[statement.variable] = ("LOGIN.access_token", statement.line)
            else:
                errors.append(
                    f"Line {statement.line}: unsupported response field "
                    f"'{statement.source_operation}.{statement.field}'."
                )

    if not workflow.statements:
        errors.append(f"Line {workflow.line}: workflow must contain at least one statement.")

    return errors
