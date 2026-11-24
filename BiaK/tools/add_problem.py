#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add Problem Tool - Công cụ thêm bài toán mới vào cơ sở dữ liệu BiaK.
Hỗ trợ:
- Cả bài toán chuẩn và bài có ô tùy định Don't Care ('X')
- Tự động tính toán grid, đáp án tối giản SOP và kiểm định tính đúng đắn trước khi lưu.
"""

import sys
import json
import argparse
from pathlib import Path

# Thêm project root vào sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from tools.generate_database import create_problem
from game_engine.kmap_parser import format_kmap_text, parse_grid_to_matrix


def get_target_file(level: str, num_vars: int) -> Path:
    """Xác định file JSON cần lưu bài toán mới."""
    if level == "basic":
        if num_vars == 2:
            return PROJECT_ROOT / "game_data" / "basic_kmap" / "variables_2.json"
        elif num_vars == 3:
            return PROJECT_ROOT / "game_data" / "basic_kmap" / "variables_3.json"
        else:
            raise ValueError("Cấp độ 'basic' chỉ hỗ trợ 2 hoặc 3 biến.")
    else:  # advanced
        if num_vars in (3, 4, 5):
            return PROJECT_ROOT / "game_data" / "advanced_kmap" / f"problems_{num_vars}.json"
        else:
            raise ValueError("Cấp độ 'advanced' chỉ hỗ trợ 3, 4 hoặc 5 biến.")


def parse_groups_input(raw_input: str) -> list:
    """
    Phân tích chuỗi các nhóm minterm do người dùng nhập.
    Ví dụ: '0,1; 1,3' hoặc '0 1 | 1 3' -> [[0, 1], [1, 3]]
    """
    raw_input = raw_input.replace("|", ";")
    group_strs = raw_input.split(";")
    minterm_groups = []
    
    for g_str in group_strs:
        g_str = g_str.strip()
        if not g_str:
            continue
        parts = g_str.replace(",", " ").split()
        grp = [int(p) for p in parts if p.isdigit()]
        if grp:
            minterm_groups.append(grp)
            
    return minterm_groups


def parse_dont_cares_input(raw_input: str) -> list:
    """Phân tích danh sách minterm Don't Care."""
    if not raw_input:
        return []
    parts = raw_input.replace(",", " ").replace(";", " ").split()
    return [int(p) for p in parts if p.isdigit()]


