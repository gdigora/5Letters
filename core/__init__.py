#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Core library for 5-letter Russian word search.
Provides lexicon loading, input parsing, and word filtering functionality.
"""

from .lexicon import load_lexicon, get_lexicon_stats
from .parser import (
    parse_input,
    parse_antipattern,
    check_conflicts,
    get_search_params,
)
from .search import (
    filter_words,
    get_search_prefixes,
    sort_by_frequency,
)

__all__ = [
    # Lexicon
    'load_lexicon',
    'get_lexicon_stats',
    # Parser
    'parse_input',
    'parse_antipattern',
    'check_conflicts',
    'get_search_params',
    # Search
    'filter_words',
    'get_search_prefixes',
    'sort_by_frequency',
]

__version__ = '1.0.0'
