#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lexicon loading module for 5-letter Russian words.
Loads words from JSONL.gz format with frequency data.
"""

import gzip
import json
import os
import time
from typing import Dict, List, Tuple


def load_lexicon(lexicon_path: str = "data/lexicon_ru_5.jsonl.gz") -> Tuple[List[str], Dict[str, float]]:
    """
    Load 5-letter words from JSONL.gz lexicon file.

    Args:
        lexicon_path: Path to lexicon file (default: data/lexicon_ru_5.jsonl.gz)

    Returns:
        Tuple of (list of words, frequency map {word: zipf_score})

    Raises:
        FileNotFoundError: If lexicon file doesn't exist
    """
    if not os.path.exists(lexicon_path):
        raise FileNotFoundError(f"Lexicon file not found: {lexicon_path}")

    print(f"Loading lexicon: {lexicon_path}")
    start_time = time.time()

    open_fn = gzip.open if lexicon_path.endswith('.gz') else open
    words_raw: List[str] = []
    freq_map: Dict[str, float] = {}
    total_lines = 0

    with open_fn(lexicon_path, 'rt', encoding='utf-8') as f:
        for line in f:
            total_lines += 1
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except Exception:
                continue

            w = obj.get('word')
            if not isinstance(w, str):
                continue

            # Normalize: lowercase and ё → е
            w = w.lower().replace('ё', 'е')
            words_raw.append(w)

            # Store frequency (Zipf score)
            z = obj.get('zipf')
            if isinstance(z, (int, float)):
                # Keep maximum value in case of duplicates
                prev = freq_map.get(w)
                if prev is None or z > prev:
                    freq_map[w] = float(z)

    # Deduplicate while preserving order
    seen = set()
    all_words = []
    for w in words_raw:
        if w not in seen:
            seen.add(w)
            all_words.append(w)

    elapsed = time.time() - start_time
    print(f"Loaded {len(all_words)} unique 5-letter words from {total_lines} lines in {elapsed:.2f}s")

    return (all_words, freq_map)


def get_lexicon_stats(words: List[str], freq_map: Dict[str, float]) -> Dict:
    """
    Get statistics about loaded lexicon.

    Args:
        words: List of words
        freq_map: Frequency map

    Returns:
        Dictionary with stats
    """
    return {
        'total_words': len(words),
        'has_freq': bool(freq_map),
        'freq_count': len(freq_map),
    }
