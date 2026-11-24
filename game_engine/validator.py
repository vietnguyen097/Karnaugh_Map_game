#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator - Bộ kiểm tra và phân tích cú pháp đáp án logic cho BiaK.
Hỗ trợ:
- Kiểm tra chân lý và điều kiện tùy định Don't Care ('X' / 'd')
- Tối giản dạng SOP (tổng các tích)
- Chấp nhận: A'B, ~AB, !AB, not A and B, A*B, A+B, v.v.
"""

import re
from typing import Dict, List, Set, Tuple, Any, Optional
from .kmap_parser import get_kmap_dimensions, get_variable_names, cell_to_binary


def normalize_expression_str(expr: str) -> str:
    """Chuẩn hóa biểu thức sơ bộ."""
    if not expr:
        return ""
    res = expr.strip().replace("’", "'").replace("‘", "'").replace("`", "'")
    res = re.sub(r'^[Ff]\s*=\s*', '', res)
    res = re.sub(r'\s*\+\s*', ' + ', res)
    return re.sub(r'\s+', ' ', res).strip()


def tokenize_expression(s: str) -> List[str]:
    """
    Phân tích chuỗi biểu thức logic thành danh sách token chuẩn.
    Tự động chèn toán tử '*' (AND) tại các vị trí nhân ngầm (juxtaposition).
    """
    s = normalize_expression_str(s)
    if not s:
        return []
        
    raw_tokens = re.findall(r'\b(?:and|or|not)\b|[A-Za-z]|[01]|\+|\*|&|\||~|!|\'|\(|\)', s)
    tokens = []
    for t in raw_tokens:
        tl = t.lower()
        if tl == 'or' or t == '|':
            tokens.append('+')
        elif tl == 'and' or t in ('*', '&'):
            tokens.append('*')
        elif tl == 'not' or t in ('~', '!'):
            tokens.append('~')
        else:
            tokens.append(t)
            
    # Chèn '*' ngầm giữa các token liền kề:
    expanded = []
    for i, tok in enumerate(tokens):
        if i > 0:
            prev = tokens[i - 1]
            prev_can_end = (
                prev.isalpha() or prev in ('0', '1', "'", ')')
            )
            curr_can_start = (
                tok.isalpha() or tok in ('0', '1', '~', '(')
            )
            if prev_can_end and curr_can_start:
                expanded.append('*')
        expanded.append(tok)
        
    return expanded


class BooleanEvaluator:
    """Parser và evaluator cú pháp logic đơn giản, an toàn."""
    
    def __init__(self, tokens: List[str], var_values: Dict[str, bool]):
        self.tokens = tokens
        self.pos = 0
        self.var_values = {k.upper(): v for k, v in var_values.items()}
        
    def peek(self) -> Optional[str]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
        
    def consume(self, expected: Optional[str] = None) -> str:
        tok = self.peek()
        if tok is None:
            raise ValueError("Hết biểu thức bất ngờ")
        if expected is not None and tok != expected:
            raise ValueError(f"Kỳ vọng '{expected}', gặp '{tok}'")
        self.pos += 1
        return tok
        
    def parse(self) -> bool:
        if not self.tokens:
            return False
        val = self.parse_or()
        if self.pos < len(self.tokens):
            raise ValueError(f"Dư thừa ký tự tại vị trí {self.pos}: '{self.tokens[self.pos]}'")
        return val
        
    def parse_or(self) -> bool:
        val = self.parse_and()
        while self.peek() == '+':
            self.consume('+')
            rhs = self.parse_and()
            val = val or rhs
        return val
        
    def parse_and(self) -> bool:
        val = self.parse_not()
        while self.peek() == '*':
            self.consume('*')
            rhs = self.parse_not()
            val = val and rhs
        return val
        
    def parse_not(self) -> bool:
        if self.peek() == '~':
            self.consume('~')
            val = not self.parse_not()
        else:
            val = self.parse_primary()
            
        while self.peek() == "'":
            self.consume("'")
            val = not val
        return val
        
    def parse_primary(self) -> bool:
        tok = self.consume()
        if tok == '(':
            val = self.parse_or()
            self.consume(')')
            return val
        elif tok == '1':
            return True
        elif tok == '0':
            return False
        elif len(tok) == 1 and tok.isalpha():
            var_name = tok.upper()
            if var_name not in self.var_values:
                return False
            return self.var_values[var_name]
        else:
            raise ValueError(f"Token không hợp lệ: '{tok}'")


def evaluate_expression(expr: str, var_values: Dict[str, bool]) -> bool:
    """Tính giá trị chân lý của biểu thức với bộ giá trị biến cụ thể."""
    tokens = tokenize_expression(expr)
    if not tokens:
        return False
    evaluator = BooleanEvaluator(tokens, var_values)
    return evaluator.parse()


def compute_truth_table(expr: str, num_vars: int, var_names: Optional[Tuple[str, ...]] = None) -> List[int]:
    """Tính toàn bộ bảng chân lý 0..2^num_vars - 1."""
    if var_names is None:
        var_names = get_variable_names(num_vars)
        
    tokens = tokenize_expression(expr)
    if not tokens:
        return [0] * (1 << num_vars)
        
    truth_table = []
    total_minterms = 1 << num_vars
    for m in range(total_minterms):
        bin_str = format(m, f'0{num_vars}b')
        var_values = {var_names[i]: (bin_str[i] == '1') for i in range(num_vars)}
        evaluator = BooleanEvaluator(tokens, var_values)
        val = evaluator.parse()
        truth_table.append(1 if val else 0)
        
    return truth_table


def get_grid_truth_spec(kmap_grid: List[Dict[str, Any]], num_vars: int) -> Tuple[Set[int], Set[int], Set[int]]:
    """
    Phân loại các minterm theo kmap_grid:
    Returns:
        (required_ones, required_zeros, dont_cares)
    """
    total_minterms = 1 << num_vars
    dims = get_kmap_dimensions(num_vars)
    
    required_ones = set()
    required_zeros = set()
    dont_cares = set()
    
    for cell in kmap_grid:
        r = cell['row']
        c = cell['col']
        v = cell.get('value', 0)
        bin_str = dims['row_labels'][r] + dims['col_labels'][c]
        m = int(bin_str, 2)
        if m < total_minterms:
            if v in ('X', 'x', 'd', 'D'):
                dont_cares.add(m)
            elif v == 1 or v == '1':
                required_ones.add(m)
            else:
                required_zeros.add(m)
                
    return required_ones, required_zeros, dont_cares


def grid_to_truth_table(kmap_grid: List[Dict[str, Any]], num_vars: int) -> List[int]:
    """Chuyển dữ liệu kmap_grid thành bảng chân lý (minterm 'X' coi là 0 hoặc 1)."""
    total_minterms = 1 << num_vars
    tt = [0] * total_minterms
    dims = get_kmap_dimensions(num_vars)
    for cell in kmap_grid:
        r = cell['row']
        c = cell['col']
        v = cell.get('value', 0)
        bin_str = dims['row_labels'][r] + dims['col_labels'][c]
        m = int(bin_str, 2)
        if m < total_minterms:
            tt[m] = 1 if (v == 1 or v == '1') else (v if v in ('X', 'x', 'd') else 0)
    return tt


def is_logically_equivalent(expr1: str, expr2: str, num_vars: int) -> bool:
    """Kiểm tra hai biểu thức logic có tương đương chân lý hoàn toàn không."""
    try:
        tt1 = compute_truth_table(expr1, num_vars)
        tt2 = compute_truth_table(expr2, num_vars)
        return tt1 == tt2
    except Exception:
        return False


def canonicalize_term(term_str: str) -> Optional[Tuple[Tuple[str, int], ...]]:
    """Chuyển một tích logic thành tuple chuẩn hóa: ((var, val), ...)."""
    t = term_str.strip()
    if not t:
        return None
    if t == '1':
        return ()
    if t == '0':
        return None
        
    matches = re.findall(r'([A-Za-z])(\'|~)?', t)
    if not matches:
        return None
        
    literals = {}
    for var, prime in matches:
        var = var.upper()
        val = 0 if prime == "'" else 1
        if var in literals and literals[var] != val:
            return None
        literals[var] = val
        
    return tuple(sorted(literals.items()))


def parse_sop_terms(expr: str) -> Optional[Set[Tuple[Tuple[str, int], ...]]]:
    """Phân tích biểu thức dạng SOP thành tập hợp các term chuẩn hóa."""
    cleaned = normalize_expression_str(expr)
    if '(' in cleaned or ')' in cleaned:
        return None
        
    parts = cleaned.split('+')
    term_set = set()
    for p in parts:
        p = p.strip()
        if not p:
            continue
        cterm = canonicalize_term(p)
        if cterm is not None:
            term_set.add(cterm)
            
    return term_set


def parse_pos_factors(expr: str) -> Optional[Set[Tuple[Tuple[str, int], ...]]]:
    """
    Phân tích biểu thức dạng POS thành tập hợp các factor chuẩn hóa.
    POS format: (A+B)(A'+C) hoặc (A+B)(C)
    """
    cleaned = normalize_expression_str(expr)
    if '+' not in cleaned and '(' not in cleaned:
        return None
    
    # Tách các factor (A+B)(C+D) → ["A+B", "C+D"]
    factors = re.findall(r'\(([^)]+)\)', cleaned)
    if not factors:
        # Trường hợp chỉ có 1 factor không ngoặc, ví dụ: A+B
        if '+' in cleaned:
            factors = [cleaned]
        else:
            return None
    
    factor_set = set()
    for f in factors:
        # Mỗi factor là một sum term: A+B+C'
        literals = {}
        sum_parts = f.split('+')
        for sp in sum_parts:
            sp = sp.strip()
            if not sp:
                continue
            matches = re.findall(r'([A-Za-z])(\'|~)?', sp)
            for var, prime in matches:
                var = var.upper()
                val = 0 if prime == "'" else 1
                if var in literals and literals[var] != val:
                    return None
                literals[var] = val
        if literals:
            factor_set.add(tuple(sorted(literals.items())))
    
    return factor_set


def validate_answer(
    user_answer: str,
    problem: Dict[str, Any],
    num_vars: Optional[int] = None,
    mode: str = "SOP",
) -> Dict[str, Any]:
    """
    Kiểm tra đáp án của người chơi, hỗ trợ cả SOP và POS, và Don't Care ('X').
    
    Args:
        user_answer: Đáp án người chơi nhập
        problem: Dữ liệu bài toán
        num_vars: Số biến (tự suy nếu None)
        mode: "SOP" hoặc "POS"
    """
    user_answer = normalize_expression_str(user_answer)
    
    # Lấy đáp án mong đợi theo mode
    if mode == "POS":
        raw_expected = problem.get('answer_pos', problem.get('answer', ''))
    else:
        raw_expected = problem.get('answer', '')
    clean_expected = raw_expected.split('=')[-1].strip() if '=' in raw_expected else raw_expected.strip()
    
    if not user_answer:
        return {
            'is_correct': False,
            'is_equivalent': False,
            'is_simplified': False,
            'message': "Vui lòng nhập đáp án!",
            'expected_answer': clean_expected,
        }
        
    if num_vars is None:
        num_vars = problem.get('num_vars')
        if num_vars is None:
            grid = problem.get('kmap_grid', [])
            max_r = max((c['row'] for c in grid), default=0)
            max_c = max((c['col'] for c in grid), default=0)
            if max_r <= 1 and max_c <= 1:
                num_vars = 2
            elif max_r <= 1 and max_c <= 3:
                num_vars = 3
            elif max_r <= 3 and max_c <= 3:
                num_vars = 4
            else:
                num_vars = 5

    req_ones, req_zeros, dont_cares = get_grid_truth_spec(problem.get('kmap_grid', []), num_vars)
    
    try:
        user_tt = compute_truth_table(user_answer, num_vars)
    except Exception as e:
        return {
            'is_correct': False,
            'is_equivalent': False,
            'is_simplified': False,
            'message': f"Cú pháp biểu thức không hợp lệ: {e}",
            'expected_answer': clean_expected,
        }
        
    # 1. Kiểm tra bao phủ các ô bắt buộc bằng 1
    missing_ones = [m for m in req_ones if user_tt[m] != 1]
    if missing_ones:
        return {
            'is_correct': False,
            'is_equivalent': False,
            'is_simplified': False,
            'message': f"Chưa chính xác: Chưa bao phủ minterm {missing_ones[:3]} có giá trị 1. Hãy thử lại!",
            'expected_answer': clean_expected,
        }
        
    # 2. Kiểm tra không được bao phủ các ô bắt buộc bằng 0
    forbidden_ones = [m for m in req_zeros if user_tt[m] == 1]
    if forbidden_ones:
        return {
            'is_correct': False,
            'is_equivalent': False,
            'is_simplified': False,
            'message': f"Chưa chính xác: Bao phủ nhầm ô có giá trị 0 tại minterm {forbidden_ones[:3]}. Hãy thử lại!",
            'expected_answer': clean_expected,
        }
        
    # Đã thỏa mãn logic chân lý (các ô Don't Care cho phép linh hoạt 0 hoặc 1)!
    # So sánh cấu trúc theo mode SOP hoặc POS
    if mode == "POS":
        expected_factors = parse_pos_factors(clean_expected)
        user_factors = parse_pos_factors(user_answer)
        
        if expected_factors is not None and user_factors is not None:
            if user_factors == expected_factors:
                return {
                    'is_correct': True,
                    'is_equivalent': True,
                    'is_simplified': True,
                    'message': "🎉 Xuất sắc! Đáp án POS chính xác và tối giản hoàn toàn.",
                    'expected_answer': clean_expected,
                }
            elif len(user_factors) == len(expected_factors):
                user_lits = sum(len(t) for t in user_factors)
                exp_lits = sum(len(t) for t in expected_factors)
                if user_lits <= exp_lits:
                    return {
                        'is_correct': True,
                        'is_equivalent': True,
                        'is_simplified': True,
                        'message': "🎉 Chính xác! Dạng POS tối giản hợp lệ.",
                        'expected_answer': clean_expected,
                    }
                else:
                    return {
                        'is_correct': False,
                        'is_equivalent': True,
                        'is_simplified': False,
                        'message': "⚠️ Đúng logic, nhưng chưa rút gọn tối đa dạng POS!",
                        'expected_answer': clean_expected,
                    }
            elif len(user_factors) > len(expected_factors):
                return {
                    'is_correct': False,
                    'is_equivalent': True,
                    'is_simplified': False,
                    'message': "⚠️ Đúng logic, nhưng chưa gom hết các factor POS!",
                    'expected_answer': clean_expected,
                }
    else:
        expected_terms = parse_sop_terms(clean_expected)
        user_terms = parse_sop_terms(user_answer)
        
        if expected_terms is not None and user_terms is not None:
            if user_terms == expected_terms:
                return {
                    'is_correct': True,
                    'is_equivalent': True,
                    'is_simplified': True,
                    'message': "🎉 Xuất sắc! Đáp án chính xác và tối giản hoàn toàn.",
                    'expected_answer': clean_expected,
                }
            elif len(user_terms) == len(expected_terms):
                user_lits = sum(len(t) for t in user_terms)
                exp_lits = sum(len(t) for t in expected_terms)
                if user_lits <= exp_lits:
                    return {
                        'is_correct': True,
                        'is_equivalent': True,
                        'is_simplified': True,
                        'message': "🎉 Chính xác! Bạn đã tìm được một dạng rút gọn tối giản hợp lệ.",
                        'expected_answer': clean_expected,
                    }
                else:
                    return {
                        'is_correct': False,
                        'is_equivalent': True,
                        'is_simplified': False,
                        'message': "⚠️ Đúng về logic, nhưng chưa rút gọn tối đa số biến trong nhóm!",
                        'expected_answer': clean_expected,
                    }
            elif len(user_terms) > len(expected_terms):
                return {
                    'is_correct': False,
                    'is_equivalent': True,
                    'is_simplified': False,
                    'message': "⚠️ Đúng về logic, nhưng chưa gom hết các nhóm để rút gọn tối đa!",
                    'expected_answer': clean_expected,
                }
            
    return {
        'is_correct': True,
        'is_equivalent': True,
        'is_simplified': True,
        'message': "🎉 Đáp án đúng về mặt logic!",
        'expected_answer': clean_expected,
    }
