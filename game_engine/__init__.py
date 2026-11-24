"""
Game Engine - Khởi tạo package engine
"""

from .kmap_parser import (
    get_kmap_dimensions,
    cell_to_binary,
    binary_to_cell,
    minterm_to_cell,
    cell_to_minterm,
    parse_grid_to_matrix,
    simplify_group,
    simplify_group_pos,
    simplify_all_groups,
    simplify_all_groups_pos,
    solve_pos_expression,
    get_pos_groups,
    format_kmap_text,
    get_variable_names,
)
from .validator import (
    validate_answer,
    evaluate_expression,
    canonicalize_term,
    is_logically_equivalent,
    normalize_expression_str,
)
from .scoring import ScoreManager, AttemptResult

__all__ = [
    'get_kmap_dimensions',
    'cell_to_binary',
    'binary_to_cell',
    'minterm_to_cell',
    'cell_to_minterm',
    'parse_grid_to_matrix',
    'simplify_group',
    'simplify_group_pos',
    'simplify_all_groups',
    'simplify_all_groups_pos',
    'solve_pos_expression',
    'get_pos_groups',
    'format_kmap_text',
    'get_variable_names',
    'validate_answer',
    'evaluate_expression',
    'canonicalize_term',
    'is_logically_equivalent',
    'normalize_expression_str',
    'ScoreManager',
    'AttemptResult',
]

