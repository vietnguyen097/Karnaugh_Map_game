#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Karnaugh Map Parser - Phân tích, chuyển đổi và đơn giản hóa bìa Karnaugh
Hỗ trợ 2, 3, 4 và 5 biến logic.
"""

from typing import Dict, List, Tuple, Any, Optional, Set

# Thứ tự mã Gray chuẩn cho 1, 2, 3 biến
GRAY_CODES = {
    1: ['0', '1'],
    2: ['00', '01', '11', '10'],
    3: ['000', '001', '011', '010', '110', '111', '101', '100'],
}

VAR_NAMES_DEFAULT = {
    2: ('A', 'B'),
    3: ('A', 'B', 'C'),
    4: ('A', 'B', 'C', 'D'),
    5: ('A', 'B', 'C', 'D', 'E'),
}


def get_variable_names(num_vars: int) -> Tuple[str, ...]:
    """Trả về danh sách tên biến theo số lượng biến."""
    if num_vars in VAR_NAMES_DEFAULT:
        return VAR_NAMES_DEFAULT[num_vars]
    return tuple(chr(65 + i) for i in range(num_vars))


def get_kmap_dimensions(num_vars: int) -> Dict[str, Any]:
    """
    Trả về thông tin kích thước và phân bố biến trên hàng/cột của bìa Karnaugh.
    
    Args:
        num_vars: Số biến (2, 3, 4 hoặc 5)
        
    Returns:
        Dict chứa num_rows, num_cols, row_vars, col_vars, row_labels, col_labels
    """
    var_names = get_variable_names(num_vars)
    
    if num_vars == 2:
        # A (hàng: 0, 1) \ B (cột: 0, 1)
        row_vars = (var_names[0],)
        col_vars = (var_names[1],)
        row_labels = GRAY_CODES[1]
        col_labels = GRAY_CODES[1]
    elif num_vars == 3:
        # A (hàng: 0, 1) \ BC (cột: 00, 01, 11, 10)
        row_vars = (var_names[0],)
        col_vars = var_names[1:3]
        row_labels = GRAY_CODES[1]
        col_labels = GRAY_CODES[2]
    elif num_vars == 4:
        # AB (hàng: 00, 01, 11, 10) \ CD (cột: 00, 01, 11, 10)
        row_vars = var_names[0:2]
        col_vars = var_names[2:4]
        row_labels = GRAY_CODES[2]
        col_labels = GRAY_CODES[2]
    elif num_vars == 5:
        # AB (hàng: 00, 01, 11, 10) \ CDE (cột: 8 cột mã Gray 3-bit)
        row_vars = var_names[0:2]
        col_vars = var_names[2:5]
        row_labels = GRAY_CODES[2]
        col_labels = GRAY_CODES[3]
    else:
        raise ValueError(f"Chỉ hỗ trợ số biến từ 2 đến 5, nhận được: {num_vars}")
        
    return {
        'num_vars': num_vars,
        'num_rows': len(row_labels),
        'num_cols': len(col_labels),
        'row_vars': "".join(row_vars),
        'col_vars': "".join(col_vars),
        'row_labels': row_labels,
        'col_labels': col_labels,
        'var_names': var_names,
    }


def cell_to_binary(row: int, col: int, num_vars: int) -> str:
    """
    Chuyển đổi tọa độ (row, col) trên bìa Karnaugh thành chuỗi nhị phân các biến.
    """
    dims = get_kmap_dimensions(num_vars)
    row_bin = dims['row_labels'][row]
    col_bin = dims['col_labels'][col]
    return row_bin + col_bin


def binary_to_cell(binary_str: str, num_vars: int) -> Tuple[int, int]:
    """
    Chuyển chuỗi nhị phân các biến thành tọa độ (row, col).
    """
    dims = get_kmap_dimensions(num_vars)
    num_row_bits = len(dims['row_vars'])
    row_bits = binary_str[:num_row_bits]
    col_bits = binary_str[num_row_bits:]
    
    row = dims['row_labels'].index(row_bits)
    col = dims['col_labels'].index(col_bits)
    return row, col


def cell_to_minterm(row: int, col: int, num_vars: int) -> int:
    """Chuyển tọa độ (row, col) thành chỉ số minterm tương ứng."""
    bin_str = cell_to_binary(row, col, num_vars)
    return int(bin_str, 2)


def minterm_to_cell(minterm: int, num_vars: int) -> Tuple[int, int]:
    """Chuyển chỉ số minterm thành tọa độ (row, col)."""
    bin_str = format(minterm, f'0{num_vars}b')
    return binary_to_cell(bin_str, num_vars)


def parse_grid_to_matrix(grid_data: List[Dict[str, Any]], num_vars: int = 3) -> List[List[int]]:
    """
    Chuyển đổi dữ liệu grid từ database thành ma trận 2D.
    
    Args:
        grid_data: Danh sách dict có {'row': int, 'col': int, 'value': int}
        num_vars: Số biến của bìa
        
    Returns:
        Ma trận 2D kích thước num_rows x num_cols
    """
    dims = get_kmap_dimensions(num_vars)
    num_rows = dims['num_rows']
    num_cols = dims['num_cols']
    
    matrix = [[0 for _ in range(num_cols)] for _ in range(num_rows)]
    for cell in grid_data:
        r = cell['row']
        c = cell['col']
        v = cell.get('value', 0)
        if 0 <= r < num_rows and 0 <= c < num_cols:
            matrix[r][c] = v
            
    return matrix


def _parse_cell_coord(cell: Any) -> Tuple[int, int]:
    """Chuyển đổi ô biểu diễn dạng 'row,col' hoặc tuple (r, c) sang tuple."""
    if isinstance(cell, str):
        parts = cell.replace('(', '').replace(')', '').split(',')
        return int(parts[0].strip()), int(parts[1].strip())
    elif isinstance(cell, (list, tuple)):
        return int(cell[0]), int(cell[1])
    elif isinstance(cell, dict):
        return int(cell['row']), int(cell['col'])
    raise ValueError(f"Định dạng ô không hợp lệ: {cell}")


def simplify_group(cells: List[Any], num_vars: int, var_names: Optional[Tuple[str, ...]] = None) -> str:
    """
    Đơn giản hóa một nhóm ô trên bìa Karnaugh thành một tích logic (product term) cho SOP.
    
    Quy tắc:
    - Nếu ô chứa biến mang giá trị cố định 1 -> X
    - Nếu ô chứa biến mang giá trị cố định 0 -> X'
    - Nếu biến thay đổi giá trị trong nhóm -> bị triệt tiêu
    - Nếu toàn bộ các biến bị triệt tiêu (nhóm toàn bộ bìa) -> '1'
    - Nếu nhóm rỗng -> '0'
    """
    if not cells:
        return '0'
        
    if var_names is None:
        var_names = get_variable_names(num_vars)
        
    binary_list = [cell_to_binary(*_parse_cell_coord(c), num_vars) for c in cells]
    
    term_literals = []
    for var_idx in range(num_vars):
        values = {b[var_idx] for b in binary_list}
        var_name = var_names[var_idx]
        if len(values) == 1:
            val = next(iter(values))
            if val == '1':
                term_literals.append(var_name)
            else:
                term_literals.append(f"{var_name}'")
                
    if not term_literals:
        return '1'
        
    return "".join(term_literals)


def simplify_group_pos(cells: List[Any], num_vars: int, var_names: Optional[Tuple[str, ...]] = None) -> str:
    """
    Đơn giản hóa một nhóm ô 0 trên bìa Karnaugh thành một tổng logic (sum term) cho POS.
    
    Quy tắc POS (đảo ngược so với SOP):
    - Nếu ô chứa biến mang giá trị cố định 0 -> X (không bù)
    - Nếu ô chứa biến mang giá trị cố định 1 -> X' (bù)
    - Nếu biến thay đổi giá trị trong nhóm -> bị triệt tiêu
    - Nếu toàn bộ các biến bị triệt tiêu -> '0'
    - Nếu nhóm rỗng -> '1'
    """
    if not cells:
        return '1'
        
    if var_names is None:
        var_names = get_variable_names(num_vars)
        
    binary_list = [cell_to_binary(*_parse_cell_coord(c), num_vars) for c in cells]
    
    sum_literals = []
    for var_idx in range(num_vars):
        values = {b[var_idx] for b in binary_list}
        var_name = var_names[var_idx]
        if len(values) == 1:
            val = next(iter(values))
            # POS: đảo ngược — giá trị 0 → biến không bù, giá trị 1 → biến bù
            if val == '0':
                sum_literals.append(var_name)
            else:
                sum_literals.append(f"{var_name}'")
                
    if not sum_literals:
        return '0'
        
    if len(sum_literals) == 1:
        return sum_literals[0]
        
    return "(" + " + ".join(sum_literals) + ")"


def simplify_all_groups(groups: List[Dict[str, Any]], num_vars: int, var_names: Optional[Tuple[str, ...]] = None) -> str:
    """
    Đơn giản hóa tất cả các nhóm ô của bài toán thành biểu thức SOP tối giản.
    
    Args:
        groups: Danh sách dict [{'id': 1, 'cells': ['0,0', '0,1'], ...}, ...]
        num_vars: Số biến
        var_names: Danh sách tên biến tùy chọn
        
    Returns:
        Chuỗi biểu thức tối giản SOP, ví dụ: "A'B + BC'" hoặc "1" hoặc "0"
    """
    if not groups:
        return '0'
        
    terms = []
    for group in groups:
        cells = group.get('cells', [])
        if cells:
            term = simplify_group(cells, num_vars, var_names)
            if term == '1':
                return '1'
            if term != '0' and term not in terms:
                terms.append(term)
                
    if not terms:
        return '0'
        
    return " + ".join(terms)


def simplify_all_groups_pos(groups: List[Dict[str, Any]], num_vars: int, var_names: Optional[Tuple[str, ...]] = None) -> str:
    """
    Đơn giản hóa tất cả các nhóm ô 0 thành biểu thức POS tối giản.
    
    Args:
        groups: Danh sách dict chứa các nhóm ô 0
        num_vars: Số biến
        var_names: Danh sách tên biến tùy chọn
        
    Returns:
        Chuỗi biểu thức POS, ví dụ: "(A+B)(A'+C)" hoặc "0" hoặc "1"
    """
    if not groups:
        return '1'
        
    factors = []
    for group in groups:
        cells = group.get('cells', [])
        if cells:
            factor = simplify_group_pos(cells, num_vars, var_names)
            if factor == '0':
                return '0'
            if factor != '1' and factor not in factors:
                factors.append(factor)
                
    if not factors:
        return '1'
        
    return "".join(factors)


def solve_pos_expression(zeros: Set[int], dont_cares: Set[int], num_vars: int) -> str:
    """
    Tìm biểu thức POS tối giản chuẩn xác cho tập hợp các minterm nhận giá trị 0 và dont_cares.
    Sử dụng thuật toán Quine-McCluskey tìm Prime Implicants của hàm đảo f' (các ô 0),
    sau đó chuyển sang Maxterms (dạng POS) của f bằng luật De Morgan.
    """
    var_names = get_variable_names(num_vars)
    all_minterms = zeros | dont_cares
    if not zeros:
        return '1'
    if len(zeros) + len(dont_cares) == (1 << num_vars):
        return '0'

    terms = {format(m, f'0{num_vars}b'): {m} for m in all_minterms}
    prime_implicants = set()

    current_terms = terms
    while current_terms:
        next_terms = {}
        combined = set()
        keys = list(current_terms.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                t1, t2 = keys[i], keys[j]
                diff_count = 0
                diff_pos = -1
                for idx in range(num_vars):
                    if t1[idx] != t2[idx]:
                        diff_count += 1
                        diff_pos = idx
                if diff_count == 1:
                    new_t = t1[:diff_pos] + '-' + t1[diff_pos+1:]
                    combined.add(t1)
                    combined.add(t2)
                    if new_t not in next_terms:
                        next_terms[new_t] = set()
                    next_terms[new_t].update(current_terms[t1])
                    next_terms[new_t].update(current_terms[t2])
        for t, covered in current_terms.items():
            if t not in combined:
                if any(m in zeros for m in covered):
                    prime_implicants.add((t, frozenset(covered & zeros)))
        current_terms = next_terms

    uncovered = set(zeros)
    chosen_terms = []
    
    while uncovered:
        essential = None
        for m in uncovered:
            covering_pis = [pi for pi in prime_implicants if m in pi[1]]
            if len(covering_pis) == 1:
                essential = covering_pis[0]
                break
        if essential:
            chosen_terms.append(essential[0])
            uncovered -= essential[1]
            prime_implicants.remove(essential)
        else:
            best_pi = max(prime_implicants, key=lambda pi: (len(pi[1] & uncovered), pi[0].count('-')))
            chosen_terms.append(best_pi[0])
            uncovered -= best_pi[1]
            prime_implicants.remove(best_pi)

    factors = []
    for t in sorted(chosen_terms):
        lits = []
        for idx in range(num_vars):
            if t[idx] == '0':
                lits.append(var_names[idx])
            elif t[idx] == '1':
                lits.append(f"{var_names[idx]}'")
        if not lits:
            factors.append('0')
        elif len(lits) == 1 and len(chosen_terms) == 1:
            factors.append(lits[0])
        else:
            factors.append('(' + ' + '.join(lits) + ')')
    return ''.join(factors)


def get_pos_groups(zeros: Set[int], dont_cares: Set[int], num_vars: int) -> Tuple[List[Dict[str, Any]], str]:
    """
    Tìm danh sách các nhóm ô 0 (groups) dạng [{'id': 1, 'cells': ['0,0', ...], 'term': '...'}, ...]
    và biểu thức POS tối giản.
    """
    var_names = get_variable_names(num_vars)
    all_minterms = zeros | dont_cares
    if not zeros:
        return [], '1'
    if len(zeros) + len(dont_cares) == (1 << num_vars):
        # Tất cả các ô là 0
        all_cells = []
        for m in zeros:
            r, c = minterm_to_cell(m, num_vars)
            all_cells.append(f"{r},{c}")
        return [{'id': 1, 'cells': all_cells, 'term': '0'}], '0'

    terms = {format(m, f'0{num_vars}b'): {m} for m in all_minterms}
    prime_implicants = set()

    current_terms = terms
    while current_terms:
        next_terms = {}
        combined = set()
        keys = list(current_terms.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                t1, t2 = keys[i], keys[j]
                diff_count = 0
                diff_pos = -1
                for idx in range(num_vars):
                    if t1[idx] != t2[idx]:
                        diff_count += 1
                        diff_pos = idx
                if diff_count == 1:
                    new_t = t1[:diff_pos] + '-' + t1[diff_pos+1:]
                    combined.add(t1)
                    combined.add(t2)
                    if new_t not in next_terms:
                        next_terms[new_t] = set()
                    next_terms[new_t].update(current_terms[t1])
                    next_terms[new_t].update(current_terms[t2])
        for t, covered in current_terms.items():
            if t not in combined:
                if any(m in zeros for m in covered):
                    prime_implicants.add((t, frozenset(covered & zeros), frozenset(covered)))
        current_terms = next_terms

    uncovered = set(zeros)
    chosen = [] # list of (pattern, covered_zeros, full_covered_minterms)
    
    while uncovered:
        essential = None
        for m in uncovered:
            covering_pis = [pi for pi in prime_implicants if m in pi[1]]
            if len(covering_pis) == 1:
                essential = covering_pis[0]
                break
        if essential:
            chosen.append(essential)
            uncovered -= essential[1]
            prime_implicants.remove(essential)
        else:
            best_pi = max(prime_implicants, key=lambda pi: (len(pi[1] & uncovered), pi[0].count('-')))
            chosen.append(best_pi)
            uncovered -= best_pi[1]
            prime_implicants.remove(best_pi)

    # Xếp thứ tự nhóm
    chosen.sort(key=lambda x: x[0])
    
    groups = []
    factors = []
    for idx, (pattern, cov_zeros, full_cov) in enumerate(chosen):
        cells = []
        for m in sorted(full_cov):
            r, c = minterm_to_cell(m, num_vars)
            cells.append(f"{r},{c}")
            
        lits = []
        for v_idx in range(num_vars):
            if pattern[v_idx] == '0':
                lits.append(var_names[v_idx])
            elif pattern[v_idx] == '1':
                lits.append(f"{var_names[v_idx]}'")
                
        term_str = '(' + ' + '.join(lits) + ')' if len(lits) > 1 else (lits[0] if lits else '0')
        groups.append({
            'id': idx + 1,
            'cells': cells,
            'term': term_str,
            'pattern': pattern
        })
        factors.append(term_str)
        
    pos_expr = ''.join(factors) if factors else '1'
    return groups, pos_expr


def format_kmap_text(kmap_matrix: List[List[int]], num_vars: int) -> str:
    """
    Tạo chuỗi văn bản biểu diễn bìa Karnaugh trực quan cho console/terminal.
    """
    dims = get_kmap_dimensions(num_vars)
    row_vars = dims['row_vars']
    col_vars = dims['col_vars']
    row_labels = dims['row_labels']
    col_labels = dims['col_labels']
    
    header = f"{row_vars}\\{col_vars}".center(8) + " | " + " | ".join(c.center(5) for c in col_labels)
    sep_line = "-" * len(header)
    
    lines = [
        f"=== BÌA KARNAUGH ({num_vars} BIẾN) ===",
        header,
        sep_line,
    ]
    
    for r_idx, r_label in enumerate(row_labels):
        row_vals = " | ".join(str(kmap_matrix[r_idx][c_idx]).center(5) for c_idx in range(len(col_labels)))
        lines.append(f"{r_label.center(8)} | {row_vals}")
        
    lines.append(sep_line)
    return "\n".join(lines)