def add_problem_to_database(
    pid: str,
    title: str,
    level: str,
    num_vars: int,
    minterm_groups: list,
    difficulty: int = 1,
    explanation: str = "",
    dont_cares: list = None,
) -> dict:
    """Tạo bài toán và thêm vào file JSON tương ứng."""
    target_file = get_target_file(level, num_vars)
    if not target_file.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {target_file}")
        
    with open(target_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    problems = data.get("problems", [])
    
    # Kiểm tra trùng ID
    for p in problems:
        if p.get("id") == pid:
            raise ValueError(f"Mã bài toán '{pid}' đã tồn tại trong {target_file.name}!")
            
    # Tạo bài toán mới (tự động tính grid, đáp án và kiểm định)
    problem = create_problem(
        pid=pid,
        title=title,
        num_vars=num_vars,
        minterm_groups=minterm_groups,
        difficulty=difficulty,
        explanation=explanation,
        dont_cares=dont_cares,
    )
    
    problems.append(problem)
    data["problems"] = problems
    
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    return problem


def interactive_mode():
    """Giao diện dòng lệnh tương tác từng bước thân thiện."""
    print("=" * 60)
    print(" ➕ CÔNG CỤ TẠO BÀI TOÁN KARNAUGH MỚI - BIAK ➕ ")
    print("=" * 60)
    
    try:
        # 1. Chọn cấp độ
        print("\nChọn cấp độ:")
        print("  1. Cơ bản (basic - 2 hoặc 3 biến)")
        print("  2. Nâng cao (advanced - 3, 4 hoặc 5 biến)")
        lvl_choice = input("👉 Lựa chọn [1/2] (mặc định 1): ").strip() or "1"
        level = "basic" if lvl_choice == "1" else "advanced"
        
        # 2. Số biến
        default_vars = 2 if level == "basic" else 4
        vars_str = input(f"👉 Số biến ({'2, 3' if level == 'basic' else '3, 4, 5'}) [mặc định {default_vars}]: ").strip()
        num_vars = int(vars_str) if vars_str else default_vars
        
        # 3. Mã bài toán
        target_file = get_target_file(level, num_vars)
        data = json.load(open(target_file, 'r', encoding='utf-8'))
        next_num = len(data.get("problems", [])) + 1
        prefix = f"{'B' if level == 'basic' else 'A'}{num_vars}"
        default_pid = f"{prefix}-{next_num:03d}"
        
        pid = input(f"👉 Mã bài toán (ID) [mặc định {default_pid}]: ").strip() or default_pid
        
        # 4. Tiêu đề bài
        title = input("👉 Tiêu đề bài toán (ví dụ: 'F = Σm(0, 1, 2, 3)'): ").strip()
        if not title:
            title = f"Bài tập {num_vars} biến - {pid}"
            
        # 5. Các nhóm minterm
        print("\nNhập các nhóm minterm:")
        print("  • Mỗi nhóm là các minterm được gom lại.")
        print("  • Phân cách các nhóm bằng dấu chấm phẩy ';'.")
        print("  • Ví dụ 2 nhóm: '0, 1 ; 1, 3' hoặc '0 2 8 10'")
        groups_input = input("👉 Danh sách nhóm minterm: ").strip()
        if not groups_input:
            print("❌ Lỗi: Bạn phải nhập ít nhất 1 nhóm minterm!")
            return
            
        minterm_groups = parse_groups_input(groups_input)
        
        # 6. Ô tùy định Don't Care
        dc_input = input("👉 Các minterm tùy định Don't Care (ví dụ: '5, 7' hoặc bỏ trống nếu không có): ").strip()
        dont_cares = parse_dont_cares_input(dc_input)
        
        # 7. Độ khó
        diff_str = input("👉 Độ khó (1-10) [mặc định 2]: ").strip() or "2"
        difficulty = int(diff_str)
        
        # 8. Lời giải tùy chọn
        exp = input("👉 Lời giải thích (bỏ trống để hệ thống tự tạo): ").strip()
        
        # Tiến hành tạo bài toán
        print("\n⏳ Đang phân tích bìa Karnaugh, rút gọn hàm và kiểm định logic...")
        problem = add_problem_to_database(
            pid=pid,
            title=title,
            level=level,
            num_vars=num_vars,
            minterm_groups=minterm_groups,
            difficulty=difficulty,
            explanation=exp,
            dont_cares=dont_cares,
        )
        
        print("\n🎉 THÀNH CÔNG! Đã thêm bài toán vào cơ sở dữ liệu.")
        print(f"📁 Đã lưu vào: {target_file.relative_to(PROJECT_ROOT)}")
        print(f"   • Mã bài: {problem['id']}")
        print(f"   • Tiêu đề: {problem['title']}")
        print(f"   • Đáp án tối giản tự động: F = {problem['answer']}")
        print(f"   • Lời giải: {problem['answer_explanation']}")
        
        # Hiển thị bìa xem trước
        matrix = parse_grid_to_matrix(problem['kmap_grid'], num_vars)
        print("\n📋 Xem trước bìa Karnaugh:")
        print(format_kmap_text(matrix, num_vars))
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Lỗi khi thêm bài: {e}")


def main():
    parser = argparse.ArgumentParser(description="Công cụ tạo và thêm bài toán Karnaugh cho BiaK")
    parser.add_argument("--interactive", action="store_true", help="Chạy chế độ tương tác hỏi đáp")
    parser.add_argument("--id", type=str, help="Mã bài toán (ví dụ: B3-025)")
    parser.add_argument("--title", type=str, help="Tiêu đề bài toán")
    parser.add_argument("--level", type=str, choices=["basic", "advanced"], default="basic", help="Cấp độ")
    parser.add_argument("--vars", type=int, choices=[2, 3, 4, 5], default=3, help="Số biến")
    parser.add_argument("--groups", type=str, help="Các nhóm minterm, ví dụ: '0,1; 1,3'")
    parser.add_argument("--dont-cares", type=str, default="", help="Các minterm Don't Care ('X'), ví dụ: '5, 7'")
    parser.add_argument("--difficulty", type=int, default=2, help="Độ khó 1-10")
    parser.add_argument("--explanation", type=str, default="", help="Lời giải thích (tuỳ chọn)")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1 or args.interactive:
        interactive_mode()
    else:
        if not args.groups:
            print("❌ Vui lòng cung cấp --groups (ví dụ: --groups '0,1; 1,3')")
            sys.exit(1)
        if not args.id:
            print("❌ Vui lòng cung cấp --id (ví dụ: --id B3-025)")
            sys.exit(1)
            
        groups = parse_groups_input(args.groups)
        dont_cares = parse_dont_cares_input(args.dont_cares)
        title = args.title or f"Bài tập {args.vars} biến - {args.id}"
        
        try:
            p = add_problem_to_database(
                pid=args.id,
                title=title,
                level=args.level,
                num_vars=args.vars,
                minterm_groups=groups,
                difficulty=args.difficulty,
                explanation=args.explanation,
                dont_cares=dont_cares,
            )
            print(f"✅ Đã thêm thành công {p['id']}: F = {p['answer']}")
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
