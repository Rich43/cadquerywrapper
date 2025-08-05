#!/usr/bin/env python3
"""Interactive menu for running example scripts."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def list_examples() -> list[Path]:
    return sorted(p for p in EXAMPLES_DIR.iterdir() if p.suffix == ".py")


def choose_example(examples: list[Path]) -> Path | None:
    for idx, ex in enumerate(examples, 1):
        print(f"{idx}. {ex.name}")
    print("0. Exit")
    choice = input("Select an example: ")
    if choice == "0":
        return None
    try:
        idx = int(choice) - 1
    except ValueError:
        return None
    if 0 <= idx < len(examples):
        return examples[idx]
    return None


def run_example(example: Path) -> None:
    print(f"\nRunning {example.name}\n{'-' * (8 + len(example.name))}")
    subprocess.run([sys.executable, str(example)], check=True)


def main() -> None:
    examples = list_examples()
    if not examples:
        print("No examples found.")
        return
    while True:
        selection = choose_example(examples)
        if selection is None:
            break
        run_example(selection)


if __name__ == "__main__":
    main()
