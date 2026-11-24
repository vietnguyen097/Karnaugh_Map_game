# -*- coding: utf-8 -*-
"""
Generator tạo bài toán Karnaugh 2 biến (Cơ bản)
Tự động sinh thêm các bài tập mới cho file variables_2.json
"""

import json
from pathlib import Path


def generate_basic_2var_problems():
    """
    Tạo thêm các bài toán Karnaugh 2 biến cơ bản.
    
    Mỗi bài có:
    - F = f(A,B) với grid 2x4 (2 hàng, 4 cột)
    - Có thể có nhóm 2, nhóm 1, hoặc nhóm 4 ô
    """
    problems = []
    
    # Danh sách các mẫu K-map cơ bản cho 2 biến
    basic_patterns = [
        {
            'title': "Hàm F = B'",
            'description': "Nhóm toàn bộ hàng B=0",
            'grid_values': [[1, 1, 1, 1], [0, 0, 0, 0]],
            'answer': 'B\'',
            'answer_explanation': 'Toàn bộ hàng đầu (A=0) đều có giá trị 1'
        },
        {
            'title': "Hàm F = A'",
            'description': "Nhóm toàn bộ cột A=0",
            'grid_values': [[1, 0], [1, 0]],
            'answer': 'A\'',
            'answer_explanation': 'Cột đầu và thứ ba đều có giá trị 1'
        },
        {
            'title': "Hàm F = AB",
            'description': "Chỉ một ô đơn độc tại A=1, B=1",
            'grid_values': [[0, 0], [0, 1]],
            'answer': 'AB',
            'answer_explanation': 'Chỉ có ô (A=1, B=1) mang giá trị 1'
        },
        {
            'title': "Hàm F = A\'B",
            'description': "Nhóm hai ô liền kề tại hàng A=0",
            'grid_values': [[1, 0], [0, 0]],
            'answer': 'A\'B',
            'answer_explanation': 'Ô (A=0, B=1) mang giá trị 1'
        },
        {
            'title': "Hàm F = A'B'",
            'description': "Nhóm hai ô đối diện tại hàng đầu",
            'grid_values': [[1, 0], [1, 0]],
            'answer': 'A\'B\'',
            'answer_explanation': 'Cột đầu và thứ ba đều có giá trị 1 tại A=0'
        },
        {
            'title': "Hàm F = AB + A'B'",
            'description': "Hai nhóm đối diện (hàng đầu)",
            'grid_values': [[1, 0], [1, 0]],
            'answer': 'A\'B\'',
            'answer_explanation': 'Toàn bộ hàng A=0 đều có giá trị 1'
        },
        {
            'title': "Hàm F = AB + AB'",
            'description': "Nhóm cột B=1",
            'grid_values': [[0, 1], [0, 1]],
            'answer': 'B',
            'answer_explanation': 'Cột thứ hai và thứ tư đều có giá trị 1'
        },
        {
            'title': "Hàm F = A'B + AB",
            'description': "Nhóm cột A=0",
            'grid_values': [[1, 0], [1, 0]],
            'answer': 'A\'',
            'answer_explanation': 'Hai ô tại A=0 đều mang giá trị 1'
        }
    ]
    
    for idx, pattern in enumerate(basic_patterns):
        problem = {
            "id": f"B2-EXT-{idx+1:03d}",
            "title": pattern['title'],
            "kmap_grid": [
                {"row": 0, "col": c, "value": v} for c, v in enumerate(pattern['grid_values'][0])
            ] + [
                {"row": 1, "col": c, "value": v} for c, v in enumerate(pattern['grid_values'][1])
            ],
            "groups": [
                {
                    "id": 1,
                    "cells": ["0,0"] if pattern['grid_values'][0][0] == 1 else [],
                    "color": "#4CAF50"
                }
            ],
            "answer": pattern['answer'],
            "answer_explanation": pattern['answer_explanation'],
            "difficulty": 1
        }
        
        # Sinh chính xác các ô có giá trị 1
        grid = pattern['grid_values']
        cells_with_1 = []
        for r_idx, row in enumerate(grid):
            for c_idx, val in enumerate(row):
                if val == 1:
                    cells_with_1.append(f"{r_idx},{c_idx}")
        
        # Tạo nhóm từ các ô có giá trị 1
        if cells_with_1:
            problem['groups'] = [{
                "id": 1,
                "cells": cells_with_1,
                "color": "#4CAF50"
            }]
        
        problems.append(problem)
    
    return problems


def main():
    """
    Tạo file mới chứa bài toán Karnaugh 2 biến cơ bản.
    """
    output_file = Path('BiaK/game_data/basic_kmap/variables_2_extended.json')
    
    # Sinh các bài toán
    new_problems = generate_basic_2var_problems()
    
    # Lưu ra file JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "level": "basic",
            "category": "2_variables_extended",
            "description": "Các bài toán Karnaugh 2 biến cơ bản (phần mở rộng)",
            "problems": new_problems,
            "total_count": len(new_problems)
        }, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Đã tạo {len(new_problems)} bài toán mới!")
    print(f"📁 File: {output_file}")
    
    # Hiển thị thống kê
    total_1 = len(json.load(open('BiaK/game_data/basic_kmap/variables_2.json', 'r', encoding='utf-8')).get('problems', []))
    total_2 = len(new_problems)
    print(f"📊 Tổng số bài 2 biến: {total_1 + total_2}")


if __name__ == '__main__':
    main()