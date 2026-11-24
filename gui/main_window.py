#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Window - Cửa sổ chính của trò chơi BiaK
Giao diện người dùng đồ họa hiện đại phong cách Modern Soft Charcoal & Slate:
- Thẻ bề mặt bo góc tự co giãn (RoundedCard) cho cả 2 cột Trái & Phải
- Độ tương phản đồng nhất, chữ đọc êm dịu, không gây chói mắt hay nhòe chữ
- HUD thống kê chỉ số thời gian thực, bộ lọc chip & capsule mượt mà
"""

import tkinter as tk
from tkinter import messagebox
import random
from typing import Dict, List, Any, Optional, Tuple

from game_engine.scoring import ScoreManager
from game_engine.validator import validate_answer
from game_engine.kmap_parser import simplify_group, cell_to_minterm, solve_pos_expression, get_pos_groups
from game_data.game_data import load_all_problems
from .kmap_display import KMapDisplay, GROUP_PALETTE
from .input_handler import InputHandler
from .rounded_widgets import THEME, RoundedCard, draw_rounded_rect


class MainWindow(tk.Tk):
    """Cửa sổ chính của game BiaK với giao diện bo góc dịu mắt và độ tương phản chuẩn."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, db: Optional[Dict[str, Any]] = None):
        super().__init__()
        
        self.config = config or {}
        self.title("BiaK - Karnaugh Map Laboratory")
        self.geometry("1120x760")
        self.minsize(980, 680)
        self.configure(bg=THEME["bg_root"])
        
        # Tải database
        self.db = db if db else load_all_problems()
        self.score_manager = ScoreManager()
        
        # Bộ lọc trạng thái hiện tại
        self.current_level = "basic"  # 'basic' hoặc 'advanced'
        self.current_var_filter = 0   # 0: Tất cả, 2, 3, 4, 5
        self.filtered_problems: List[Dict[str, Any]] = []
        self.current_problem_idx: int = 0
        self.current_problem: Optional[Dict[str, Any]] = None
        self.solution_revealed: bool = False
        self.current_mode: str = "SOP"  # "SOP" hoặc "POS"
        
        self._build_ui()
        self._apply_filter()
        
    def _build_ui(self):
        """Xây dựng bố cục giao diện bo góc đồng nhất."""
        
        # 1. Thanh ứng dụng trên cùng (App Bar)
        app_bar = tk.Frame(self, bg=THEME["bg_inner"], height=52, bd=0)
        app_bar.pack(fill=tk.X, side=tk.TOP)
        app_bar.pack_propagate(False)
        
        # Logo Badge + Tên ứng dụng
        brand_frame = tk.Frame(app_bar, bg=THEME["bg_inner"])
        brand_frame.pack(side=tk.LEFT, padx=16, pady=8)
        
        logo_badge = tk.Label(
            brand_frame,
            text="BIAK",
            font=("Consolas", 11, "bold"),
            bg=THEME["accent_primary"],
            fg="#FFFFFF",
            padx=8,
            pady=2
        )
        logo_badge.pack(side=tk.LEFT, padx=(0, 10))
        
        title_lbl = tk.Label(
            brand_frame,
            text="Karnaugh Map Laboratory",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["bg_inner"],
            fg=THEME["text_primary"]
        )
        title_lbl.pack(side=tk.LEFT)
        
        version_pill = tk.Label(
            brand_frame,
            text="v1.0 • 500 bài tập",
            font=("Segoe UI", 9),
            bg="#1E2838",
            fg=THEME["text_muted"],
            padx=8,
            pady=2
        )
        version_pill.pack(side=tk.LEFT, padx=10)
        
        # Cụm chuyển cấp độ Segmented Capsule
        capsule_frame = tk.Frame(app_bar, bg="#1E2838", padx=3, pady=3)
        capsule_frame.pack(side=tk.RIGHT, padx=16)
        
        self.btn_level_basic = tk.Button(
            capsule_frame,
            text="Cơ Bản (2-3 biến)",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["accent_primary"],
            fg="#FFFFFF",
            activebackground="#4338CA",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=3,
            cursor="hand2",
            command=lambda: self._set_level("basic")
        )
        self.btn_level_basic.pack(side=tk.LEFT)
        
        self.btn_level_adv = tk.Button(
            capsule_frame,
            text="Nâng Cao (3-5 biến)",
            font=("Segoe UI", 9),
            bg="#1E2838",
            fg=THEME["text_muted"],
            activebackground="#2A384E",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=3,
            cursor="hand2",
            command=lambda: self._set_level("advanced")
        )
        self.btn_level_adv.pack(side=tk.LEFT)
        
        # Cụm chuyển dạng tối giản SOP / POS
        mode_capsule = tk.Frame(app_bar, bg="#1E2838", padx=3, pady=3)
        mode_capsule.pack(side=tk.RIGHT, padx=8)
        
        tk.Label(
            mode_capsule, text="DẠNG:", font=("Segoe UI", 8, "bold"),
            bg="#1E2838", fg=THEME["text_muted"]
        ).pack(side=tk.LEFT, padx=(4, 4))
        
        self.btn_mode_sop = tk.Button(
            mode_capsule,
            text="SOP",
            font=("Consolas", 9, "bold"),
            bg=THEME["accent_primary"],
            fg="#FFFFFF",
            activebackground="#4338CA",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=lambda: self._set_mode("SOP")
        )
        self.btn_mode_sop.pack(side=tk.LEFT)
        
        self.btn_mode_pos = tk.Button(
            mode_capsule,
            text="POS",
            font=("Consolas", 9),
            bg="#1E2838",
            fg=THEME["text_muted"],
            activebackground="#2A384E",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=lambda: self._set_mode("POS")
        )
        self.btn_mode_pos.pack(side=tk.LEFT)
        
        # 2. Thanh thống kê chỉ số (Stats HUD Bar)
        hud_bar = tk.Frame(self, bg=THEME["bg_card"], height=48)
        hud_bar.pack(fill=tk.X, padx=16, pady=(10, 6))
        hud_bar.pack_propagate(False)
        
        # Các thẻ chỉ số phong cách Dashboard dịu mắt
        self.lbl_score_val = self._create_hud_stat(hud_bar, "SCORE", "0", THEME["accent_cyan"])
        self.lbl_streak_val = self._create_hud_stat(hud_bar, "STREAK", "0", THEME["accent_amber"])
        self.lbl_solved_val = self._create_hud_stat(hud_bar, "SOLVED", "0", THEME["accent_green"])
        self.lbl_accuracy_val = self._create_hud_stat(hud_bar, "ACCURACY", "0%", "#A78BFA")
        
        # Cụm chip lọc số biến bên phải
        filter_box = tk.Frame(hud_bar, bg=THEME["bg_card"])
        filter_box.pack(side=tk.RIGHT, padx=14)
        
        tk.Label(
            filter_box, text="LỌC BIẾN:", font=("Segoe UI", 8, "bold"),
            bg=THEME["bg_card"], fg=THEME["text_muted"]
        ).pack(side=tk.LEFT, padx=(0, 6))
        
        self.var_filter_buttons = {}
        for num in [0, 2, 3, 4, 5]:
            lbl_txt = "Tất cả" if num == 0 else f"{num}V"
            btn = tk.Button(
                filter_box,
                text=lbl_txt,
                font=("Consolas", 9, "bold"),
                bg=THEME["accent_primary"] if num == 0 else "#243044",
                fg="#FFFFFF" if num == 0 else THEME["text_muted"],
                activebackground="#33425E",
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda n=num: self._set_var_filter(n)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.var_filter_buttons[num] = btn

        # 3. Khu vực chính (Split Pane Bo Góc: Trái K-map, Phải Điều khiển & Lời giải)
        main_content = tk.Frame(self, bg=THEME["bg_root"])
        main_content.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)
        
        # --- CỘT TRÁI: Thẻ Bìa Karnaugh Bo Góc ---
        self.left_card = RoundedCard(
            main_content,
            bg_color=THEME["bg_root"],
            card_bg=THEME["bg_card"],
            border_color=THEME["border_card"],
            radius=14,
            pad=12
        )
        self.left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        left_body = self.left_card.content
        
        # Header thẻ bài toán
        prob_header = tk.Frame(left_body, bg=THEME["bg_card"])
        prob_header.pack(fill=tk.X, padx=8, pady=(4, 6))
        
        self.lbl_prob_id = tk.Label(
            prob_header,
            text="[B3-001]",
            font=("Consolas", 10, "bold"),
            bg="#243044",
            fg="#818CF8",
            padx=8,
            pady=2
        )
        self.lbl_prob_id.pack(side=tk.LEFT)
        
        self.lbl_prob_title = tk.Label(
            prob_header,
            text="Tiêu đề bài toán",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["text_primary"]
        )
        self.lbl_prob_title.pack(side=tk.LEFT, padx=10)
        
        self.lbl_dc_badge = tk.Label(
            prob_header,
            text="DON'T CARE (X)",
            font=("Segoe UI", 8, "bold"),
            bg="#2E2310",
            fg=THEME["accent_amber"],
            padx=6,
            pady=1
        )
        # Sẽ pack khi có Don't Care
        
        self.lbl_difficulty_dots = tk.Label(
            prob_header,
            text="● ● ○ ○ ○",
            font=("Segoe UI", 10),
            bg=THEME["bg_card"],
            fg=THEME["accent_amber"]
        )
        self.lbl_difficulty_dots.pack(side=tk.RIGHT)
        
        # Canvas bìa Karnaugh bo góc
        self.kmap_display = KMapDisplay(left_body)
        self.kmap_display.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Chú thích nhóm (Legend)
        self.legend_frame = tk.Frame(left_body, bg=THEME["bg_card"])
        self.legend_frame.pack(fill=tk.X, padx=8, pady=(4, 6))
        
        # --- CỘT PHẢI: Thẻ Điều Khiển, Nhập Liệu & Lời Giải Bo Góc ---
        self.right_card = RoundedCard(
            main_content,
            bg_color=THEME["bg_root"],
            card_bg=THEME["bg_card"],
            border_color=THEME["border_card"],
            radius=14,
            pad=12,
            width=420
        )
        self.right_card.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(6, 0))
        right_body = self.right_card.content
        
        # Bàn phím & thanh nhập công thức
        self.input_handler = InputHandler(
            right_body,
            on_submit_callback=self._handle_submit
        )
        self.input_handler.pack(fill=tk.X, padx=4, pady=(2, 4))
        
        # Thông báo phản hồi Toast Banner bo tròn
        self.feedback_frame = tk.Frame(right_body, bg=THEME["bg_inner"], padx=10, pady=8)
        self.feedback_frame.pack(fill=tk.X, padx=8, pady=4)
        
        self.lbl_feedback = tk.Label(
            self.feedback_frame,
            text="Quan sát các ô giá trị 1 và nhóm khoanh để nhập biểu thức tối giản SOP.",
            font=("Segoe UI", 9),
            bg=THEME["bg_inner"],
            fg=THEME["text_body"],
            wraplength=360,
            justify=tk.LEFT
        )
        self.lbl_feedback.pack(fill=tk.X)
        
        # Cụm nút thao tác
        tools_row = tk.Frame(right_body, bg=THEME["bg_card"])
        tools_row.pack(fill=tk.X, padx=8, pady=4)
        
        self.btn_hint = tk.Button(
            tools_row,
            text="Gợi ý",
            font=("Segoe UI", 9, "bold"),
            bg="#2E2310",
            fg=THEME["accent_amber"],
            activebackground="#3D3017",
            activeforeground="#FDE68A",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self._show_hint
        )
        self.btn_hint.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=4)
        
        self.btn_reveal = tk.Button(
            tools_row,
            text="Xem lời giải",
            font=("Segoe UI", 9),
            bg="#243044",
            fg=THEME["text_body"],
            activebackground="#33425E",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self._reveal_solution
        )
        self.btn_reveal.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=4)
        
        self.btn_next = tk.Button(
            tools_row,
            text="Bài tiếp  →",
            font=("Segoe UI", 9, "bold"),
            bg="#15803D",
            fg="#FFFFFF",
            activebackground="#166534",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self._next_problem
        )
        self.btn_next.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=4)
        
        # Khung lời giải chi tiết (Terminal Code Card bo góc)
        self.solution_frame = tk.Frame(
            right_body,
            bg=THEME["bg_inner"],
            bd=1,
            relief=tk.SOLID,
            highlightbackground=THEME["border_inner"],
            highlightthickness=1
        )
        self.solution_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 6))
        
        header_sol = tk.Frame(self.solution_frame, bg=THEME["bg_inner"])
        header_sol.pack(fill=tk.X, padx=10, pady=(6, 2))
        
        tk.Label(
            header_sol, text="PHÂN TÍCH RÚT GỌN",
            font=("Segoe UI", 8, "bold"), bg=THEME["bg_inner"], fg=THEME["text_muted"]
        ).pack(side=tk.LEFT)
        
        self.lbl_solution_text = tk.Label(
            self.solution_frame,
            text="Nhập đáp án rồi nhấn 'Kiểm tra', hoặc bấm 'Gợi ý' để nhận trợ giúp.",
            font=("Consolas", 9), bg=THEME["bg_inner"], fg=THEME["text_body"],
            wraplength=355, justify=tk.LEFT
        )
        self.lbl_solution_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 6))

        # 4. Thanh điều hướng chân trang (Footer Bar)
        footer = tk.Frame(self, bg=THEME["bg_inner"], height=36)
        footer.pack(fill=tk.X, side=tk.BOTTOM, padx=16, pady=(2, 8))
        footer.pack_propagate(False)
        
        self.lbl_counter = tk.Label(
            footer, text="Bài 1 / 80", font=("Consolas", 9, "bold"),
            bg=THEME["bg_inner"], fg=THEME["text_body"]
        )
        self.lbl_counter.pack(side=tk.LEFT, padx=10)
        
        btn_prev = tk.Button(
            footer, text="← Trước", font=("Segoe UI", 9),
            bg="#243044", fg=THEME["text_body"], activebackground="#33425E",
            relief=tk.FLAT, bd=0, padx=8, pady=2, cursor="hand2", command=self._prev_problem
        )
        btn_prev.pack(side=tk.LEFT, padx=3)
        
        btn_next_bot = tk.Button(
            footer, text="Sau →", font=("Segoe UI", 9),
            bg="#243044", fg=THEME["text_body"], activebackground="#33425E",
            relief=tk.FLAT, bd=0, padx=8, pady=2, cursor="hand2", command=self._next_problem
        )
        btn_next_bot.pack(side=tk.LEFT, padx=3)
        
        btn_rand = tk.Button(
            footer, text="Ngẫu nhiên", font=("Segoe UI", 9),
            bg="#243044", fg=THEME["accent_cyan"], activebackground="#33425E",
            relief=tk.FLAT, bd=0, padx=8, pady=2, cursor="hand2", command=self._random_problem
        )
        btn_rand.pack(side=tk.LEFT, padx=5)
        
        lbl_tip = tk.Label(
            footer,
            text="Gõ trực tiếp A, B, C, ', + từ bàn phím và nhấn Enter để kiểm tra nhanh",
            font=("Segoe UI", 8), bg=THEME["bg_inner"], fg=THEME["text_muted"]
        )
        lbl_tip.pack(side=tk.RIGHT, padx=10)

    def _create_hud_stat(self, parent, label_text: str, default_val: str, val_color: str) -> tk.Label:
        """Tạo một khối chỉ số HUD tinh gọn với độ tương phản dịu mắt."""
        box = tk.Frame(parent, bg=THEME["bg_card"], padx=12, pady=2)
        box.pack(side=tk.LEFT, padx=6)
        
        tk.Label(
            box, text=label_text, font=("Segoe UI", 7, "bold"),
            bg=THEME["bg_card"], fg=THEME["text_muted"]
        ).pack(anchor="w")
        
        val_lbl = tk.Label(
            box, text=default_val, font=("Consolas", 13, "bold"),
            bg=THEME["bg_card"], fg=val_color
        )
        val_lbl.pack(anchor="w")
        return val_lbl

    def _set_level(self, level: str):
        """Đổi cấp độ: Cơ bản hoặc Nâng cao."""
        if self.current_level == level:
            return
        self.current_level = level
        if level == "basic":
            self.btn_level_basic.config(bg=THEME["accent_primary"], fg="#FFFFFF", font=("Segoe UI", 9, "bold"))
            self.btn_level_adv.config(bg="#1E2838", fg=THEME["text_muted"], font=("Segoe UI", 9))
        else:
            self.btn_level_basic.config(bg="#1E2838", fg=THEME["text_muted"], font=("Segoe UI", 9))
            self.btn_level_adv.config(bg=THEME["accent_primary"], fg="#FFFFFF", font=("Segoe UI", 9, "bold"))
            
        self.current_var_filter = 0
        self._apply_filter()

    def _set_mode(self, mode: str):
        """Đổi dạng rút gọn: SOP (Sum of Products) hoặc POS (Product of Sums)."""
        if self.current_mode == mode:
            return
        self.current_mode = mode
        if mode == "SOP":
            self.btn_mode_sop.config(bg=THEME["accent_primary"], fg="#FFFFFF", font=("Consolas", 9, "bold"))
            self.btn_mode_pos.config(bg="#1E2838", fg=THEME["text_muted"], font=("Consolas", 9))
        else:
            self.btn_mode_sop.config(bg="#1E2838", fg=THEME["text_muted"], font=("Consolas", 9))
            self.btn_mode_pos.config(bg=THEME["accent_primary"], fg="#FFFFFF", font=("Consolas", 9, "bold"))
        
        # Cập nhật lại giao diện và thông báo cho bài hiện tại
        if self.current_problem:
            self._load_problem_index(self.current_problem_idx)

    def _set_var_filter(self, num_vars: int):
        """Lọc bài toán theo số biến."""
        self.current_var_filter = num_vars
        for num, btn in self.var_filter_buttons.items():
            if num == num_vars:
                btn.config(bg=THEME["accent_primary"], fg="#FFFFFF")
            else:
                btn.config(bg="#243044", fg=THEME["text_muted"])
        self._apply_filter()

    def _apply_filter(self):
        """Lọc danh sách bài toán theo cấp độ và số biến (tự động chuyển tab thông minh)."""
        # Tự động đồng bộ cấp độ phù hợp khi người dùng chọn số biến
        if self.current_var_filter in (4, 5) and self.current_level != "advanced":
            self.current_level = "advanced"
            self.btn_level_basic.config(bg="#1E2838", fg=THEME["text_muted"], font=("Segoe UI", 9))
            self.btn_level_adv.config(bg=THEME["accent_primary"], fg="#FFFFFF", font=("Segoe UI", 9, "bold"))
        elif self.current_var_filter == 2 and self.current_level != "basic":
            self.current_level = "basic"
            self.btn_level_basic.config(bg=THEME["accent_primary"], fg="#FFFFFF", font=("Segoe UI", 9, "bold"))
            self.btn_level_adv.config(bg="#1E2838", fg=THEME["text_muted"], font=("Segoe UI", 9))

        source = self.db.get(self.current_level, [])
        if self.current_var_filter > 0:
            self.filtered_problems = [p for p in source if p.get('num_vars') == self.current_var_filter]
        else:
            self.filtered_problems = list(source)
            
        self.current_problem_idx = 0
        if self.filtered_problems:
            self._load_problem_index(0)
        else:
            self._set_feedback("Không có bài toán phù hợp với bộ lọc hiện tại.", "warning")

    def _load_problem_index(self, idx: int):
        """Nạp bài toán theo chỉ số trong danh sách đã lọc."""
        if not self.filtered_problems:
            return
        self.current_problem_idx = idx % len(self.filtered_problems)
        self.current_problem = self.filtered_problems[self.current_problem_idx]
        self.solution_revealed = False
        self.score_manager.reset_problem_attempts()
        
        p = self.current_problem
        self.lbl_prob_id.config(text=f"[{p.get('id', 'KMAP')}]")
        self.lbl_prob_title.config(text=p.get('title', 'Bài toán'))
        
        # Biểu diễn độ khó dạng pips tối giản
        diff = p.get('difficulty', 1)
        filled_dots = min(diff, 5)
        pips_text = "● " * filled_dots + "○ " * (5 - filled_dots)
        self.lbl_difficulty_dots.config(text=pips_text.strip())
        
        # Don't Care Badge
        grid = p.get('kmap_grid', [])
        has_dc = any(str(c.get('value', '')).upper() in ('X', 'D') for c in grid)
        if has_dc:
            self.lbl_dc_badge.pack(side=tk.LEFT, padx=6)
        else:
            self.lbl_dc_badge.pack_forget()
            
        # Cập nhật số bài
        total = len(self.filtered_problems)
        self.lbl_counter.config(text=f"Bài {self.current_problem_idx + 1} / {total}")
        
        num_vars = p.get('num_vars', 3)

        # Lấy danh sách nhóm theo chế độ SOP hoặc POS
        if self.current_mode == "POS":
            active_groups, pos_ans = self._get_pos_data(p, num_vars)
        else:
            active_groups = p.get('groups', [])

        # Cập nhật K-map display với nhóm và chế độ màu phù hợp
        self.kmap_display.load_problem(p, custom_groups=active_groups, mode=self.current_mode)
        
        # Cập nhật danh sách biến
        self.input_handler.set_available_variables(num_vars)
        self.input_handler.clear()
        
        # Reset toast feedback
        if self.current_mode == "POS":
            self._set_feedback("[DẠNG POS] Quan sát các nhóm ô 0 được khoanh màu (và X) để nhập tích các tổng F = (A+B)(...)", "info")
            self.lbl_solution_text.config(
                text="Chế độ POS: Nhập biểu thức dạng tích các tổng (Maxterms), ví dụ: (A+B)(A'+C), hoặc bấm 'Gợi ý' / 'Xem lời giải'.",
                fg=THEME["text_muted"]
            )
        else:
            self._set_feedback("[DẠNG SOP] Quan sát các nhóm ô 1 được khoanh màu và nhập biểu thức tổng các tích SOP.", "info")
            self.lbl_solution_text.config(
                text="Chế độ SOP: Nhập đáp án rồi nhấn 'Kiểm tra', hoặc bấm 'Gợi ý' để nhận trợ giúp.",
                fg=THEME["text_muted"]
            )
        
        # Cập nhật chú thích nhóm (Legend)
        for w in self.legend_frame.winfo_children():
            w.destroy()
            
        legend_title = "NHÓM Ô 0 (POS):" if self.current_mode == "POS" else "NHÓM Ô 1 (SOP):"
        tk.Label(
            self.legend_frame, text=legend_title,
            font=("Segoe UI", 8, "bold"), bg=THEME["bg_card"], fg=THEME["text_muted"]
        ).pack(side=tk.LEFT, padx=(0, 6))
        
        for idx, grp in enumerate(active_groups):
            gid = grp.get('id', idx + 1)
            color = grp.get('color', GROUP_PALETTE[idx % len(GROUP_PALETTE)])
            cell_count = len(grp.get('cells', []))
            term_info = f" -> {grp['term']}" if 'term' in grp else ""
            if cell_count > 1:
                tag_text = f"● G{gid} ({cell_count} ô{term_info})"
            else:
                c_part = grp['cells'][0].split(',')
                tag_text = f"● m{cell_to_minterm(int(c_part[0]), int(c_part[1]), num_vars)} (cô lập{term_info})"
            lbl = tk.Label(
                self.legend_frame,
                text=tag_text,
                font=("Consolas", 8, "bold"),
                fg=color,
                bg=THEME["bg_card"]
            )
            lbl.pack(side=tk.LEFT, padx=5)

    def _get_pos_data(self, p: Dict[str, Any], num_vars: int) -> Tuple[List[Dict[str, Any]], str]:
        """Lấy hoặc tự động tính danh sách nhóm ô 0 và biểu thức POS tối giản."""
        if 'pos_groups' in p and 'answer_pos' in p:
            return p['pos_groups'], p['answer_pos']
        grid = p.get('kmap_grid', [])
        zeros = set()
        dont_cares = set(p.get('dont_cares', []))
        for cell in grid:
            r, c = cell['row'], cell['col']
            v = str(cell.get('value', '0')).upper()
            m = cell_to_minterm(r, c, num_vars)
            if v == '0':
                zeros.add(m)
            elif v in ('X', 'D'):
                dont_cares.add(m)
        pos_groups, pos_ans = get_pos_groups(zeros, dont_cares, num_vars)
        p['pos_groups'] = pos_groups
        p['answer_pos'] = pos_ans
        return pos_groups, pos_ans

    def _get_pos_answer(self, p: Dict[str, Any], num_vars: int) -> str:
        """Lấy biểu thức POS tối giản chuẩn xác."""
        _, pos_ans = self._get_pos_data(p, num_vars)
        return pos_ans

    def _handle_submit(self, user_answer: str):
        """Xử lý kiểm tra khi người chơi gửi đáp án."""
        if not self.current_problem:
            return
            
        p = self.current_problem
        num_vars = p.get('num_vars', 3)
        
        # Nếu đang ở mode POS, đảm bảo bài toán có answer_pos
        if self.current_mode == "POS":
            self._get_pos_answer(p, num_vars)

        res = validate_answer(user_answer, p, num_vars, mode=self.current_mode)
        
        attempt_res = self.score_manager.record_attempt(
            problem_id=p.get('id', ''),
            is_correct=res['is_correct'],
            user_answer=user_answer,
            difficulty=p.get('difficulty', 1)
        )
        
        self._update_score_display()
        
        if res['is_correct']:
            pts = attempt_res.points_awarded
            msg = f"{res['message']} (+{pts} điểm)"
            self._set_feedback(msg, "success")
            self._display_explanation()
        elif res['is_equivalent']:
            self._set_feedback(res['message'], "warning")
        else:
            self._set_feedback(res['message'], "danger")

    def _display_explanation(self):
        """Hiển thị lời giải chi tiết của bài toán với chữ rõ ràng, dễ đọc."""
        if not self.current_problem:
            return
        p = self.current_problem
        num_vars = p.get('num_vars', 3)
        
        if self.current_mode == "POS":
            ans = self._get_pos_answer(p, num_vars)
            exp = p.get('answer_pos_explanation')
            if not exp:
                exp = f"Gom các ô mang giá trị 0 trên bìa {num_vars} biến (kết hợp các ô Don't Care X nếu có) để tạo các maxterm lớn nhất, rút gọn thành tích các tổng: F = {ans}"
            text = f"ĐÁP ÁN TỐI GIẢN (POS): F = {ans}\n\nCHI TIẾT RÚT GỌN:\n{exp}"
        else:
            ans = p.get('answer', '')
            exp = p.get('answer_explanation', '')
            text = f"ĐÁP ÁN TỐI GIẢN (SOP): F = {ans}\n\nCHI TIẾT RÚT GỌN:\n{exp}"
        
        self.lbl_solution_text.config(text=text, fg=THEME["text_primary"])

    def _reveal_solution(self):
        """Xem lời giải ngay."""
        if not self.current_problem:
            return
        self.solution_revealed = True
        self._display_explanation()
        num_vars = self.current_problem.get('num_vars', 3)
        if self.current_mode == "POS":
            ans = self._get_pos_answer(self.current_problem, num_vars)
            self.input_handler.set_value(ans)
            self._set_feedback(f"Đáp án tối giản POS: F = {ans}", "info")
        else:
            ans = self.current_problem.get('answer', '')
            self.input_handler.set_value(ans)
            self._set_feedback(f"Đáp án tối giản SOP: F = {ans}", "info")

    def _show_hint(self):
        """Gợi ý một phần của biểu thức logic."""
        if not self.current_problem:
            return
        num_vars = self.current_problem.get('num_vars', 3)
        if self.current_mode == "POS":
            pos_ans = self._get_pos_answer(self.current_problem, num_vars)
            import re
            factors = re.findall(r'\([^)]+\)|[A-Za-z]\'?', pos_ans)
            if factors:
                self._set_feedback(f"Gợi ý POS: Một trong các thừa số maxterm là: '{factors[0]}'.", "warning")
            else:
                self._set_feedback(f"Gợi ý POS: Hãy quan sát các ô giá trị 0.", "warning")
        else:
            groups = self.current_problem.get('groups', [])
            if groups:
                grp = groups[0]
                term = simplify_group(grp.get('cells', []), num_vars)
                hint_text = f"Gợi ý: Một trong các nhóm tạo thành tích logic: '{term}'."
                self._set_feedback(hint_text, "warning")
            else:
                self._set_feedback("Gợi ý: Hãy quan sát các ô giá trị 1 và xác định các biến không đổi.", "warning")

    def _set_feedback(self, message: str, kind: str = "info"):
        """Đặt nội dung và màu sắc Toast banner theo chuẩn độ tương phản dịu mắt."""
        colors = {
            "success": ("#132F26", "#4ADE80"),  # Xanh ngọc dịu
            "warning": ("#2E2310", "#FBBF24"),  # Hổ phách dịu
            "danger":  ("#381D24", "#FDA4AF"),  # Hồng cánh sen dịu
            "info":    (THEME["bg_inner"], THEME["text_body"]),  # Nền tối dịu, chữ sáng rõ
        }
        bg, fg = colors.get(kind, (THEME["bg_inner"], THEME["text_body"]))
        self.feedback_frame.config(bg=bg)
        self.lbl_feedback.config(text=message, bg=bg, fg=fg)

    def _update_score_display(self):
        """Cập nhật các giá trị HUD."""
        stats = self.score_manager.get_stats()
        self.lbl_score_val.config(text=f"{stats['score']:,}")
        self.lbl_streak_val.config(text=str(stats['streak']))
        self.lbl_solved_val.config(text=str(stats['total_solved']))
        self.lbl_accuracy_val.config(text=f"{stats['accuracy']}%")

    def _next_problem(self):
        if self.filtered_problems:
            self._load_problem_index(self.current_problem_idx + 1)

    def _prev_problem(self):
        if self.filtered_problems:
            self._load_problem_index(self.current_problem_idx - 1)

    def _random_problem(self):
        if self.filtered_problems:
            rand_idx = random.randint(0, len(self.filtered_problems) - 1)
            self._load_problem_index(rand_idx)


def start_game(config: Optional[Dict[str, Any]] = None, db: Optional[Dict[str, Any]] = None):
    """Điểm khởi động GUI cho game BiaK."""
    app = MainWindow(config=config, db=db)
    app.mainloop()


if __name__ == "__main__":
    start_game()
