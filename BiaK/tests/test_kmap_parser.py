#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test K-Map Parser - Kiểm thử các hàm chuyển đổi và rút gọn bìa Karnaugh
"""

import unittest
from game_engine.kmap_parser import (
    get_kmap_dimensions,
    cell_to_binary,
    binary_to_cell,
    minterm_to_cell,
    cell_to_minterm,
    parse_grid_to_matrix,
    simplify_group,
    simplify_all_groups,
    format_kmap_text,
    get_variable_names,
)


class TestKMapParser(unittest.TestCase):
    
    def test_dimensions(self):
        for n, expected_rows, expected_cols in [(2, 2, 2), (3, 2, 4), (4, 4, 4), (5, 4, 8)]:
            dims = get_kmap_dimensions(n)
            self.assertEqual(dims['num_rows'], expected_rows)
            self.assertEqual(dims['num_cols'], expected_cols)
            self.assertEqual(dims['num_vars'], n)
            
    def test_coordinate_minterm_bijectivity(self):
        for n in [2, 3, 4, 5]:
            dims = get_kmap_dimensions(n)
            total = 1 << n
            visited_cells = set()
            for m in range(total):
                r, c = minterm_to_cell(m, n)
                self.assertTrue(0 <= r < dims['num_rows'])
                self.assertTrue(0 <= c < dims['num_cols'])
                
                # Chuyển ngược lại
                m_back = cell_to_minterm(r, c, n)
                self.assertEqual(m, m_back)
                
                cell_tuple = (r, c)
                self.assertNotIn(cell_tuple, visited_cells)
                visited_cells.add(cell_tuple)
                
            self.assertEqual(len(visited_cells), total)
            
    def test_simplify_single_cell(self):
        # 2 biến: m3 -> r=1, c=1 -> AB
        term = simplify_group([(1, 1)], 2)
        self.assertEqual(term, "AB")
        
        # 3 biến: m0 -> r=0, c=0 -> A'B'C'
        term = simplify_group([(0, 0)], 3)
        self.assertEqual(term, "A'B'C'")
        
    def test_simplify_row_col(self):
        # 2 biến: hàng A=0 -> cells (0,0) và (0,1) -> A'
        term = simplify_group([(0, 0), (0, 1)], 2)
        self.assertEqual(term, "A'")
        
        # 3 biến: hàng A=1 -> cells (1,0), (1,1), (1,2), (1,3) -> A
        term = simplify_group([(1, 0), (1, 1), (1, 2), (1, 3)], 3)
        self.assertEqual(term, "A")
        
    def test_simplify_wrap_around(self):
        # 3 biến: 2 cột ngoài cùng m(0, 2, 4, 6) -> C'
        # m0=(0,0), m2=(0,3), m4=(1,0), m6=(1,3)
        cells = [(0, 0), (0, 3), (1, 0), (1, 3)]
        term = simplify_group(cells, 3)
        self.assertEqual(term, "C'")
        
    def test_simplify_all_1s(self):
        # 2 biến: cả 4 ô bằng 1 -> '1'
        cells = [(0, 0), (0, 1), (1, 0), (1, 1)]
        term = simplify_group(cells, 2)
        self.assertEqual(term, "1")
        
    def test_simplify_empty(self):
        term = simplify_group([], 2)
        self.assertEqual(term, "0")
        
    def test_simplify_all_groups(self):
        groups = [
            {"id": 1, "cells": ["0,0", "0,1"]},
            {"id": 2, "cells": ["1,1", "1,2"]}
        ]
        sop = simplify_all_groups(groups, 3)
        self.assertIn("A'B'", sop)
        self.assertIn("AC", sop)
        
    def test_format_kmap_text(self):
        matrix = [[1, 0, 0, 1], [0, 1, 1, 0]]
        text = format_kmap_text(matrix, 3)
        self.assertIn("BÌA KARNAUGH", text)
        self.assertIn("A\\BC", text)


if __name__ == '__main__':
    unittest.main()
