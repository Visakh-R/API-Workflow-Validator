# API Workflow Validator — Flask Web Edition

A Compiler Design project that validates API workflow descriptions written in API Workflow Language (AWL). It demonstrates lexical analysis, recursive-descent syntax analysis, semantic checks, AST display, token output, and a browser-based interface.

## Requirements
- Python 3.10 or newer
- Flask (`python -m pip install -r requirements.txt`)

## Run in VS Code
1. Extract the ZIP and open the `API-Workflow-Validator` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Install dependencies: `python -m pip install -r requirements.txt`
4. Start the site: `python app.py`
5. Open `http://127.0.0.1:5000` in your browser. Keep the terminal running.

The command-line validator is also available with `python main.py` and `python main.py examples/invalid_order.awl`.

## Built-in examples
The web interface includes eight selectable test cases under **Example workflows**:
- Valid — User Management
- Valid — Simple Session
- Invalid — Authentication Order
- Invalid — Missing Closing Brace
- Invalid — Unexpected Character
- Invalid — Undefined Token
- Invalid — Unknown API Operation
- Invalid — Request After Logout

Choose an example, click **Load example**, and then click **Validate workflow**. The examples are source files in `examples/`; the app loads their actual text and submits it to the compiler. Results are not hardcoded.

## Supported AWL statements
- `WORKFLOW Name { ... }` declares a workflow.
- `REQUEST OPERATION` declares an API operation.
- `REQUEST OPERATION USING variable` declares an operation using a variable.
- `SAVE variable FROM LOGIN.access_token` saves a simulated token.
- `#` starts a comment.

## Compiler phases
1. **Lexical analysis:** tokenizes source and detects unexpected characters.
2. **Syntax analysis:** checks grammar and builds parsed statement nodes.
3. **Semantic analysis:** checks operation names, authentication order, saved token variables, and requests after logout.
4. **AST and report:** displays parsed statements, tokens, and diagnostics.

## Run tests
`python -m unittest discover -s tests -v`

## Scope note
This is a teaching validator for simulated API workflow descriptions. It does not send real HTTP requests to external APIs.

https://api-workflow-validator-1.onrender.com
