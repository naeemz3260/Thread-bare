"""
Turns a flat list of findings into a Markdown report and a self-contained HTML report.
"""

import html
from collections import Counter
from datetime import datetime

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Info"]

SEVERITY_COLORS = {
    "Critical": "#dc2626",
    "High": "#ea580c",
    "Medium": "#d97706",
    "Low": "#2563eb",
    "Info": "#6b7280",
}


def _sort_findings(findings: list[dict]) -> list[dict]:
    return sorted(
        findings,
        key=lambda f: SEVERITY_ORDER.index(f.get("severity", "Info"))
        if f.get("severity") in SEVERITY_ORDER
        else len(SEVERITY_ORDER),
    )


def generate_markdown_report(findings: list[dict], target_path: str) -> str:
    findings = _sort_findings(findings)
    counts = Counter(f.get("severity", "Info") for f in findings)
    lines = []
    lines.append(f"# AI Vulnerability Scan Report\n")
    lines.append(f"**Target:** `{target_path}`  ")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"**Total findings:** {len(findings)}\n")

    lines.append("## Summary\n")
    lines.append("| Severity | Count |")
    lines.append("|---|---|")
    for sev in SEVERITY_ORDER:
        lines.append(f"| {sev} | {counts.get(sev, 0)} |")
    lines.append("")

    lines.append("## Findings\n")
    for i, f in enumerate(findings, 1):
        lines.append(f"### {i}. {f.get('title', 'Unknown')} — {f.get('severity', 'Info')}")
        lines.append(f"- **File:** `{f.get('file', '')}` (line {f.get('line', '?')})")
        if f.get("cwe"):
            lines.append(f"- **CWE:** {f.get('cwe')}")
        lines.append(f"\n**Why this is a problem:**\n{f.get('explanation', '')}\n")
        if f.get("vulnerable_code"):
            lines.append("**Vulnerable code:**")
            lines.append(f"```\n{f.get('vulnerable_code')}\n```")
        if f.get("remediation"):
            lines.append(f"**Remediation:**\n{f.get('remediation')}\n")
        lines.append("---\n")

    return "\n".join(lines)


def generate_html_report(findings: list[dict], target_path: str) -> str:
    findings = _sort_findings(findings)
    counts = Counter(f.get("severity", "Info") for f in findings)

    summary_cards = "".join(
        f"""<div class="card" style="border-top:4px solid {SEVERITY_COLORS[sev]}">
                <div class="card-count">{counts.get(sev, 0)}</div>
                <div class="card-label">{sev}</div>
            </div>"""
        for sev in SEVERITY_ORDER
    )

    finding_rows = ""
    for i, f in enumerate(findings, 1):
        sev = f.get("severity", "Info")
        color = SEVERITY_COLORS.get(sev, "#6b7280")
        cwe_html = f'<span class="cwe">{html.escape(f.get("cwe") or "")}</span>' if f.get("cwe") else ""
        finding_rows += f"""
        <div class="finding">
            <div class="finding-header">
                <span class="badge" style="background:{color}">{sev}</span>
                <span class="finding-title">{i}. {html.escape(f.get('title', 'Unknown'))}</span>
                {cwe_html}
            </div>
            <div class="finding-meta">{html.escape(f.get('file', ''))} : line {f.get('line', '?')}</div>
            <div class="finding-body">
                <p class="explanation">{html.escape(f.get('explanation', ''))}</p>
                {f'<pre class="code">{html.escape(f.get("vulnerable_code",""))}</pre>' if f.get('vulnerable_code') else ''}
                <div class="remediation">
                    <strong>Fix:</strong>
                    <p>{html.escape(f.get('remediation', ''))}</p>
                </div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AI Vulnerability Scan Report</title>
<style>
    :root {{
        --bg: #0f172a;
        --panel: #1e293b;
        --text: #e2e8f0;
        --muted: #94a3b8;
        --accent: #38bdf8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
        background: var(--bg);
        color: var(--text);
        font-family: 'Segoe UI', system-ui, sans-serif;
        margin: 0;
        padding: 40px 20px;
    }}
    .container {{ max-width: 900px; margin: 0 auto; }}
    h1 {{ font-size: 28px; margin-bottom: 4px; }}
    .subtitle {{ color: var(--muted); margin-bottom: 30px; font-size: 14px; }}
    .summary {{ display: flex; gap: 16px; margin-bottom: 40px; flex-wrap: wrap; }}
    .card {{
        background: var(--panel);
        border-radius: 10px;
        padding: 16px 24px;
        min-width: 100px;
        text-align: center;
    }}
    .card-count {{ font-size: 28px; font-weight: 700; }}
    .card-label {{ color: var(--muted); font-size: 13px; margin-top: 4px; }}
    .finding {{
        background: var(--panel);
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 18px;
    }}
    .finding-header {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
    .badge {{
        color: white;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        text-transform: uppercase;
    }}
    .finding-title {{ font-size: 17px; font-weight: 600; }}
    .cwe {{ color: var(--muted); font-size: 12px; border: 1px solid var(--muted); padding: 2px 8px; border-radius: 6px; }}
    .finding-meta {{ color: var(--accent); font-size: 13px; font-family: monospace; margin: 8px 0 12px; }}
    .explanation {{ line-height: 1.6; margin: 0 0 12px; }}
    .code {{
        background: #0b1120;
        color: #f87171;
        padding: 12px 16px;
        border-radius: 8px;
        overflow-x: auto;
        font-size: 13px;
        margin-bottom: 12px;
    }}
    .remediation {{
        background: rgba(56, 189, 248, 0.08);
        border-left: 3px solid var(--accent);
        padding: 10px 16px;
        border-radius: 0 8px 8px 0;
    }}
    .remediation p {{ margin: 4px 0 0; line-height: 1.5; }}
    .empty {{ color: var(--muted); text-align: center; padding: 60px 0; }}
</style>
</head>
<body>
<div class="container">
    <h1>🛡️ AI Vulnerability Scan Report</h1>
    <div class="subtitle">Target: {html.escape(target_path)} &nbsp;•&nbsp; Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    <div class="summary">{summary_cards}</div>
    {finding_rows if findings else '<div class="empty">No vulnerabilities found. 🎉</div>'}
</div>
</body>
</html>"""
