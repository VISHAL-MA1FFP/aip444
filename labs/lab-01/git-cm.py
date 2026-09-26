#!/usr/bin/env python3
"""
git-cm: An LLM-powered git commit message generator.
AIP444 - Lab 01
"""

import os
import sys
import subprocess
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

# ----------------------------------------------------------------------------
# CONFIG — edit these two lines with your own info
# ----------------------------------------------------------------------------
STUDENT_NAME = "VISHAL SHARMA"       # <-- replace this
STUDENT_ID = "189273238"        # <-- replace this

# ----------------------------------------------------------------------------
# MODEL CONFIG — two models from two different providers, both free/cheap
# ----------------------------------------------------------------------------
MODEL_A =  "google/gemma-4-31b-it"    # Google
MODEL_B =   "meta-llama/llama-3.3-70b-instruct" 

DEFAULT_MODEL = MODEL_A

# ----------------------------------------------------------------------------
# SYSTEM PROMPTS
# ----------------------------------------------------------------------------
DEFAULT_SYSTEM_PROMPT = (
    "You are an LLM running in a CLI tool, which writes semantic commit "
    "messages for the user. You will be given a git diff. You must output "
    "ONLY the commit message using the Conventional Commits standard format "
    "(e.g., 'feat: add logging'). Respond in plain text suitable for pasting "
    "into git commit -m '...your commit message...'; just the plain text "
    "commit message with no Markdown, no rationale about why you chose it, etc."
)

CREATIVE_SYSTEM_PROMPT = (
    "You are an LLM running in a CLI tool, which writes commit messages for "
    "the user in the style of a 17th century pirate. You will be given a git "
    "diff. Use Gitmoji (an emoji prefix, e.g. '✨') and write the commit "
    "message using exaggerated pirate slang (e.g., 'Arrr', 'ye', 'be', "
    "'plunder'), while still briefly conveying what actually changed in the "
    "code. Respond in plain text suitable for pasting into "
    "git commit -m '...your commit message...'; just the plain text commit "
    "message with no Markdown and no extra commentary."
)


def print_header():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("AIP444 Fall 2026 - Lab 01")
    print(f"git-cm: Developed by {STUDENT_NAME} - {STUDENT_ID}")
    print(f"Run Date: {now}")
    print("-" * 64)


def load_api_key():
    load_dotenv(find_dotenv())
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found")
        sys.exit(1)
    return api_key


def get_staged_diff():
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            )
        diff = result.stdout.strip()
        if not diff:
            print("❌ No staged changes found")
            sys.exit(1)
        print(f"✅ Diff found: {len(diff)} characters")
        return diff
    except subprocess.CalledProcessError:
        print("❌ Not a git repo.")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ git is not installed or not on PATH.")
        sys.exit(1)


def generate_commit_message(client, model, system_prompt, diff, temperature):
    try:
        completion = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": diff},
            ],
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error generating message with {model}: {e}"
    
     # test change 

def main():
    print_header()

    api_key = load_api_key()
    diff = get_staged_diff()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    is_creative = "--creative" in sys.argv

    if is_creative:
        print("\n🏴‍☠️ Creative mode enabled — generating two pirate-style options...\n")
        system_prompt = CREATIVE_SYSTEM_PROMPT
        temperature = 1.3

        msg_a = generate_commit_message(client, MODEL_A, system_prompt, diff, temperature)
        msg_b = generate_commit_message(client, MODEL_B, system_prompt, diff, temperature)

        print(f"Option 1 ({MODEL_A}):")
        print(msg_a)
        print()
        print(f"Option 2 ({MODEL_B}):")
        print(msg_b)
    else:
        print("\n✍️  Generating commit message...\n")
        system_prompt = DEFAULT_SYSTEM_PROMPT
        temperature = 0.1

        msg = generate_commit_message(client, DEFAULT_MODEL, system_prompt, diff, temperature)
        print(f"Commit message ({DEFAULT_MODEL}):")
        print(msg)


if __name__ == "__main__":
    main()