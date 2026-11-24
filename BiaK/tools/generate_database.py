#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Generator - Tạo bộ dữ liệu 500 bài toán Karnaugh chuẩn cho game BiaK.
Bao gồm:
- 2 biến: 20 bài
- 3 biến Cơ bản: 80 bài
- 3 biến Nâng cao: 100 bài (chuẩn, ô cô lập, Don't Care)
- 4 biến Nâng cao: 220 bài (chuẩn, ô cô lập, Don't Care, 4 góc, khối tâm, bao biên)
- 5 biến Chuyên sâu: 80 bài (chuẩn, ô cô lập, Don't Care, khối 8-16 ô)
Tổng cộng: 500 bài toán kiểm định 100% bằng engine.
"""

import sys
import json
from pathlib import Path
from typing import List, Tuple, Set, Optional

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from game_engine.kmap_parser import (
    get_kmap_dimensions,
    minterm_to_cell,
    cell_to_minterm,
    simplify_group,
    simplify_all_groups,
)
from game_engine.validator import validate_answer

COLORS = [
    "#4CAF50", "#2196F3", "#FF9800", "#E91E63", 
    "#9C27B0", "#00BCD4", "#3B82F6", "#8B5CF6", 
    "#EC4899", "#14B8A6", "#F59E0B", "#10B981"
]


def mask_to_minterms(mask: str) -> List[int]:
    """Chuyển chuỗi mask (ví dụ '-0-0') thành danh sách minterm hợp lệ."""
    indices = [i for i, ch in enumerate(mask) if ch == '-']
    base_val = sum((1 << (len(mask) - 1 - i)) for i, ch in enumerate(mask) if ch == '1')
    results = []
    num_dash = len(indices)
    for combo in range(1 << num_dash):
        val = base_val
        for bit_idx, pos in enumerate(indices):
            if (combo >> (num_dash - 1 - bit_idx)) & 1:
                val |= (1 << (len(mask) - 1 - pos))
        results.append(val)
    return sorted(results)


def create_problem(
    pid: str,
    title: str,
    num_vars: int,
    minterm_groups: list,
    difficulty: int,
    explanation: str = "",
    dont_cares: list = None,
) -> dict:
    """Tạo một bài toán Karnaugh hoàn chỉnh, hỗ trợ cả Don't Care ('X') và ô cô lập."""
    dims = get_kmap_dimensions(num_vars)
    num_rows = dims['num_rows']
    num_cols = dims['num_cols']
    
    dont_cares_set = set(dont_cares) if dont_cares else set()
    
    all_grouped_minterms = set()
    for grp in minterm_groups:
        for m in grp:
            all_grouped_minterms.add(m)
            
    grid = []
    for r in range(num_rows):
        for c in range(num_cols):
            m = cell_to_minterm(r, c, num_vars)
            if m in dont_cares_set:
                val = "X"
            elif m in all_grouped_minterms:
                val = 1
            else:
                val = 0
            grid.append({"row": r, "col": c, "value": val})
            
    groups = []
    for idx, grp in enumerate(minterm_groups):
        cells = []
        for m in grp:
            r, c = minterm_to_cell(m, num_vars)
            cells.append(f"{r},{c}")
        groups.append({
            "id": idx + 1,
            "cells": cells,
            "color": COLORS[idx % len(COLORS)]
        })
        
    answer = simplify_all_groups(groups, num_vars)
    
    if not explanation:
        terms_exp = []
        for g in groups:
            term = simplify_group(g['cells'], num_vars)
            c_len = len(g['cells'])
            if c_len == 1:
                terms_exp.append(f"Ô cô lập {c_len} ô -> {term}")
            else:
                has_dc = any(cell_to_minterm(int(c.split(',')[0]), int(c.split(',')[1]), num_vars) in dont_cares_set for c in g['cells'])
                dc_note = " (kết hợp ô tùy định X)" if has_dc else ""
                terms_exp.append(f"Nhóm {c_len} ô{dc_note} -> {term}")
        explanation = "; ".join(terms_exp)
        
    problem = {
        "id": pid,
        "title": title,
        "num_vars": num_vars,
        "difficulty": difficulty,
        "kmap_grid": grid,
        "groups": groups,
        "answer": answer,
        "answer_explanation": explanation,
    }
    
    if dont_cares_set:
        problem["dont_cares"] = sorted(list(dont_cares_set))
        
    val = validate_answer(answer, problem, num_vars)
    if not val['is_correct']:
        raise ValueError(f"Lỗi kiểm định bài {pid}: {val['message']} (answer={answer})")
        
    return problem


# =============================================================================
# BỘ SINH DỮ LIỆU BÀI TOÁN
# =============================================================================

def generate_2var_problems() -> list:
    """Tạo 20 bài 2 biến."""
    probs = []
    
    # 1. Hàng & cột cơ bản
    probs.append(create_problem("B2-001", "Hàng A = 0", 2, [mask_to_minterms("0-")], 1))
    probs.append(create_problem("B2-002", "Hàng A = 1", 2, [mask_to_minterms("1-")], 1))
    probs.append(create_problem("B2-003", "Cột B = 0", 2, [mask_to_minterms("-0")], 1))
    probs.append(create_problem("B2-004", "Cột B = 1", 2, [mask_to_minterms("-1")], 1))
    
    # 2. Ô đơn lẻ (cô lập)
    probs.append(create_problem("B2-005", "Ô cô lập m0 (0,0)", 2, [mask_to_minterms("00")], 1))
    probs.append(create_problem("B2-006", "Ô cô lập m1 (0,1)", 2, [mask_to_minterms("01")], 1))
    probs.append(create_problem("B2-007", "Ô cô lập m2 (1,0)", 2, [mask_to_minterms("10")], 1))
    probs.append(create_problem("B2-008", "Ô cô lập m3 (1,1)", 2, [mask_to_minterms("11")], 1))
    
    # 3. Đường chéo & toàn bộ
    probs.append(create_problem("B2-009", "Toàn bộ bìa F = 1", 2, [mask_to_minterms("--")], 1))
    probs.append(create_problem("B2-010", "Hai ô cô lập m0 và m3 (XNOR)", 2, [mask_to_minterms("00"), mask_to_minterms("11")], 2))
    probs.append(create_problem("B2-011", "Hai ô cô lập m1 và m2 (XOR)", 2, [mask_to_minterms("01"), mask_to_minterms("10")], 2))
    
    # 4. Gom 2 nhóm giao nhau
    probs.append(create_problem("B2-012", "F = A' + B", 2, [mask_to_minterms("0-"), mask_to_minterms("-1")], 2))
    probs.append(create_problem("B2-013", "F = A + B", 2, [mask_to_minterms("1-"), mask_to_minterms("-1")], 2))
    probs.append(create_problem("B2-014", "F = A' + B'", 2, [mask_to_minterms("0-"), mask_to_minterms("-0")], 2))
    probs.append(create_problem("B2-015", "F = A + B'", 2, [mask_to_minterms("1-"), mask_to_minterms("-0")], 2))
    
    # 5. Don't Care 2 biến
    probs.append(create_problem("B2-016", "Don't Care: m(0) + d(1)", 2, [mask_to_minterms("0-")], 2, dont_cares=[1]))
    probs.append(create_problem("B2-017", "Don't Care: m(1) + d(3)", 2, [mask_to_minterms("-1")], 2, dont_cares=[3]))
    probs.append(create_problem("B2-018", "Don't Care: m(2) + d(3)", 2, [mask_to_minterms("1-")], 2, dont_cares=[3]))
    probs.append(create_problem("B2-019", "Don't Care: m(0) + d(2)", 2, [mask_to_minterms("-0")], 2, dont_cares=[2]))
    probs.append(create_problem("B2-020", "Don't Care: m(0) + d(3) cô lập", 2, [mask_to_minterms("00")], 2, dont_cares=[3]))
    
    return probs


def generate_3var_basic_problems() -> list:
    """Tạo 80 bài 3 biến cơ bản."""
    probs = []
    
    # 1. Tám ô đơn lẻ (m0..m7) (8 bài)
    for m in range(8):
        mask = format(m, '03b')
        probs.append(create_problem(f"B3-{len(probs)+1:03d}", f"Ô đơn lẻ m{m} ({mask})", 3, [mask_to_minterms(mask)], 1))
        
    # 2. Toàn bộ 12 cặp 2 ô kề nhau (12 bài)
    pair_masks = [
        # Hàng A=0
        "00-", "0-1", "01-", "0-0",
        # Hàng A=1
        "10-", "1-1", "11-", "1-0",
        # Cột dọc
        "-00", "-01", "-11", "-10"
    ]
    for p_mask in pair_masks:
        mterms = mask_to_minterms(p_mask)
        probs.append(create_problem(f"B3-{len(probs)+1:03d}", f"Cặp 2 ô m({mterms[0]},{mterms[1]})", 3, [mterms], 1))
        
    # 3. Sáu khối 4 ô (6 bài)
    quad_masks = ["0--", "1--", "-0-", "--1", "-1-", "--0"]
    for q_mask in quad_masks:
        mterms = mask_to_minterms(q_mask)
        probs.append(create_problem(f"B3-{len(probs)+1:03d}", f"Khối 4 ô mask '{q_mask}'", 3, [mterms], 2))
        
    # 4. Toàn bộ bìa (1 bài)
    probs.append(create_problem(f"B3-{len(probs)+1:03d}", "Toàn bộ 8 ô đều bằng 1", 3, [mask_to_minterms("---")], 1))
    
    # 5. Kết hợp 2 cặp ô (30 bài)
    pair_combos_added = 0
    for i in range(len(pair_masks)):
        for j in range(i + 1, len(pair_masks)):
            m1 = pair_masks[i]
            m2 = pair_masks[j]
            grp1 = mask_to_minterms(m1)
            grp2 = mask_to_minterms(m2)
            if len(set(grp1 + grp2)) < 8:
                try:
                    probs.append(create_problem(f"B3-{len(probs)+1:03d}", f"Kết hợp 2 cặp '{m1}' và '{m2}'", 3, [grp1, grp2], 2))
                    pair_combos_added += 1
                    if pair_combos_added >= 30:
                        break
                except Exception:
                    pass
        if pair_combos_added >= 30:
            break
            
    # 6. Khối 4 ô + 1 cặp 2 ô (15 bài)
    quad_pair_added = 0
    for q in quad_masks:
        for p in pair_masks:
            grp1 = mask_to_minterms(q)
            grp2 = mask_to_minterms(p)
            if len(set(grp1 + grp2)) < 8 and not set(grp2).issubset(set(grp1)):
                try:
                    probs.append(create_problem(f"B3-{len(probs)+1:03d}", f"Khối 4 ô '{q}' + Cặp 2 ô '{p}'", 3, [grp1, grp2], 3))
                    quad_pair_added += 1
                    if quad_pair_added >= 15:
                        break
                except Exception:
                    pass
        if quad_pair_added >= 15:
            break
        
    # 7. Khối 4 ô + 1 ô cô lập (10 bài)
    iso_targets = [
        ("0--", "100"), ("0--", "111"), ("0--", "101"), ("0--", "110"),
        ("1--", "000"), ("1--", "011"), ("1--", "001"), ("1--", "010"),
        ("-0-", "011"), ("-1-", "000"), ("--0", "001"), ("--1", "000")
    ]
    for q, iso in iso_targets:
        grp1 = mask_to_minterms(q)
        grp2 = mask_to_minterms(iso)
        if len(probs) < 80:
            probs.append(create_problem(f"B3-{len(probs)+1:03d}", f"Khối 4 ô '{q}' + Ô cô lập m{grp2[0]}", 3, [grp1, grp2], 3))
        
    return probs[:80]


def generate_3var_adv_problems() -> list:
    """Tạo 100 bài 3 biến nâng cao (gồm nhiều ô cô lập & Don't Care)."""
    probs = []
    
    # 1. Các bài chuẩn phức hợp (30 bài)
    # 3 cặp ô chồng lấn / đối xứng
    combos_3 = [
        (["0-0", "1-1"], 4, "Bao biên kép F = Σm(0,2,5,7)"),
        (["-00", "-11"], 4, "Hai cột đối xứng F = Σm(0,4,3,7)"),
        (["0-1", "-01", "1-0"], 5, "Ba nhóm kề F = Σm(1,3,4,5,6)"),
        (["0-0", "-01"], 5, "Bao biên + dọc F = Σm(0,1,2,5)"),
        (["-1-", "1--"], 4, "Sáu ô kề F = Σm(2,3,4,5,6,7)"),
        (["-00", "1-0", "111"], 6, "Hai nhóm + 1 ô cô lập m7"),
        (["001", "010", "100", "111"], 7, "Parity 3 biến (4 ô cô lập hoàn toàn)"),
        (["000", "011", "101", "110"], 7, "Đối xứng chéo (4 ô cô lập hoàn toàn)"),
        (["-0-", "-00"], 4, "B=0 và C=0"),
        (["--1", "-00"], 4, "C=1 và B'C'"),
    ]
    for grp_masks, diff, title in combos_3:
        groups = [mask_to_minterms(m) for m in grp_masks]
        probs.append(create_problem(f"A3-{len(probs)+1:03d}", title, 3, groups, diff))
        
    # Tạo thêm các bài có ô cô lập (40 bài)
    for i in range(40):
        # 1 cặp + 1 hoặc 2 ô cô lập
        p_mask = ["00-", "0-1", "10-", "1-1", "-00", "-11", "0-0", "1-0", "-01", "-10"][i % 10]
        iso_m1 = format((i * 3 + 2) % 8, '03b')
        m_p = mask_to_minterms(p_mask)
        m_iso = mask_to_minterms(iso_m1)
        if m_iso[0] in m_p:
            iso_m1 = format((i * 3 + 5) % 8, '03b')
            m_iso = mask_to_minterms(iso_m1)
            
        probs.append(create_problem(
            f"A3-{len(probs)+1:03d}",
            f"Nhóm 2 ô '{p_mask}' + Ô cô lập m{m_iso[0]}",
            3,
            [m_p, m_iso],
            5
        ))
        
    # 2. Năm mươi bài Don't Care 3 biến (50 bài)
    for i in range(50):
        # Chọn mẫu: nhóm 4 ô được tạo bởi 1, 2 ô 1 và các ô don't care
        quad_mask = ["0--", "1--", "-0-", "--1", "-1-", "--0"][i % 6]
        all_quad_m = mask_to_minterms(quad_mask)
        
        # Chọn 1 hoặc 2 minterm làm Don't Care
        dc_count = 1 if i % 2 == 0 else 2
        dc_indices = [(i + j) % 4 for j in range(dc_count)]
        dcs = [all_quad_m[idx] for idx in dc_indices]
        
        # Thêm bài toán Don't Care
        if i % 3 == 0 and len(probs) < 95:
            # Don't Care kết hợp thêm 1 ô cô lập
            iso_m = format((all_quad_m[0] + 5) % 8, '03b')
            iso_grp = mask_to_minterms(iso_m)
            if iso_grp[0] in all_quad_m or iso_grp[0] in dcs:
                iso_m = format((all_quad_m[0] + 3) % 8, '03b')
                iso_grp = mask_to_minterms(iso_m)
            probs.append(create_problem(
                f"A3-{len(probs)+1:03d}",
                f"Don't Care '{quad_mask}' + Ô cô lập m{iso_grp[0]}",
                3,
                [all_quad_m, iso_grp],
                6,
                dont_cares=dcs
            ))
        else:
            probs.append(create_problem(
                f"A3-{len(probs)+1:03d}",
                f"Don't Care: Khối '{quad_mask}' nhờ d({','.join(map(str, dcs))})",
                3,
                [all_quad_m],
                5,
                dont_cares=dcs
            ))
            
    return probs[:100]


def generate_4var_adv_problems() -> list:
    """Tạo 220 bài 4 biến nâng cao (chứa rất nhiều ô cô lập và Don't Care)."""
    probs = []
    
    # Danh sách các mask 4 biến thông dụng
    # 8-cell masks (8)
    oct_masks = ["0---", "1---", "-0--", "-1--", "--0-", "--1-", "---0", "---1"]
    
    # 4-cell masks (24)
    quad_masks = [
        # Khối 2x2
        "0-0-", "0-1-", "1-0-", "1-1-",  # 4 góc lớn
        "00--", "01--", "11--", "10--",  # 4 hàng
        "--00", "--01", "--11", "--10",  # 4 cột
        "-0-0", "-1-1", "-0-1", "-1-0",  # 4 góc ngoài, tâm, đối
        "0--0", "1--0", "0--1", "1--1",
        "-00-", "-01-", "-11-", "-10-",
    ]
    
    # 1. Các bài đơn nhóm: 8 ô và 4 ô (30 bài)
    for m in oct_masks:
        mterms = mask_to_minterms(m)
        probs.append(create_problem(f"A4-{len(probs)+1:03d}", f"Nhóm 8 ô mask '{m}'", 4, [mterms], 4))
        
    for m in quad_masks[:22]:
        mterms = mask_to_minterms(m)
        probs.append(create_problem(f"A4-{len(probs)+1:03d}", f"Khối 4 ô mask '{m}'", 4, [mterms], 5))
        
    # 2. Hai nhóm 4 ô hoặc 8 ô kết hợp (40 bài)
    for i in range(40):
        m1 = quad_masks[i % len(quad_masks)]
        m2 = quad_masks[(i * 3 + 7) % len(quad_masks)]
        g1 = mask_to_minterms(m1)
        g2 = mask_to_minterms(m2)
        probs.append(create_problem(f"A4-{len(probs)+1:03d}", f"Hai khối '{m1}' và '{m2}'", 4, [g1, g2], 6))
        
    # 3. Ba nhóm 4 ô kết hợp (30 bài)
    for i in range(30):
        m1 = quad_masks[i % len(quad_masks)]
        m2 = quad_masks[(i + 4) % len(quad_masks)]
        m3 = quad_masks[(i + 9) % len(quad_masks)]
        g1 = mask_to_minterms(m1)
        g2 = mask_to_minterms(m2)
        g3 = mask_to_minterms(m3)
        probs.append(create_problem(f"A4-{len(probs)+1:03d}", f"Ba khối '{m1}', '{m2}', '{m3}'", 4, [g1, g2, g3], 7))
        
    # 4. CÁC BÀI TOÁN CÓ Ô CÔ LẬP TRONG 4 BIẾN (50 bài - Tăng độ khó cực cao!)
    for i in range(50):
        # 1 nhóm lớn (4 ô hoặc 8 ô) + 1 hoặc 2 ô cô lập
        base_mask = oct_masks[i % len(oct_masks)] if i % 3 == 0 else quad_masks[i % len(quad_masks)]
        base_m = mask_to_minterms(base_mask)
        
        # Tìm các ô bên ngoài base_m làm ô cô lập
        outside = [m for m in range(16) if m not in base_m]
        
        if i % 2 == 0:
            # 1 ô cô lập
            iso1 = outside[(i * 7) % len(outside)]
            probs.append(create_problem(
                f"A4-{len(probs)+1:03d}",
                f"Khối '{base_mask}' + 1 Ô CÔ LẬP m{iso1}",
                4,
                [base_m, [iso1]],
                7,
                f"Nhóm lớn {len(base_m)} ô; ô cô lập duy nhất m{iso1}"
            ))
        else:
            # 2 ô cô lập
            iso1 = outside[(i * 5) % len(outside)]
            iso2 = outside[(i * 11 + 3) % len(outside)]
            if iso1 == iso2:
                iso2 = outside[(i * 11 + 7) % len(outside)]
            probs.append(create_problem(
                f"A4-{len(probs)+1:03d}",
                f"Khối '{base_mask}' + 2 Ô CÔ LẬP m{iso1}, m{iso2}",
                4,
                [base_m, [iso1], [iso2]],
                8,
                f"Nhóm lớn {len(base_m)} ô; hai ô cô lập m{iso1} và m{iso2}"
            ))
            
    # 5. CÁC BÀI TOÁN DON'T CARE 4 BIẾN (70 bài)
    for i in range(70):
        target_mask = quad_masks[i % len(quad_masks)] if i % 2 == 0 else oct_masks[i % len(oct_masks)]
        mterms = mask_to_minterms(target_mask)
        
        # Chọn 1 đến 3 minterm trong nhóm làm Don't Care
        num_dc = 1 + (i % 3)
        dc_m = [mterms[(i * 2 + j) % len(mterms)] for j in range(num_dc)]
        
        # Tùy biến kết hợp thêm ô cô lập bên ngoài
        if i % 4 == 0:
            outside = [m for m in range(16) if m not in mterms]
            iso = outside[(i * 3) % len(outside)]
            probs.append(create_problem(
                f"A4-{len(probs)+1:03d}",
                f"Don't Care '{target_mask}' + Ô cô lập m{iso}",
                4,
                [mterms, [iso]],
                7,
                dont_cares=dc_m
            ))
        else:
            probs.append(create_problem(
                f"A4-{len(probs)+1:03d}",
                f"Don't Care: Khối '{target_mask}' nhờ d({','.join(map(str, dc_m))})",
                4,
                [mterms],
                6,
                dont_cares=dc_m
            ))
            
    return probs[:220]


def generate_5var_adv_problems() -> list:
    """Tạo 80 bài 5 biến nâng cao (bìa 4x8 ô - 32 minterms)."""
    probs = []
    
    # 1. Mười nhóm 16 ô (nửa bìa 5 biến)
    half_masks = [
        "0----", "1----", "-0---", "-1---", 
        "--0--", "--1--", "---0-", "---1-",
        "----0", "----1"
    ]
    for h_mask in half_masks:
        mterms = mask_to_minterms(h_mask)
        probs.append(create_problem(f"A5-{len(probs)+1:03d}", f"Khối 16 ô mask '{h_mask}'", 5, [mterms], 8))
        
    # 2. Hai mươi nhóm 8 ô (20 bài)
    oct_masks = [
        "00---", "01---", "11---", "10---",
        "0-0--", "0-1--", "1-0--", "1-1--",
        "-0-0-", "-0-1-", "-1-0-", "-1-1-",
        "--00-", "--01-", "--11-", "--10-",
        "0---0", "1---0", "0---1", "1---1"
    ]
    for o_mask in oct_masks:
        mterms = mask_to_minterms(o_mask)
        probs.append(create_problem(f"A5-{len(probs)+1:03d}", f"Khối 8 ô mask '{o_mask}'", 5, [mterms], 8))
        
    # 3. Kết hợp 2 khối 8 ô hoặc 16 ô (20 bài)
    for i in range(20):
        h = half_masks[i % len(half_masks)]
        o = oct_masks[(i * 3 + 2) % len(oct_masks)]
        g1 = mask_to_minterms(h)
        g2 = mask_to_minterms(o)
        probs.append(create_problem(f"A5-{len(probs)+1:03d}", f"Khối 16 ô '{h}' + Khối 8 ô '{o}'", 5, [g1, g2], 9))
        
    # 4. CÁC BÀI TOÁN CÓ Ô CÔ LẬP TRONG 5 BIẾN (15 bài - Thử thách cực đại)
    for i in range(15):
        base_mask = oct_masks[i % len(oct_masks)]
        base_m = mask_to_minterms(base_mask)
        outside = [m for m in range(32) if m not in base_m]
        iso = outside[(i * 13 + 5) % len(outside)]
        probs.append(create_problem(
            f"A5-{len(probs)+1:03d}",
            f"Khối 8 ô '{base_mask}' + Ô CÔ LẬP 5 BIẾN m{iso}",
            5,
            [base_m, [iso]],
            9,
            f"Nhóm 8 ô {base_mask}; ô cô lập hoàn toàn m{iso}"
        ))
        
    # 5. CÁC BÀI TOÁN DON'T CARE 5 BIẾN (15 bài)
    for i in range(15):
        base_mask = half_masks[i % len(half_masks)] if i % 2 == 0 else oct_masks[i % len(oct_masks)]
        mterms = mask_to_minterms(base_mask)
        dcs = [mterms[j] for j in range(2 + (i % 3))]
        probs.append(create_problem(
            f"A5-{len(probs)+1:03d}",
            f"Don't Care 5 biến: Khối '{base_mask}' nhờ d({','.join(map(str, dcs))})",
            5,
            [mterms],
            9,
            dont_cares=dcs
        ))
        
    return probs[:80]


def generate_all():
    print("🚀 Bắt đầu tạo database 500 BÀI TOÁN KARNAUGH TOÀN DIỆN cho BiaK...")
    
    p2 = generate_2var_problems()
    file_b2 = PROJECT_ROOT / "game_data" / "basic_kmap" / "variables_2.json"
    with open(file_b2, 'w', encoding='utf-8') as f:
        json.dump({"level": "basic", "category": "2_variables", "description": "Bài toán 2 biến", "problems": p2}, f, indent=2, ensure_ascii=False)
    print(f"✅ Đã tạo {len(p2)} bài vào {file_b2.name}")

    p3_basic = generate_3var_basic_problems()
    file_b3 = PROJECT_ROOT / "game_data" / "basic_kmap" / "variables_3.json"
    with open(file_b3, 'w', encoding='utf-8') as f:
        json.dump({"level": "basic", "category": "3_variables", "description": "Bài toán 3 biến cơ bản", "problems": p3_basic}, f, indent=2, ensure_ascii=False)
    print(f"✅ Đã tạo {len(p3_basic)} bài vào {file_b3.name}")

    p3_adv = generate_3var_adv_problems()
    file_a3 = PROJECT_ROOT / "game_data" / "advanced_kmap" / "problems_3.json"
    with open(file_a3, 'w', encoding='utf-8') as f:
        json.dump({"level": "advanced", "category": "3_variables_advanced", "description": "Bài toán 3 biến nâng cao, ô cô lập & Don't Care", "problems": p3_adv}, f, indent=2, ensure_ascii=False)
    print(f"✅ Đã tạo {len(p3_adv)} bài vào {file_a3.name}")

    p4_adv = generate_4var_adv_problems()
    file_a4 = PROJECT_ROOT / "game_data" / "advanced_kmap" / "problems_4.json"
    with open(file_a4, 'w', encoding='utf-8') as f:
        json.dump({"level": "advanced", "category": "4_variables", "description": "Bài toán 4 biến nâng cao, ô cô lập & Don't Care", "problems": p4_adv}, f, indent=2, ensure_ascii=False)
    print(f"✅ Đã tạo {len(p4_adv)} bài vào {file_a4.name}")

    p5_adv = generate_5var_adv_problems()
    file_a5 = PROJECT_ROOT / "game_data" / "advanced_kmap" / "problems_5.json"
    with open(file_a5, 'w', encoding='utf-8') as f:
        json.dump({"level": "advanced", "category": "5_variables", "description": "Bài toán 5 biến nâng cao, ô cô lập & Don't Care", "problems": p5_adv}, f, indent=2, ensure_ascii=False)
    print(f"✅ Đã tạo {len(p5_adv)} bài vào {file_a5.name}")

    total = len(p2) + len(p3_basic) + len(p3_adv) + len(p4_adv) + len(p5_adv)
    print(f"\n🎉 HOÀN THÀNH 100%! Đã tạo và kiểm định thành công {total} BÀI TOÁN!")


if __name__ == "__main__":
    generate_all()
