#!/usr/bin/env python3
"""
Test that the core violations colleague_1 mentioned are fixed.

Specifically checks:
1. chirality/domain/semantics/lens.py has no messages= usage
2. chirality/infrastructure/semantics/resolvers.py has no messages= usage  
3. Core adapter uses client.responses.create not client.chat.completions.create
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fails = []

def check_file_clean(filepath, patterns, description):
    """Check that a file contains none of the forbidden patterns."""
    try:
        for pattern in patterns:
            result = subprocess.run(
                ["rg", "-n", pattern, str(filepath)],
                capture_output=True,
                text=True,
                cwd=ROOT
            )
            if result.stdout.strip():
                fails.append(f"{description} found in {filepath}:\n{result.stdout}")
    except FileNotFoundError:
        fails.append("Error: ripgrep (rg) is not installed")

print("🔍 Testing core violations are fixed...")

# Test the two specific files colleague_1 mentioned
print("  • Checking lens.py is clean...")
check_file_clean(
    "chirality/domain/semantics/lens.py",
    [r'\bmessages\s*=', r'call_responses_api.*messages='],
    "FORBIDDEN: messages= usage"
)

print("  • Checking resolvers.py is clean...")
check_file_clean(
    "chirality/infrastructure/semantics/resolvers.py", 
    [r'\bmessages\s*=', r'call_responses_api.*messages='],
    "FORBIDDEN: messages= usage"
)

# Test core adapter uses Responses API
print("  • Checking core adapter uses Responses API...")
check_file_clean(
    "chirality/infrastructure/llm/openai_adapter.py",
    [r'self\.client\.chat\.completions\.create'],
    "FORBIDDEN: Chat Completions API usage"
)

# Verify Responses API is used
try:
    result = subprocess.run(
        ["rg", "-n", r'self\.client\.responses\.create', "chirality/infrastructure/llm/openai_adapter.py"],
        capture_output=True,
        text=True,
        cwd=ROOT
    )
    if not result.stdout.strip():
        fails.append("ERROR: No client.responses.create usage found in adapter")
    else:
        print(f"  ✅ Found {len(result.stdout.strip().split(chr(10)))} uses of client.responses.create")
except FileNotFoundError:
    fails.append("Error: ripgrep (rg) is not installed")

if fails:
    print("\n❌ Core violations still found:")
    for fail in fails:
        print(f"\n{fail}")
    exit(1)

print("\n✅ CORE VIOLATIONS FIXED!")
print("✅ lens.py and resolvers.py no longer use messages=")
print("✅ Core adapter uses client.responses.create exclusively")
print("✅ Ready for colleague_1 verification")