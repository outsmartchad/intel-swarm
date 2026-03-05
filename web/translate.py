#!/usr/bin/env python3
"""
Translate an intel-swarm markdown findings file to Traditional Chinese using Claude Haiku via CLI.
Usage: python3 translate.py <path-to-findings.md>
Output: same path with .zh.md extension
"""

import sys
import os
import subprocess
import tempfile

SYSTEM_DEFAULT = """You are a professional translator specialising in Traditional Chinese (繁體中文). You are translating open-source research summaries — journalism digests, policy notes, and market analysis — into Traditional Chinese for a bilingual readership.

Guidelines:
- Produce a complete, accurate Traditional Chinese translation of the entire document
- Keep URLs, dates, numbers, tickers, proper nouns, organisation names, and technical terms in English
- Preserve all markdown formatting exactly (##, **, -, etc.)
- Output ONLY the translated markdown with no preamble, commentary, or footnotes"""

SYSTEM_SPORTS = """You are a professional sports journalist and translator specialising in Traditional Chinese (繁體中文). You are translating sports news summaries — covering contracts, trades, injuries, and league developments — into Traditional Chinese for a bilingual readership.

Guidelines:
- Produce a complete, accurate Traditional Chinese translation of the entire document
- Keep URLs, dates, numbers, player names, team names, and technical terms in English
- Preserve all markdown formatting exactly (##, **, -, etc.)
- Output ONLY the translated markdown with no preamble, commentary, or footnotes"""

def get_system_prompt(filepath):
    """Pick the right system prompt based on researcher domain."""
    if "/sports/" in filepath or "sports" in os.path.basename(os.path.dirname(os.path.dirname(filepath))):
        return SYSTEM_SPORTS
    return SYSTEM_DEFAULT

def translate_file(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    with open(filepath) as f:
        content = f.read()

    if not content.strip():
        print(f"Empty: {filepath}")
        return

    out_path = filepath.replace(".md", ".zh.md")

    # Skip if already translated and newer
    if os.path.exists(out_path):
        if os.path.getmtime(out_path) >= os.path.getmtime(filepath):
            print(f"Up to date: {out_path}")
            return

    print(f"Translating → {out_path}")

    system = get_system_prompt(filepath)
    prompt = f"{system}\n\n---\n\n{content}"

    result = subprocess.run(
        ["claude", "--model", "claude-haiku-4-5", "-p", prompt],
        capture_output=True, text=True, timeout=300
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr[:200]}")
        sys.exit(1)

    translated = result.stdout.strip()

    with open(out_path, "w") as f:
        f.write(translated)

    print(f"Done: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: translate.py <findings.md>")
        sys.exit(1)
    translate_file(sys.argv[1])
