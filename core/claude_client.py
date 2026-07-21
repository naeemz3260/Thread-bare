"""
Thin wrapper around the Anthropic API used to send source files for security analysis
and parse the structured JSON response back into Python objects.
"""

import json
import os
import re
import time

import anthropic

from .prompts import SYSTEM_PROMPT, build_user_prompt

DEFAULT_MODEL = os.environ.get("SCANNER_MODEL", "claude-sonnet-5")


class ClaudeVulnScanner:
    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "No API key found. Set the ANTHROPIC_API_KEY environment variable "
                "or pass api_key explicitly."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def _extract_json(self, text: str) -> dict:
        """Be defensive: strip markdown fences if the model adds them anyway."""
        text = text.strip()
        text = re.sub(r"^```(json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # last resort: grab the outermost {...}
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise

    def scan_file(self, file_path: str, code: str, language: str, retries: int = 2) -> list[dict]:
        """Send one file's code to Claude and return a list of finding dicts."""
        user_prompt = build_user_prompt(file_path, code, language)

        last_error = None
        for attempt in range(retries + 1):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                raw_text = "".join(
                    block.text for block in response.content if block.type == "text"
                )
                parsed = self._extract_json(raw_text)
                findings = parsed.get("findings", [])
                for f in findings:
                    f["file"] = file_path
                return findings
            except Exception as e:  # noqa: BLE001
                last_error = e
                time.sleep(1.5 * (attempt + 1))

        # If every retry failed, surface it as a single "scan error" finding rather than crashing
        return [
            {
                "file": file_path,
                "line": 0,
                "title": "Scan Error",
                "severity": "Info",
                "cwe": None,
                "explanation": f"Could not analyze this file automatically: {last_error}",
                "vulnerable_code": "",
                "remediation": "Re-run the scan, or review this file manually.",
            }
        ]
