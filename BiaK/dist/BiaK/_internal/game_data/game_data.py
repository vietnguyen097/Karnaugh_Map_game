# -*- coding: utf-8 -*-
"""
Game Data - Quản lý và nạp dữ liệu bài toán Karnaugh
Hỗ trợ nạp bài cơ bản (2-3 biến) và nâng cao (3-5 biến).
"""

import json
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

if getattr(sys, 'frozen', False):
    GAME_DATA_DIR = Path(sys._MEIPASS).resolve() / "game_data"
else:
    GAME_DATA_DIR = Path(__file__).parent.resolve()


def load_basic_problems() -> List[Dict[str, Any]]:
    """Tải tất cả bài toán cơ bản (2-3 biến)."""
    basic_problems = []
    
    for filename in ["variables_2.json", "variables_3.json"]:
        path = GAME_DATA_DIR / "basic_kmap" / filename
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                basic_problems.extend(data.get('problems', []))
                
    return basic_problems


def load_advanced_problems() -> List[Dict[str, Any]]:
    """Tải tất cả bài toán nâng cao (3-5 biến)."""
    advanced_problems = []
    
    for var_count in [3, 4, 5]:
        path = GAME_DATA_DIR / "advanced_kmap" / f"problems_{var_count}.json"
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                advanced_problems.extend(data.get('problems', []))
                
    return advanced_problems


def load_all_problems() -> Dict[str, List[Dict[str, Any]]]:
    """
    Tải tất cả bài toán.
    Returns:
        Dict: {'basic': [...], 'advanced': [...]}
    """
    return {
        'basic': load_basic_problems(),
        'advanced': load_advanced_problems()
    }


def get_problem_by_id(problem_id: str) -> Optional[Dict[str, Any]]:
    """Tìm bài toán theo ID."""
    all_problems = load_all_problems()
    for cat in ['basic', 'advanced']:
        for problem in all_problems[cat]:
            if problem.get('id') == problem_id:
                return problem
    return None


def get_problems_by_variable_count(var_count: int, level: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lọc bài toán theo số biến và cấp độ tùy chọn.
    """
    all_problems = load_all_problems()
    source = []
    if level == 'basic':
        source = all_problems['basic']
    elif level == 'advanced':
        source = all_problems['advanced']
    else:
        source = all_problems['basic'] + all_problems['advanced']
        
    return [p for p in source if p.get('num_vars') == var_count]


def get_basic_problems_by_difficulty(min_diff: int = 1, max_diff: int = 5) -> List[Dict[str, Any]]:
    """Lọc bài toán cơ bản theo độ khó."""
    return [
        p for p in load_basic_problems() 
        if min_diff <= p.get('difficulty', 1) <= max_diff
    ]


def get_advanced_problems_by_difficulty(min_diff: int = 4, max_diff: int = 10) -> List[Dict[str, Any]]:
    """Lọc bài toán nâng cao theo độ khó."""
    return [
        p for p in load_advanced_problems() 
        if min_diff <= p.get('difficulty', 1) <= max_diff
    ]


def generate_random_problem(difficulty: int = 1, var_count: int = 3) -> Dict[str, Any]:
    """Lấy một bài toán ngẫu nhiên theo số biến hoặc độ khó."""
    import random
    matches = get_problems_by_variable_count(var_count)
    if matches:
        return random.choice(matches)
    all_p = load_basic_problems() + load_advanced_problems()
    return random.choice(all_p) if all_p else {}


__all__ = [
    'load_basic_problems',
    'load_advanced_problems',
    'load_all_problems',
    'get_problem_by_id',
    'get_problems_by_variable_count',
    'get_basic_problems_by_difficulty',
    'get_advanced_problems_by_difficulty',
    'generate_random_problem',
]
