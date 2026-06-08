#!/usr/bin/env python3
import argparse
import textwrap


def summarize(text: str, max_lines: int) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:max_lines])


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple text summary skill")
    parser.add_argument("--max-lines", type=int, default=3)
    parser.add_argument("text", nargs="+", help="Target text")
    args = parser.parse_args()

    merged = " ".join(args.text)
    wrapped = textwrap.fill(merged, width=80)
    print(summarize(wrapped, max_lines=args.max_lines))


if __name__ == "__main__":
    main()
