#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Input parsing module for 5-letter word search.
Handles smart argument parsing with flexible order.
"""

from typing import Dict, List, Optional, Set


def parse_antipattern(antipattern: Optional[str]) -> Optional[List[Optional[Set[str]]]]:
    """
    Parse antipattern in two formats:
    - New: '1аб5в' = forbid 'а','б' at position 1 and 'в' at position 5
    - Old: '%аб%%%в' = same (backward compatibility)

    Args:
        antipattern: Antipattern string (e.g., "1аб5в" or "%аб%%%в")

    Returns:
        List of 5 elements, each either None or set of forbidden letters
        Returns None if no constraints
    """
    if not antipattern:
        return None

    constraints: List[Optional[Set[str]]] = [None] * 5

    # Determine format by presence of '%'
    if '%' in antipattern:
        # Old format: %аб%%%в
        segments = antipattern.split('%')
        position_segments = segments[1:6]
        for pos, segment in enumerate(position_segments):
            if pos >= 5:
                break
            if segment:
                constraints[pos] = set(segment)
    else:
        # New format: 1аб5в (digit + letters)
        current_pos: Optional[int] = None
        current_letters: List[str] = []

        for ch in antipattern:
            if ch.isdigit():
                # Save previous position
                if current_pos is not None and current_letters:
                    idx = current_pos - 1  # positions 1-5 → indices 0-4
                    if 0 <= idx < 5:
                        if constraints[idx] is None:
                            constraints[idx] = set()
                        constraints[idx].update(current_letters)
                # Start new position
                current_pos = int(ch)
                current_letters = []
            elif ch.isalpha():
                current_letters.append(ch)

        # Save last position
        if current_pos is not None and current_letters:
            idx = current_pos - 1
            if 0 <= idx < 5:
                if constraints[idx] is None:
                    constraints[idx] = set()
                constraints[idx].update(current_letters)

    # Return None if no constraints
    if all(c is None for c in constraints):
        return None
    return constraints


def check_conflicts(
    pattern: Optional[str],
    must_have: Set[str],
    excluded: Set[str],
    antipattern_constraints: Optional[List[Optional[Set[str]]]]
) -> List[str]:
    """
    Check for conflicts in search parameters.

    Args:
        pattern: Pattern string (e.g., "__а__")
        must_have: Set of required letters
        excluded: Set of excluded letters
        antipattern_constraints: Parsed antipattern constraints

    Returns:
        List of conflict messages (empty if no conflicts)
    """
    msgs: List[str] = []

    if not pattern:
        pattern_letters: Set[str] = set()
    else:
        pattern_letters = {ch for ch in pattern if ch != '_'}

    # Check if pattern requires excluded letters
    if pattern_letters & excluded:
        msgs.append(
            f"Pattern requires {sorted(pattern_letters & excluded)}, but they are excluded"
        )

    # Check if pattern conflicts with antipattern
    if antipattern_constraints and pattern:
        for i, ch in enumerate(pattern):
            if ch == '_':
                continue
            if antipattern_constraints[i] and ch in antipattern_constraints[i]:
                msgs.append(
                    f"Position {i+1}: required letter '{ch}' is forbidden by antipattern"
                )

    # Check if there's enough space for must_have letters
    free_positions = 5 - len(pattern_letters) if pattern else 5
    pattern_letters_in_must_have = pattern_letters & must_have
    remaining_must_have = must_have - pattern_letters_in_must_have
    if len(remaining_must_have) > free_positions:
        msgs.append(
            f"Not enough free positions: need to place {len(remaining_must_have)} "
            f"required letters in {free_positions} positions"
        )

    return msgs


def parse_input(input_text: str) -> Dict[str, str]:
    """
    Smart parsing of arguments by their pattern (order doesn't matter):
      -abc     → excluded (gray letters)
      +def     → included (yellow letters)
      _a___    → pattern (5 characters with '_')
      1a5b     → antipattern (contains digits)

    Args:
        input_text: Input string (e.g., "-нзф +ки __а__ 2к")

    Returns:
        Dictionary with keys: excluded, included, pattern, antipattern
    """
    # Split by whitespace
    args = input_text.split()

    result = {
        "excluded": "",
        "included": "",
        "pattern": "",
        "antipattern": "",
    }

    for arg in args:
        if arg.startswith('-'):
            # Excluded letters (but not flags like --help)
            if not arg.startswith('--'):
                result["excluded"] = arg[1:]  # remove '-'
        elif arg.startswith('+'):
            # Required letters
            result["included"] = arg[1:]  # remove '+'
        elif len(arg) == 5 and '_' in arg:
            # Pattern (5 characters with underscore)
            result["pattern"] = arg
        elif any(ch.isdigit() for ch in arg):
            # Antipattern (contains digits)
            result["antipattern"] = arg
        # Otherwise ignore (or could add to excluded by default)

    return result


def get_search_params(input_text: str) -> Dict:
    """
    Parse input and prepare search parameters.

    Args:
        input_text: User input string

    Returns:
        Dictionary with:
        - excluded: set of excluded letters
        - must_have: set of required letters
        - pattern: pattern string or None
        - antipattern_constraints: parsed antipattern or None
        - conflicts: list of conflict messages
    """
    params = parse_input(input_text)

    excluded = set(params["excluded"].lower())
    must_have = set(params["included"].lower())

    raw_pattern = params["pattern"]
    pattern = raw_pattern.lower() if raw_pattern else None
    if pattern and len(pattern) != 5:
        pattern = None  # Invalid pattern

    raw_antipattern = params["antipattern"]
    antipattern = raw_antipattern.lower() if raw_antipattern else None
    antipattern_constraints = parse_antipattern(antipattern)

    conflicts = check_conflicts(pattern, must_have, excluded, antipattern_constraints)

    return {
        'excluded': excluded,
        'must_have': must_have,
        'pattern': pattern,
        'antipattern_constraints': antipattern_constraints,
        'conflicts': conflicts,
        'raw_antipattern': antipattern,
    }
