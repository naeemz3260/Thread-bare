# 🛡️ SentinelScan — AI-Powered Vulnerability Scanner

SentinelScan is a static application security testing (SAST) tool that uses **Claude**
(Anthropic's LLM) to read source code the way a human application security reviewer would —
finding real vulnerabilities and explaining, in plain English, *why* each line is insecure and
*how* to fix it.

Unlike traditional regex/pattern-based SAST tools, SentinelScan reasons about code context,
so it can catch logic-level issues (broken access control, IDOR, insecure deserialization)
that simple pattern matchers miss — and it produces a report a non-security engineer can
actually understand.

## Features

- 🔍 **Multi-language scanning** — Python, JavaScript/TypeScript, PHP, Java, Ruby, Go, C/C++, C#
- 🧠 **LLM-based analysis** — uses Claude to reason about each file, not just grep for patterns
- 📋 **Plain-English findings** — severity, CWE ID, vulnerable snippet, and concrete remediation
- 📊 **Two interfaces**:
  - **CLI** — scan any folder, get a Markdown + HTML report
  - **Web Dashboard** — drag-and-drop a `.zip`, watch a live scan console, browse results visually
- 🧪 **Includes deliberately vulnerable demo files in 4 languages** (`examples/vulnerable_app/`:
  `app.py`, `vulnerable.js`, `vulnerable.php`, `VulnerableServlet.java`) so you can test and demo
  it immediately — SQLi, XSS, command injection, insecure deserialization, path traversal,
  broken access control, hardcoded secrets.

## Project Structure

```
ai-vuln-scanner/
├── core/
│   ├── claude_client.py     # Calls the Anthropic API, parses structured findings
│   ├── file_utils.py        # Walks a directory, picks source files to scan
│   ├── prompts.py           # The security-review system prompt
│   └── report_generator.py  # Builds Markdown + HTML reports
├── templates/index.html      # Web dashboard UI
├── static/{style.css,app.js} # Dashboard styling + live-polling frontend logic
├── examples/vulnerable_app/  # Intentionally vulnerable demo target
├── cli.py                    # Command-line entry point
├── app.py                    # Flask web dashboard entry point
└── requirements.txt
```

## Setup

```bash
git clone <this-repo>
cd ai-vuln-scanner
pip install -r requirements.txt
cp .env.example .env   # then add your ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY=sk-ant-...   # or use a .env loader of your choice
```

## Usage — CLI

```bash
python cli.py --path examples/vulnerable_app --output reports/demo --format both
```

This scans every supported source file under the target path and writes:
- `reports/demo.md` — Markdown report
- `reports/demo.html` — Styled HTML report (dark theme, severity breakdown, per-finding cards)

Options:
| Flag | Description |
|---|---|
| `--path` | Directory to scan (required) |
| `--output` | Output report path, no extension (default `reports/scan`) |
| `--format` | `html`, `markdown`, or `both` (default `both`) |
| `--model` | Claude model to use (default `claude-sonnet-5`, also settable via `SCANNER_MODEL` env var) |

## Usage — Web Dashboard

```bash
python app.py
```

Open `http://localhost:5000`, zip up a project folder (or use the included
`examples/vulnerable_app`), drag it in, and watch the live scan console populate a
findings dashboard — grouped by severity, with the vulnerable code and the fix for each.

## How it works

1. `file_utils.py` walks the target directory and collects source files by extension,
   skipping `node_modules`, `.git`, build artifacts, and oversized/generated files.
2. Each file is sent to Claude individually with a system prompt (`prompts.py`) instructing
   it to act as an app-sec reviewer and return **structured JSON findings** — never free text.
3. `claude_client.py` calls the API, validates/repairs the JSON response, and retries on
   transient failures.
4. `report_generator.py` (CLI) or `app.js` (dashboard) renders the aggregated findings into
   a severity-sorted report.

## Why this project

This was built to demonstrate applied AI + application security skills for internship/job
applications — specifically: prompt engineering for structured security output, working with
the Anthropic API, and building a usable security tool end-to-end (not just a script).

## Disclaimer

This tool is for educational and portfolio purposes. The included vulnerable app is
intentionally insecure and must never be deployed anywhere internet-facing. LLM-based
findings should be validated by a human before being treated as a full security audit —
this is a supplement to, not a replacement for, professional pentesting.

## License

MIT — see [LICENSE](LICENSE).
