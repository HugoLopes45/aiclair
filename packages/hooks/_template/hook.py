#!/usr/bin/env python3
"""
<hook-name> — <one-line description>

Replace this docstring with your hook's purpose.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from packages.core.bypass import check_bypass
from packages.core.hook import build_evaluation_wrapper, read_prompt, write_output

SKILL_NAME = "<hook-name>"  # Replace with your hook's skill name


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
