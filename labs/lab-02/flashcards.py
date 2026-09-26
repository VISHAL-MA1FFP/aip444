#!/usr/bin/env python3
"""
flashcards: ACE flashcard generator from course notes.
AIP444 - Lab 02
"""

import os
import sys
import re
import argparse
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

# ----------------------------------------------------------------------------
# CONFIG — edit these two lines with your own info
# ----------------------------------------------------------------------------
STUDENT_NAME = "VISHAL SHARMA"       # <-- replace this
STUDENT_ID = "189273238"             # <-- replace this

# ----------------------------------------------------------------------------
# MODEL CONFIG — try free first, fall back to cheap paid version on 429
# ----------------------------------------------------------------------------
FREE_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
PAID_FALLBACK_MODEL = "meta-llama/llama-3.3-70b-instruct"

# Approximate OpenRouter pricing for the paid fallback, per 1M tokens
PAID_INPUT_COST_PER_M = 0.10
PAID_OUTPUT_COST_PER_M = 0.32


def print_header():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("AIP444 Fall 2026 - Lab 02")
    print(f"flashcards: Developed by {STUDENT_NAME} - {STUDENT_ID}")
    print(f"Run Date: {now}")
    print("-" * 64)


def load_api_key():
    load_dotenv(find_dotenv())
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found")
        sys.exit(1)
    return api_key


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate ACE flashcards from course notes"
    )
    parser.add_argument(
        "notes_path",
        help="Path to the notes file (Markdown, HTML, or text)",
    )
    parser.add_argument(
        "--cards",
        type=int,
        default=3,
        help="Number of flashcards to generate (1-5, default: 3)",
    )
    args = parser.parse_args()

    if args.cards < 1 or args.cards > 5:
        parser.error("--cards must be between 1 and 5")

    return args


def get_file_contents(path, description):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: {description} not found: {path}")
        sys.exit(1)
    except Exception as err:
        print(f"❌ Error reading {description}: {path}")
        print(f"   {err}")
        sys.exit(1)


def build_user_prompt(notes_content, num_cards):
    return f"""Generate exactly {num_cards} ACE flashcard(s) from the course notes below.

Remember:
- Only use information that literally appears in the notes.
- EVIDENCE must be an exact, word-for-word quote from the notes.
- Expand every acronym in ANSWER on first use.
- MISCONCEPTION must be a first-person quote from a confused student.
- If the notes don't support {num_cards} good card(s), generate fewer and explain why.
- If the notes are empty or insufficient, don't generate any cards — explain what's missing instead.

<notes>
{notes_content}
</notes>

Now generate exactly {num_cards} ACE flashcard(s) following the format and
reasoning workflow from your instructions. Only use information found in
the <notes> above — do not invent anything.

REMINDER: You must output exactly {num_cards} complete card(s), numbered
CARD 1 through CARD {num_cards}, one after another, in this single response.
Do not stop after the first card if more were requested."""


def call_model(client, model, system_prompt, user_prompt, max_tokens):
    completion = client.chat.completions.create(
        model=model,
        temperature=0.3,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    output = completion.choices[0].message.content
    usage = getattr(completion, "usage", None)
    return output, usage


def generate_flashcards(client, system_prompt, user_prompt, num_cards):
    """Try the free model first; fall back to the cheap paid version on a 429."""
    # Give the model enough room for reasoning + all requested cards.
    # ~900 tokens per card plus a buffer for the reasoning/thinking text.
    max_tokens = min(4096, 1200 + num_cards * 900)
    try:
        print(f"✍️  Generating with {FREE_MODEL}...\n")
        return call_model(client, FREE_MODEL, system_prompt, user_prompt, max_tokens), FREE_MODEL
    except Exception as e:
        error_text = str(e)
        if "429" in error_text or "unavailable for free" in error_text:
            print(f"  (free model unavailable/rate-limited, falling back to {PAID_FALLBACK_MODEL})\n")
            return call_model(client, PAID_FALLBACK_MODEL, system_prompt, user_prompt, max_tokens), PAID_FALLBACK_MODEL
        print(f"❌ Error generating flashcards: {e}")
        sys.exit(1)


def print_cost_estimate(model, usage):
    if usage is None:
        return
    prompt_tokens = getattr(usage, "prompt_tokens", 0)
    completion_tokens = getattr(usage, "completion_tokens", 0)

    if model == PAID_FALLBACK_MODEL:
        cost = (
            prompt_tokens / 1_000_000 * PAID_INPUT_COST_PER_M
            + completion_tokens / 1_000_000 * PAID_OUTPUT_COST_PER_M
        )
        print(f"\n💰 Estimated cost: ${cost:.6f} "
              f"({prompt_tokens} prompt tokens, {completion_tokens} completion tokens)")
    else:
        print(f"\n💰 Cost: $0.00 (free model — "
              f"{prompt_tokens} prompt tokens, {completion_tokens} completion tokens)")


def extract_cards(output):
    # Primary: the exact required format.
    cards = re.findall(r"(=== CARD \d+ ===.*?===)", output, re.DOTALL)
    if cards:
        return cards

    # Fallback: tolerate the model using a Markdown heading instead of the
    # literal === delimiter (e.g. "### CARD 1"), splitting on card boundaries.
    loose_matches = list(re.finditer(r"^#{1,3}\s*CARD\s+\d+", output, re.MULTILINE | re.IGNORECASE))
    if not loose_matches:
        return []

    fallback_cards = []
    for i, match in enumerate(loose_matches):
        start = match.start()
        end = loose_matches[i + 1].start() if i + 1 < len(loose_matches) else len(output)
        fallback_cards.append(output[start:end].strip())
    return fallback_cards


def main():
    print_header()

    api_key = load_api_key()
    args = parse_arguments()

    system_prompt = get_file_contents("SYSTEM_PROMPT.md", "System prompt file")
    notes_content = get_file_contents(args.notes_path, "Notes file")

    user_prompt = build_user_prompt(notes_content, args.cards)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    (output, usage), model_used = generate_flashcards(client, system_prompt, user_prompt, args.cards)

    cards = extract_cards(output)

    if not cards:
        # No cards found — this is the expected path for edge cases
        # (empty/insufficient notes). Show the model's explanation instead.
        print("❌ No cards found in output. Model's response:\n")
        print(output)
    else:
        print(f"✅ Generated {len(cards)} flashcard(s):\n")
        for card in cards:
            print(card)
            print()

    print_cost_estimate(model_used, usage)


if __name__ == "__main__":
    main()