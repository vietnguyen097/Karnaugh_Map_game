#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Scoring - Kiểm thử hệ thống tính điểm, chuỗi thắng và thống kê
"""

import unittest
from game_engine.scoring import ScoreManager


class TestScoring(unittest.TestCase):
    
    def setUp(self):
        self.mgr = ScoreManager()
        
    def test_first_attempt_points(self):
        res = self.mgr.record_attempt("B2-001", is_correct=True, user_answer="A'", difficulty=1)
        self.assertEqual(res.points_awarded, 10)
        self.assertEqual(self.mgr.score, 10)
        self.assertEqual(self.mgr.streak, 1)
        self.assertEqual(self.mgr.total_solved, 1)
        
    def test_second_attempt_points(self):
        # Lần 1 sai
        res1 = self.mgr.record_attempt("B2-001", is_correct=False, user_answer="B", difficulty=1)
        self.assertEqual(res1.points_awarded, 0)
        self.assertEqual(self.mgr.score, 0)
        self.assertEqual(self.mgr.streak, 0)
        
        # Lần 2 đúng -> +5 điểm
        res2 = self.mgr.record_attempt("B2-001", is_correct=True, user_answer="A'", difficulty=1)
        self.assertEqual(res2.points_awarded, 5)
        self.assertEqual(self.mgr.score, 5)
        self.assertEqual(self.mgr.streak, 1)
        
    def test_third_attempt_points(self):
        self.mgr.record_attempt("B2-001", False, "B")
        self.mgr.record_attempt("B2-001", False, "AB")
        res = self.mgr.record_attempt("B2-001", True, "A'")
        self.assertEqual(res.points_awarded, 2)
        self.assertEqual(self.mgr.score, 2)
        
    def test_streak_bonus(self):
        # 3 bài đúng liên tiếp lần đầu: 10 + 10 + (10 + 2 bonus) = 32
        self.mgr.reset_problem_attempts()
        self.mgr.record_attempt("P1", True, "ans")
        self.mgr.reset_problem_attempts()
        self.mgr.record_attempt("P2", True, "ans")
        self.mgr.reset_problem_attempts()
        res3 = self.mgr.record_attempt("P3", True, "ans")
        
        self.assertEqual(self.mgr.streak, 3)
        self.assertEqual(res3.points_awarded, 12)  # 10 + 2 bonus
        self.assertEqual(self.mgr.score, 32)
        
    def test_streak_reset_on_failure(self):
        self.mgr.record_attempt("P1", True, "ans")
        self.assertEqual(self.mgr.streak, 1)
        self.mgr.record_attempt("P2", False, "wrong")
        self.assertEqual(self.mgr.streak, 0)
        self.assertEqual(self.mgr.best_streak, 1)

    def test_stats(self):
        self.mgr.record_attempt("P1", True, "ans")
        self.mgr.record_attempt("P2", False, "wrong")
        stats = self.mgr.get_stats()
        self.assertEqual(stats['total_attempts'], 2)
        self.assertEqual(stats['total_solved'], 1)
        self.assertEqual(stats['accuracy'], 50.0)


if __name__ == '__main__':
    unittest.main()

