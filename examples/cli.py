#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI version of 5-letter Russian word search (Wordle helper).

Smart argument parsing (order doesn't matter):
  -абв       gray (excluded letters)
  +где       yellow (required letters)
  _а___      pattern (green, 5 characters with '_')
  1а5б       antipattern (position + forbidden letters)

Examples:
  python examples/cli.py -нзф +ки _а___ 2к
  python examples/cli.py +ки -нзф 2к _а___    # order doesn't matter
  python examples/cli.py -абв +где            # without pattern

Notes:
  - By default 'ё' is replaced with 'е'
  - Supports --sort flag for sorting (freq/alpha/none)
"""

import argparse
import sys
import os

# Add parent directory to path for core imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import (
    load_lexicon,
    get_search_params,
    filter_words,
    sort_by_frequency,
)


def parse_args():
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(
        description="Search for 5-letter Russian words (Wordle helper)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Smart argument parsing (order doesn't matter):
  -абв       gray (excluded)
  +где       yellow (required)
  _а___      pattern (green, 5 characters with '_')
  1а5б       antipattern (position + forbidden letters)

Examples:
  %(prog)s -нзф +ки _а___ 2к
  %(prog)s +ки -нзф 2к _а___    # order doesn't matter
  %(prog)s -абв +где            # without pattern
""",
    )
    p.add_argument(
        "--sort",
        choices=["freq", "alpha", "none"],
        help="Sort results (freq=frequency, alpha=alphabetical, none=original order)"
    )
    p.add_argument(
        "args",
        nargs="*",
        help="Search parameters (-abc +def __w__ 1z)"
    )

    return p.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Show help if no arguments
    if not args.args:
        print("No search parameters provided. Use -h for help.")
        return

    # Join args into single string for parsing
    input_text = " ".join(args.args)

    # Load lexicon
    lexicon_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'lexicon_ru_5.jsonl.gz')
    try:
        all_words, freq_map = load_lexicon(lexicon_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Parse search parameters
    params = get_search_params(input_text)

    print("\n=== Search for 5-letter Russian words ===")
    print("Parameters:")
    print(f"  Excluded letters:   {''.join(sorted(params['excluded'])) or 'none'}")
    print(f"  Required letters:   {''.join(sorted(params['must_have'])) or 'none'}")
    print(f"  Pattern:            {params['pattern'] or 'none'}")
    print(f"  Antipattern:        {params['raw_antipattern'] or 'none'}")

    # Check for conflicts
    if params['conflicts']:
        print("\nConflicts detected:")
        for msg in params['conflicts']:
            print(f"  - {msg}")
        print("Search aborted.")
        return

    # Filter words
    filtered_words, fstats = filter_words(
        all_words,
        params['must_have'],
        params['excluded'],
        params['pattern'],
        params['antipattern_constraints']
    )

    print("\nFiltering:")
    print(f"  Filtered by 'gray':      {fstats['excluded']}")
    print(f"  Filtered by 'yellow':    {fstats['must_have']}")
    print(f"  Filtered by pattern:     {fstats['pattern']}")
    print(f"  Filtered by antipattern: {fstats['antipattern']}")
    print(f"  Total matches:           {len(filtered_words)}")

    # Sort results
    sort_mode = args.sort
    if not sort_mode:
        if freq_map:
            sort_mode = 'freq'
        else:
            sort_mode = 'alpha'

    if sort_mode == 'freq':
        if freq_map:
            filtered_words = sort_by_frequency(filtered_words, freq_map)
            print("Sorting: by frequency (Zipf)")
        else:
            filtered_words = sorted(filtered_words)
            print("Sorting: alphabetical (frequency unavailable)")
    elif sort_mode == 'alpha':
        filtered_words = sorted(filtered_words)
        print("Sorting: alphabetical")
    else:
        print("Sorting: none (original order)")

    # Display results
    if filtered_words:
        print("\nResults:")
        for w in filtered_words:
            print(f"  {w}")
    else:
        print("\nResults: no words found.")


if __name__ == "__main__":
    main()
