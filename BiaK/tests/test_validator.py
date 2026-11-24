#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Validator - Kiểm thử bộ phân tích cú pháp và kiểm tra đáp án logic
"""

import unittest
from game_engine.validator import (
    tokenize_expression,
    evaluate_expression,
    compute_truth_table,
    canonicalize_term,
    parse_sop_terms,
    is_logically_equivalent,
    validate_answer,
    normalize_expression_str,
)


class TestValidator(unittest.TestCase):
    
    def test_tokenization_and_implicit_and(self):
        # AB -> A * B
        tokens = tokenize_expression("AB")
        self.assertEqual(tokens, ['A', '*', 'B'])
        
        # A'B -> A ' * B
        tokens = tokenize_expression("A'B")
        self.assertEqual(tokens, ['A', "'", '*', 'B'])
        
        # A'B + CD' -> A ' * B + C * D '
        tokens = tokenize_expression("A'B + CD'")
        self.assertEqual(tokens, ['A', "'", '*', 'B', '+', 'C', '*', 'D', "'"])
        
        # ~A B -> ~ A * B
        tokens = tokenize_expression("~AB")
        self.assertEqual(tokens, ['~', 'A', '*', 'B'])
        
        # (A+B)(C+D) -> ( A + B ) * ( C + D )
        tokens = tokenize_expression("(A+B)(C+D)")
        self.assertEqual(tokens, ['(', 'A', '+', 'B', ')', '*', '(', 'C', '+', 'D', ')'])

    def test_evaluate_basic(self):
        # A and B
        self.assertTrue(evaluate_expression("AB", {'A': True, 'B': True}))
        self.assertFalse(evaluate_expression("AB", {'A': True, 'B': False}))
        
        # A' or B
        self.assertTrue(evaluate_expression("A' + B", {'A': False, 'B': False}))
        self.assertFalse(evaluate_expression("A' + B", {'A': True, 'B': False}))
        self.assertTrue(evaluate_expression("A' + B", {'A': True, 'B': True}))
        
        # Constants
        self.assertTrue(evaluate_expression("1", {}))
        self.assertFalse(evaluate_expression("0", {}))

    def test_truth_table_equivalence(self):
        # De Morgan: (A + B)' == A'B'
        self.assertTrue(is_logically_equivalent("(A + B)'", "A'B'", 2))
        
        # XOR: A'B + AB'
        self.assertTrue(is_logically_equivalent("A'B + AB'", "BA' + B'A", 2))
        
        # Distributive: A(B + C) == AB + AC
        self.assertTrue(is_logically_equivalent("A(B + C)", "AB + AC", 3))

    def test_canonicalize_terms(self):
        term1 = canonicalize_term("B'A")
        term2 = canonicalize_term("AB'")
        self.assertEqual(term1, term2)
        self.assertEqual(term1, (('A', 1), ('B', 0)))

    def test_validate_answer_exact(self):
        mock_problem = {
            "id": "T-001",
            "num_vars": 2,
            "answer": "A'B + AB'",
            "kmap_grid": [
                {"row": 0, "col": 0, "value": 0},
                {"row": 0, "col": 1, "value": 1},
                {"row": 1, "col": 0, "value": 1},
                {"row": 1, "col": 1, "value": 0},
            ]
        }
        
        # Đáp án chuẩn
        res = validate_answer("A'B + AB'", mock_problem, 2)
        self.assertTrue(res['is_correct'])
        
        # Đảo thứ tự tích
        res = validate_answer("AB' + A'B", mock_problem, 2)
        self.assertTrue(res['is_correct'])
        
        # Đảo thứ tự biến trong tích
        res = validate_answer("BA' + B'A", mock_problem, 2)
        self.assertTrue(res['is_correct'])
        
        # Dùng ký hiệu NOT khác: ~ hoặc !
        res = validate_answer("~A B + A ~B", mock_problem, 2)
        self.assertTrue(res['is_correct'])

    def test_validate_unsimplified_answer(self):
        mock_problem = {
            "id": "T-002",
            "num_vars": 2,
            "answer": "A'",
            "kmap_grid": [
                {"row": 0, "col": 0, "value": 1},
                {"row": 0, "col": 1, "value": 1},
                {"row": 1, "col": 0, "value": 0},
                {"row": 1, "col": 1, "value": 0},
            ]
        }
        # Đáp án tương đương logic nhưng chưa tối giản (tổng minterm)
        res = validate_answer("A'B' + A'B", mock_problem, 2)
        self.assertFalse(res['is_correct'])
        self.assertTrue(res['is_equivalent'])
        self.assertIn("chưa gom hết các nhóm", res['message'])

    def test_validate_wrong_answer(self):
        mock_problem = {
            "id": "T-003",
            "num_vars": 2,
            "answer": "A",
            "kmap_grid": [
                {"row": 0, "col": 0, "value": 0},
                {"row": 0, "col": 1, "value": 0},
                {"row": 1, "col": 0, "value": 1},
                {"row": 1, "col": 1, "value": 1},
            ]
        }
        res = validate_answer("B", mock_problem, 2)
        self.assertFalse(res['is_correct'])
        self.assertFalse(res['is_equivalent'])

    def test_validate_answer_with_dont_care(self):
        # 3 biến: F = Σm(1, 3, 7) + d(5) -> gom 4 ô -> C
        mock_problem = {
            "id": "T-DC-001",
            "num_vars": 3,
            "answer": "C",
            "dont_cares": [5],
            "kmap_grid": [
                {"row": 0, "col": 0, "value": 0},
                {"row": 0, "col": 1, "value": 1},  # m1
                {"row": 0, "col": 2, "value": 1},  # m3
                {"row": 0, "col": 3, "value": 0},
                {"row": 1, "col": 0, "value": 0},
                {"row": 1, "col": 1, "value": "X"}, # m5 (don't care)
                {"row": 1, "col": 2, "value": 1},  # m7
                {"row": 1, "col": 3, "value": 0},
            ]
        }
        res = validate_answer("C", mock_problem, 3)
        self.assertTrue(res['is_correct'])
        self.assertTrue(res['is_simplified'])


if __name__ == '__main__':
    unittest.main()

