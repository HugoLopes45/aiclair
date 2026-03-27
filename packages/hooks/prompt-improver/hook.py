#!/usr/bin/env python3
"""
prompt-improver hook — evaluates prompt clarity and enriches vague prompts.
Imports shared utilities from packages.core.
"""
import sys
from pathlib import Path

# Allow running as standalone script from any working directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from packages.core.bypass import check_bypass
from packages.core.hook import build_evaluation_wrapper, read_prompt, write_output

SKILL_NAME = "prompt-improver"


def main():
    prompt = read_prompt()
    is_bypass, clean_prompt = check_bypass(prompt)

    if is_bypass:
        write_output(clean_prompt)
        return

    wrapper = build_evaluation_wrapper(prompt, SKILL_NAME)
    write_output(wrapper)


if __name__ == "__main__":
    main()
