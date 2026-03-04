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

SYSTEM = "You are a professional translator. Translate the following intelligence research findings from English to Traditional Chinese (繁體中文). Keep all URLs, dates, numbers, tickers (BTC, ETH, SOL, etc.), proper nouns, org names, and technical terms in English. Preserve all markdown formatting exactly. Only output the translated markdown — nothing else."

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

    prompt = f"{SYSTEM}\n\n---\n\n{content}"

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
