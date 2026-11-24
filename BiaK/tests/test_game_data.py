#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Game Data - Kiểm thử toàn vẹn dữ liệu cho toàn bộ 40 bài toán Karnaugh
Đảm bảo tất cả các bài đều có cấu trúc hợp lệ và đáp án được kiểm định 100%.
"""

import unittest
from game_data.game_data import (
    load_all_problems,
    load_basic_problems,
    load_advanced_problems,
    get_problem_by_id,
    get_problems_by_variable_count,
)
from game_engine.validator import validate_answer
from game_engine.kmap_parser import simplify_all_groups


class TestGameData(unittest.TestCase):
    
    def setUp(self):
        self.all_problems = load_all_problems()
        
    def test_database_counts(self):
        basic = self.all_problems['basic']
        advanced = self.all_problems['advanced']
        self.assertGreaterEqual(len(basic), 20)
        self.assertGreaterEqual(len(advanced), 15)
        
    def test_all_problems_validity(self):
        """Kiểm tra từng bài toán trong toàn bộ cơ sở dữ liệu."""
        all_list = self.all_problems['basic'] + self.all_problems['advanced']
        seen_ids = set()
        
        for p in all_list:
            pid = p.get('id')
            self.assertIsNotNone(pid)
            self.assertNotIn(pid, seen_ids, f"ID trùng lặp: {pid}")
            seen_ids.add(pid)
            
            # Kiểm tra trường bắt buộc
            self.assertIn('title', p)
            self.assertIn('num_vars', p)
            self.assertIn('kmap_grid', p)
            self.assertIn('groups', p)
            self.assertIn('answer', p)
            self.assertIn('difficulty', p)
            
            nvars = p['num_vars']
            self.assertTrue(2 <= nvars <= 5)
            
            # Kiểm tra số ô trong grid
            expected_cells = 1 << nvars
            self.assertEqual(len(p['kmap_grid']), expected_cells, f"Số ô grid không khớp ở bài {pid}")
            
            # Kiểm tra đáp án với validator
            val = validate_answer(p['answer'], p, nvars)
            self.assertTrue(
                val['is_correct'],
                f"Bài {pid} kiểm định thất bại: {val['message']} (đáp án={p['answer']})"
            )
            
    def test_get_by_id(self):
        p = get_problem_by_id("B2-001")
        self.assertIsNotNone(p)
        self.assertEqual(p['id'], "B2-001")
        
        p_none = get_problem_by_id("NONEXISTENT_999")
        self.assertIsNone(p_none)
        
    def test_filter_by_variable_count(self):
        for n in [2, 3, 4, 5]:
            probs = get_problems_by_variable_count(n)
            self.assertTrue(len(probs) > 0)
            for p in probs:
                self.assertEqual(p['num_vars'], n)


if __name__ == '__main__':
    unittest.main()

