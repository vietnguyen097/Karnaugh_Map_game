#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rounded Widgets & Design System - Thư viện widget bo góc và bảng màu dịu mắt
Hệ thống giao diện Modern Soft Charcoal & Slate:
- Tỷ lệ tương phản theo tiêu chuẩn WCAG AAA (chữ rõ ràng, không gây mỏi mắt)
- Thuật toán bo góc hình học chính xác (cạnh thẳng tuyệt đối, góc cung tròn mịn)
- Triệt tiêu hoàn toàn hiện tượng méo mó, lượn sóng (wobbly/jagged) do spline gây ra
"""

import math
import tkinter as tk
from typing import List, Tuple, Optional, Any

# Bảng màu thiết kế đồng nhất, tối ưu cho thị giác
THEME = {
    # Nền tổng thể và bề mặt
    "bg_root": "#0E131F",        # Nền tổng thể mềm mại (không dùng đen tuyền #000000)
    "bg_card": "#182030",        # Nền thẻ chính đồng nhất cho cả 2 bên Trái & Phải
    "border_card": "#28354D",    # Viền thẻ dịu mắt, chuyển tiếp mượt mà
    "bg_inner": "#121824",       # Bề mặt lùi sâu (K-map canvas, Formula bar, Solution)
    "border_inner": "#222D42",   # Viền bề mặt lùi sâu
    
    # Bậc màu chữ (độ tương phản chuẩn, đọc êm mắt)
    "text_primary": "#F1F5F9",   # Tiêu đề, số liệu chính (trắng kem, không chói lóa)
    "text_body": "#E2E8F0",      # Nội dung lời giải, gợi ý, phản hồi (rõ ràng, dễ đọc)
    "text_muted": "#94A3B8",     # Nhãn phụ, minterm, mô tả (độ tương phản 6.5:1)
    "text_dim": "#64748B",       # Chữ mờ tối thiểu (vẫn đủ phân biệt trên nền tối)
    
    # Màu điểm nhấn
    "accent_primary": "#4F46E5", # Nút chính / tab hoạt động
    "accent_cyan": "#38BDF8",    # Công thức F =, con trỏ
    "accent_green": "#22C55E",   # Nút tiếp theo, kết quả đúng
    "accent_amber": "#F59E0B",   # Don't Care X, nút gợi ý
    "accent_rose": "#F43F5E",    # Nút xóa, kết quả sai
    
    # Màu ô bìa Karnaugh (dịu mắt, độ tương phản vừa phải)
    "cell_0_bg": "#182030",
    "cell_0_border": "#28354D",
    "cell_0_fg": "#64748B",
    
    "cell_1_bg": "#182030",
    "cell_1_border": "#28354D",
    "cell_1_fg": "#4ADE80",
    
    "cell_x_bg": "#2E2310",
    "cell_x_border": "#A16207",
    "cell_x_fg": "#FBBF24",
    
    # Bảng màu nhóm khoanh (Pastel dịu nhẹ, không lóa)
    "palette": [
        "#38BDF8",  # Sky Blue
        "#4ADE80",  # Emerald Mint
        "#F472B6",  # Rose Pink
        "#A78BFA",  # Violet
        "#FBBF24",  # Amber
        "#2DD4BF",  # Teal
        "#FB923C",  # Orange
        "#818CF8",  # Indigo
    ]
}


def get_round_rect_points(x1: float, y1: float, x2: float, y2: float, radius: int = 8, steps: int = 8) -> List[float]:
    """
    Tính toán tập hợp các điểm của hình chữ nhật bo góc với 4 cạnh THẲNG TUYỆT ĐỐI.
    Góc bo được tạo bằng các cung tròn rời rạc chính xác theo hàm lượng giác.
    """
    r = min(radius, abs(x2 - x1) / 2, abs(y2 - y1) / 2)
    if r <= 1:
        return [x1, y1, x2, y1, x2, y2, x1, y2]
        
    points = []
    # 4 góc: tâm (cx, cy) và góc quét start_ang -> end_ang
    corners = [
        (x2 - r, y1 + r, -math.pi / 2, 0),             # Góc trên phải
        (x2 - r, y2 - r, 0, math.pi / 2),              # Góc dưới phải
        (x1 + r, y2 - r, math.pi / 2, math.pi),        # Góc dưới trái
        (x1 + r, y1 + r, math.pi, 3 * math.pi / 2)     # Góc trên trái
    ]
    
    for cx, cy, start_ang, end_ang in corners:
        for i in range(steps + 1):
            theta = start_ang + (end_ang - start_ang) * (i / steps)
            points.append(cx + r * math.cos(theta))
            points.append(cy + r * math.sin(theta))
            
    return points


def draw_rounded_rect(canvas: tk.Canvas, x1: float, y1: float, x2: float, y2: float, radius: int = 8, **kwargs) -> int:
    """
    Vẽ hình chữ nhật bo góc với các cạnh thẳng tuyệt đối và 4 góc bo tròn chuẩn xác.
    Sử dụng smooth=False để đảm bảo cạnh thẳng 100%, không bị cong vênh hay lượn sóng.
    """
    r = min(radius, abs(x2 - x1) / 2, abs(y2 - y1) / 2)
    if r <= 1:
        return canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
        
    pts = get_round_rect_points(x1, y1, x2, y2, radius=int(r), steps=8)
    return canvas.create_polygon(pts, smooth=False, **kwargs)


class RoundedCard(tk.Canvas):
    """
    Card bề mặt bo góc tự co giãn với 4 cạnh thẳng tuyệt đối và góc bo mịn.
    Bao bọc `self.content` (tk.Frame) để đặt các widget con vào bên trong.
    """
    
    def __init__(
        self,
        parent,
        bg_color: str = THEME["bg_root"],
        card_bg: str = THEME["bg_card"],
        border_color: str = THEME["border_card"],
        radius: int = 12,
        pad: int = 10,
        **kwargs
    ):
        super().__init__(parent, bg=bg_color, highlightthickness=0, bd=0, **kwargs)
        self.card_bg = card_bg
        self.border_color = border_color
        self.radius = radius
        self.pad = pad
        
        self.content = tk.Frame(self, bg=card_bg)
        self.window_id = self.create_window(pad, pad, window=self.content, anchor="nw")
        self.bind("<Configure>", self._on_resize)
        
    def _on_resize(self, event):
        w, h = event.width, event.height
        if w <= self.pad * 2 or h <= self.pad * 2:
            return
            
        self.delete("card_poly")
        poly = draw_rounded_rect(
            self,
            2, 2, w - 2, h - 2,
            radius=self.radius,
            fill=self.card_bg,
            outline=self.border_color,
            width=1.5
        )
        self.itemconfigure(poly, tags="card_poly")
        self.tag_lower("card_poly")
        
        # Cập nhật kích thước vùng nội dung bên trong
        content_w = max(w - 2 * self.pad, 10)
        content_h = max(h - 2 * self.pad, 10)
        self.itemconfigure(self.window_id, width=content_w, height=content_h)
