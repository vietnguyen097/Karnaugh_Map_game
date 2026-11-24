"""
Game Data Package - Quản lý và cung cấp database bài toán Karnaugh
"""

from .game_data import (
    load_all_problems,
    load_basic_problems,
    load_advanced_problems,
    get_problem_by_id,
    get_basic_problems_by_difficulty,
    get_advanced_problems_by_difficulty,
    generate_random_problem,
)

__all__ = [
    'load_all_problems',
    'load_basic_problems',
    'load_advanced_problems',
    'get_problem_by_id',
    'get_basic_problems_by_difficulty',
    'get_advanced_problems_by_difficulty',
    'generate_random_problem',
]

