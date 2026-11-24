#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Input Handler - Bàn phím ảo logic & thanh nhập công thức hiện đại
Thiết kế Modern Soft Charcoal & Slate bo góc:
- Thanh công thức mô phỏng IDE với nền lùi sâu, con trỏ Cyan
- Các phím macro bo góc nhẹ với độ tương phản hài hòa, êm mắt
"""

import tkinter as tk
from typing import Callable, Optional, Dict
from .rounded_widgets import THEME, draw_rounded_rect


class InputHandler(tk.Frame):
    """Bàn phím logic và thanh nhập liệu phong cách studio kỹ thuật số dịu mắt."""
    
    def __init__(self, parent, on_submit_callback: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(parent, bg=THEME["bg_card"], **kwargs)
        self.on_submit = on_submit_callback
        
        self._init_ui()
        
    def _init_ui(self):
        # 1. Thanh công thức (Formula Bar)
        bar_container = tk.Frame(self, bg=THEME["bg_card"])
        bar_container.pack(fill=tk.X, padx=8, pady=(4, 8))
        
        entry_wrapper = tk.Frame(
            bar_container,
            bg=THEME["bg_inner"],
            bd=1,
            relief=tk.SOLID,
            highlightbackground=THEME["border_inner"],
            highlightcolor=THEME["accent_primary"],
            highlightthickness=1.5
        )
        entry_wrapper.pack(fill=tk.X)
        
        # Huy hiệu tiền tố "F ="
        prefix_lbl = tk.Label(
            entry_wrapper,
            text=" F = ",
            font=("Consolas", 13, "bold"),
            bg="#1E2838",
            fg=THEME["accent_cyan"],
            padx=8,
            pady=6
        )
        prefix_lbl.pack(side=tk.LEFT)
        
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            entry_wrapper,
            textvariable=self.entry_var,
            font=("Consolas", 15, "bold"),
            bg=THEME["bg_inner"],
            fg=THEME["text_primary"],
            insertbackground=THEME["accent_cyan"],
            relief=tk.FLAT,
            bd=0
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.entry.focus_set()
        
        # Bắt phím Enter để nộp bài
        self.entry.bind("<Return>", lambda e: self._submit())
        
        # Nút xóa nhanh góc phải ô nhập
        btn_quick_clear = tk.Label(
            entry_wrapper,
            text=" ✕ ",
            font=("Segoe UI", 11, "bold"),
            bg=THEME["bg_inner"],
            fg=THEME["text_muted"],
            cursor="hand2"
        )
        btn_quick_clear.pack(side=tk.RIGHT, padx=6)
        btn_quick_clear.bind("<Button-1>", lambda e: self.clear())
        btn_quick_clear.bind("<Enter>", lambda e: btn_quick_clear.config(fg=THEME["accent_rose"]))
        btn_quick_clear.bind("<Leave>", lambda e: btn_quick_clear.config(fg=THEME["text_muted"]))

        # 2. Bàn phím Macro logic (Keypad)
        keypad_frame = tk.Frame(self, bg=THEME["bg_card"])
        keypad_frame.pack(fill=tk.X, padx=8, pady=(2, 4))
        
        # Hàng 1: Cụm biến logic A, B, C, D, E
        var_row = tk.Frame(keypad_frame, bg=THEME["bg_card"])
        var_row.pack(fill=tk.X, pady=2)
        
        self.var_buttons: Dict[str, tk.Button] = {}
        for var in ['A', 'B', 'C', 'D', 'E']:
            btn = tk.Button(
                var_row,
                text=var,
                font=("Consolas", 12, "bold"),
                bg="#243044",
                fg=THEME["text_primary"],
                activebackground="#33425E",
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                command=lambda v=var: self.insert_text(v)
            )
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X, ipady=4)
            self.var_buttons[var] = btn
            
        # Hàng 2: Toán tử logic & Hằng số
        ops_row = tk.Frame(keypad_frame, bg=THEME["bg_card"])
        ops_row.pack(fill=tk.X, pady=2)
        
        ops = [
            (" ' (NOT)", "'", "#2E2310", THEME["accent_amber"]),   # Hổ phách dịu
            (" + (OR)", " + ", "#1A2A44", "#93C5FD"),              # Xanh lam dịu
            (" 1 ", "1", "#132F26", THEME["accent_green"]),        # Xanh ngọc
            (" 0 ", "0", "#243044", THEME["text_body"]),           # Xám chì rõ nét
            (" ( ", "(", "#243044", THEME["text_body"]),
            (" ) ", ")", "#243044", THEME["text_body"]),
        ]
        for label, val, bg_col, fg_col in ops:
            btn = tk.Button(
                ops_row,
                text=label,
                font=("Consolas", 10, "bold"),
                bg=bg_col,
                fg=fg_col,
                activebackground="#33425E",
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                command=lambda v=val: self.insert_text(v)
            )
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X, ipady=4)
            
        # Hàng 3: Xóa & Kiểm tra
        act_row = tk.Frame(keypad_frame, bg=THEME["bg_card"])
        act_row.pack(fill=tk.X, pady=2)
        
        btn_back = tk.Button(
            act_row,
            text="⌫ Xóa ký tự",
            font=("Segoe UI", 9, "bold"),
            bg="#381D24",
            fg="#FDA4AF",
            activebackground="#4E232E",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.backspace
        )
        btn_back.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X, ipady=5)
        
        btn_clear_all = tk.Button(
            act_row,
            text="✕ Xóa hết",
            font=("Segoe UI", 9),
            bg="#243044",
            fg=THEME["text_body"],
            activebackground="#33425E",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.clear
        )
        btn_clear_all.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X, ipady=5)
        
        btn_check = tk.Button(
            act_row,
            text="Kiểm tra  ↵",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["accent_primary"],
            fg="#FFFFFF",
            activebackground="#4338CA",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self._submit
        )
        btn_check.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X, ipady=5)
        
    def set_available_variables(self, num_vars: int):
        """Kích hoạt chỉ các biến có trong bài toán hiện tại."""
        vars_available = ['A', 'B', 'C', 'D', 'E'][:num_vars]
        for var, btn in self.var_buttons.items():
            if var in vars_available:
                btn.config(state=tk.NORMAL, bg="#243044", fg=THEME["text_primary"], cursor="hand2")
            else:
                btn.config(state=tk.DISABLED, bg="#161C26", fg="#475569", cursor="arrow")
                
    def insert_text(self, text: str):
        """Chèn ký tự vào vị trí con trỏ."""
        self.entry.insert(tk.INSERT, text)
        self.entry.focus_set()
        
    def backspace(self):
        """Xóa 1 ký tự trước con trỏ."""
        pos = self.entry.index(tk.INSERT)
        if pos > 0:
            self.entry.delete(pos - 1, pos)
        self.entry.focus_set()
        
    def clear(self):
        """Xóa trắng nội dung."""
        self.entry_var.set("")
        self.entry.focus_set()
        
    def get_value(self) -> str:
        return self.entry_var.get().strip()
        
    def set_value(self, val: str):
        self.entry_var.set(val)
        self.entry.focus_set()
        
    def _submit(self):
        if self.on_submit:
            self.on_submit(self.get_value())
