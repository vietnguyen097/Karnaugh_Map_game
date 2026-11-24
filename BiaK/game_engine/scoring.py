#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scoring - Hệ thống tính điểm và thống kê cho game BiaK.
Theo quy tắc:
- Đúng lần 1: +10 điểm
- Đúng lần 2: +5 điểm
- Đúng từ lần 3 trở đi: +2 điểm
- Thưởng chuỗi thắng (Streak bonus): +2 điểm mỗi mốc 3 bài liên tiếp
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class AttemptResult:
    """Kết quả một lượt đoán của người chơi."""
    problem_id: str
    is_correct: bool
    points_awarded: int
    attempt_number: int
    user_answer: str


class ScoreManager:
    """Quản lý điểm số, chuỗi thắng và tiến trình trò chơi."""
    
    def __init__(self):
        self.score: int = 0
        self.streak: int = 0
        self.best_streak: int = 0
        self.total_solved: int = 0
        self.total_attempts: int = 0
        self.current_problem_attempts: int = 0
        self.history: List[Dict[str, Any]] = []
        self.solved_problem_ids: set = set()
        
    def reset_problem_attempts(self):
        """Đặt lại số lần thử khi chuyển sang bài toán mới."""
        self.current_problem_attempts = 0
        
    def record_attempt(
        self,
        problem_id: str,
        is_correct: bool,
        user_answer: str,
        difficulty: int = 1,
    ) -> AttemptResult:
        """
        Ghi nhận lượt thử và tính điểm tương ứng.
        
        Args:
            problem_id: Mã bài toán
            is_correct: Kết quả kiểm tra
            user_answer: Đáp án người dùng nhập
            difficulty: Độ khó của bài toán
            
        Returns:
            AttemptResult chứa thông tin điểm được cộng
        """
        self.total_attempts += 1
        self.current_problem_attempts += 1
        
        points = 0
        if is_correct:
            # Điểm cơ bản theo số lần thử
            if self.current_problem_attempts == 1:
                base_points = 10
            elif self.current_problem_attempts == 2:
                base_points = 5
            else:
                base_points = 2
                
            # Hệ số độ khó (độ khó >= 4 được thưởng thêm)
            diff_bonus = max(0, difficulty - 1)
            
            # Thưởng chuỗi thắng
            self.streak += 1
            if self.streak > self.best_streak:
                self.best_streak = self.streak
                
            streak_bonus = (self.streak // 3) * 2
            
            points = base_points + diff_bonus + streak_bonus
            self.score += points
            
            if problem_id not in self.solved_problem_ids:
                self.solved_problem_ids.add(problem_id)
                self.total_solved += 1
        else:
            # Đoán sai -> reset chuỗi thắng
            self.streak = 0
            
        result = AttemptResult(
            problem_id=problem_id,
            is_correct=is_correct,
            points_awarded=points,
            attempt_number=self.current_problem_attempts,
            user_answer=user_answer,
        )
        
        self.history.append({
            'problem_id': problem_id,
            'is_correct': is_correct,
            'points': points,
            'attempt': self.current_problem_attempts,
            'answer': user_answer,
        })
        
        return result
        
    def get_stats(self) -> Dict[str, Any]:
        """Trả về bản đồ thống kê đầy đủ."""
        accuracy = (self.total_solved / max(1, self.total_attempts)) * 100
        return {
            'score': self.score,
            'streak': self.streak,
            'best_streak': self.best_streak,
            'total_solved': self.total_solved,
            'total_attempts': self.total_attempts,
            'accuracy': round(accuracy, 1),
            'current_attempts': self.current_problem_attempts,
        }
        
    def reset_all(self):
        """Khởi động lại toàn bộ điểm số."""
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.total_solved = 0
        self.total_attempts = 0
        self.current_problem_attempts = 0
        self.history.clear()
        self.solved_problem_ids.clear()

