#!/usr/bin/env python3
"""
Threadbare — AI Vulnerability Scanner CLI

Usage:
    python cli.py --path ./my-project --output reports/scan --format both
"""

import argparse
import os
import sys

from core.claude_client import ClaudeVulnScanner, DEFAULT_MODEL
from core.file_utils import discover_source_files, read_file_safely, get_language
from core.report_generator import generate_html_report, generate_markdown_report


def main():
    parser = argparse.ArgumentParser(description="Threadbare — AI-powered source code vulnerability scanner")
    parser.add_argument("--path", required=True, help="Path to the source code directory to scan")
    parser.add_argument("--output", default="reports/scan", help="Output report path (no extension)")
    parser.add_argument("--format", choices=["html", "markdown", "both"], default="both")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Claude model to use")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: {args.path} is not a valid directory")
        sys.exit(1)

    files = discover_source_files(args.path)
    if not files:
        print("No supported source files found to scan.")
        sys.exit(0)

    print(f"Found {len(files)} file(s) to scan.\n")

    scanner = ClaudeVulnScanner(model=args.model)
    all_findings = []

    for i, file_path in enumerate(files, 1):
        rel_path = os.path.relpath(file_path, args.path)
        print(f"[{i}/{len(files)}] Scanning {rel_path} ...", end=" ", flush=True)
        code = read_file_safely(file_path)
        language = get_language(file_path)
        findings = scanner.scan_file(rel_path, code, language)
        real_findings = [f for f in findings if f.get("title") != "Scan Error"]
        print(f"{len(real_findings)} finding(s)")
        all_findings.extend(findings)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    if args.format in ("markdown", "both"):
        md = generate_markdown_report(all_findings, args.path)
        with open(f"{args.output}.md", "w") as f:
            f.write(md)
        print(f"\nMarkdown report saved to {args.output}.md")

    if args.format in ("html", "both"):
        html_report = generate_html_report(all_findings, args.path)
        with open(f"{args.output}.html", "w") as f:
            f.write(html_report)
        print(f"HTML report saved to {args.output}.html")

    print(f"\nTotal findings: {len(all_findings)}")


if __name__ == "__main__":
    main()
