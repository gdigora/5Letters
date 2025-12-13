#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Word search and filtering module.
Filters words based on excluded letters, must-have letters, pattern, and antipattern.
"""

from typing import Dict, List, Optional, Sequence, Set, Tuple


def filter_words(
    words: Sequence[str],
    must_have: Set[str],
    excluded: Set[str],
    pattern: Optional[str] = None,
    antipattern_constraints: Optional[List[Optional[Set[str]]]] = None,
) -> Tuple[List[str], Dict[str, int]]:
    """
    Filter words based on search criteria.

    Args:
        words: List of candidate words
        must_have: Set of required letters (yellow in Wordle)
        excluded: Set of excluded letters (gray in Wordle)
        pattern: Pattern with '_' for unknown positions (green in Wordle)
        antipattern_constraints: Position-specific forbidden letters

    Returns:
        Tuple of (filtered words list, filter statistics dict)
    """
    if not words:
        return [], {"must_have": 0, "excluded": 0, "pattern": 0, "antipattern": 0}

    result: List[str] = []
    filtered_stats = {"must_have": 0, "excluded": 0, "pattern": 0, "antipattern": 0}

    for word in words:
        # Filter: excluded letters
        if excluded and any(ch in excluded for ch in word):
            filtered_stats["excluded"] += 1
            continue

        # Filter: must_have letters
        if must_have and not must_have.issubset(set(word)):
            filtered_stats["must_have"] += 1
            continue

        # Filter: pattern (green positions)
        if pattern:
            ok = True
            for i, ch in enumerate(pattern):
                if ch != '_' and word[i] != ch:
                    ok = False
                    break
            if not ok:
                filtered_stats["pattern"] += 1
                continue

        # Filter: antipattern (positional bans)
        if antipattern_constraints:
            violation = False
            for i, banned in enumerate(antipattern_constraints):
                if banned and word[i] in banned:
                    violation = True
                    break
            if violation:
                filtered_stats["antipattern"] += 1
                continue

        result.append(word)

    return result, filtered_stats


def get_search_prefixes(
    pattern: Optional[str],
    excluded: Set[str],
    antipattern_constraints: Optional[List[Optional[Set[str]]]]
) -> Set[str]:
    """
    Get possible first letters for search optimization.

    Args:
        pattern: Pattern string
        excluded: Excluded letters
        antipattern_constraints: Antipattern constraints

    Returns:
        Set of allowed first letters
    """
    russian_alphabet = set('абвгдежзийклмнопрстуфхцчшщъыьэюя')
    antipattern_excluded_first: Set[str] = set()

    if antipattern_constraints and antipattern_constraints[0]:
        antipattern_excluded_first = antipattern_constraints[0]

    if pattern and pattern[0] != '_':
        first_letter = pattern[0]
        if first_letter in excluded or first_letter in antipattern_excluded_first:
            return set()
        return {first_letter}

    return russian_alphabet - excluded - antipattern_excluded_first


def sort_by_frequency(
    words: List[str],
    freq_map: Dict[str, float],
    reverse: bool = True
) -> List[str]:
    """
    Sort words by frequency (Zipf score).

    Args:
        words: List of words to sort
        freq_map: Frequency map {word: zipf_score}
        reverse: If True, sort from most to least frequent (default)

    Returns:
        Sorted list of words
    """
    if not freq_map:
        return sorted(words)  # Fallback to alphabetical

    # Sort by frequency (descending) then alphabetically for ties
    return sorted(words, key=lambda w: (-freq_map.get(w, -100.0), w))
