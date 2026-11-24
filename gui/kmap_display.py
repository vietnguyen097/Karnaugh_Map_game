#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KMap Display - Widget Canvas hiển thị bìa Karnaugh hiện đại
Thiết kế chuẩn kỹ thuật số:
- Lưới ô thẳng tắp 100%, sắc nét tuyệt đối, không bị méo mó hay nhiễu
- Mã Gray và nhãn biến căn chỉnh chuẩn xác theo tọa độ toán học
- Đường bao nhóm (Loops) dạng capsule bo tròn viền mượt với cạnh thẳng tuyệt đối
"""

import tkinter as tk
from typing import Dict, List, Any, Optional, Tuple

from game_engine.kmap_parser import (
    get_kmap_dimensions,
    parse_grid_to_matrix,
    cell_to_minterm,
    simplify_group,
)
from .rounded_widgets import THEME, draw_rounded_rect

GROUP_PALETTE = THEME["palette"]


class KMapDisplay(tk.Frame):
    """Widget Canvas hiển thị bìa Karnaugh với lưới ô thẳng sắc nét và vòng nhóm bo tròn mượt mà."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=THEME["bg_card"], **kwargs)
        
        self.problem: Optional[Dict[str, Any]] = None
        self.num_vars: int = 3
        self.matrix: List[List[Any]] = []
        self.groups: List[Dict[str, Any]] = []
        self.mode: str = "SOP"
        
        # Cấu hình kích thước ô chuẩn
        self.cell_w = 72
        self.cell_h = 62
        self.header_w = 76
        self.header_h = 44
        self.margin_x = 24
        self.margin_y = 18
        
        self.hover_cell: Optional[Tuple[int, int]] = None
        
        # Canvas chính trên nền lùi sâu dịu mắt
        self.canvas = tk.Canvas(
            self,
            bg=THEME["bg_inner"],
            highlightthickness=1,
            highlightbackground=THEME["border_inner"],
            cursor="crosshair"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)
        
    def load_problem(self, problem: Dict[str, Any], custom_groups: Optional[List[Dict[str, Any]]] = None, mode: str = "SOP"):
        """Tải dữ liệu bài toán mới và dựng lại giao diện bìa. Hỗ trợ truyền custom_groups và mode (SOP/POS)."""
        self.problem = problem
        self.num_vars = problem.get('num_vars', 3)
        self.matrix = parse_grid_to_matrix(problem.get('kmap_grid', []), self.num_vars)
        self.groups = custom_groups if custom_groups is not None else problem.get('groups', [])
        self.mode = mode
        self.hover_cell = None
        self.redraw()
        
    def redraw(self):
        """Vẽ lại toàn bộ bìa Karnaugh với lưới thẳng tắp, sắc nét 100%."""
        self.canvas.delete("all")
        if not self.problem:
            return
            
        dims = get_kmap_dimensions(self.num_vars)
        num_rows = dims['num_rows']
        num_cols = dims['num_cols']
        row_labels = dims['row_labels']
        col_labels = dims['col_labels']
        row_vars = dims['row_vars']
        col_vars = dims['col_vars']
        
        # Điều chỉnh kích thước ô theo số cột
        if num_cols > 4:
            self.cell_w = 60
            self.cell_h = 52
        elif num_cols == 2:
            self.cell_w = 95
            self.cell_h = 76
        else:
            self.cell_w = 76
            self.cell_h = 62
            
        total_w = self.margin_x * 2 + self.header_w + num_cols * self.cell_w
        total_h = self.margin_y * 2 + self.header_h + num_rows * self.cell_h + 16
        
        self.canvas.config(scrollregion=(0, 0, total_w, total_h))
        self.canvas.config(width=min(total_w, 760), height=total_h)
        
        start_x = self.margin_x
        start_y = self.margin_y
        
        # 1. Ô góc phân tách biến (RowVars \ ColVars) thẳng nét
        corner_x1 = start_x
        corner_y1 = start_y
        corner_x2 = corner_x1 + self.header_w
        corner_y2 = corner_y1 + self.header_h
        
        self.canvas.create_rectangle(
            corner_x1, corner_y1, corner_x2, corner_y2,
            fill="#1E2838", outline="#2F3E55", width=1.2
        )
        self.canvas.create_line(
            corner_x1, corner_y1, corner_x2, corner_y2,
            fill="#3B4B63", width=1.2
        )
        # Biến cột
        self.canvas.create_text(
            corner_x2 - 10, corner_y1 + 13,
            text=col_vars, font=("Consolas", 10, "bold"), fill=THEME["accent_cyan"], anchor="e"
        )
        # Biến hàng
        self.canvas.create_text(
            corner_x1 + 10, corner_y2 - 13,
            text=row_vars, font=("Consolas", 10, "bold"), fill="#A78BFA", anchor="w"
        )
        
        # 2. Header cột (Mã Gray dạng Keycap thẳng nét, liền kề chuẩn xác)
        for c in range(num_cols):
            x1 = corner_x2 + c * self.cell_w
            x2 = x1 + self.cell_w
            self.canvas.create_rectangle(
                x1, corner_y1, x2, corner_y2,
                fill="#1E2838", outline="#2F3E55", width=1.2
            )
            self.canvas.create_text(
                (x1 + x2) / 2, (corner_y1 + corner_y2) / 2,
                text=col_labels[c], font=("Consolas", 12, "bold"), fill=THEME["text_primary"]
            )
            
        # 3. Header hàng (Mã Gray dạng Keycap thẳng nét)
        for r in range(num_rows):
            y1 = corner_y2 + r * self.cell_h
            y2 = y1 + self.cell_h
            self.canvas.create_rectangle(
                corner_x1, y1, corner_x2, y2,
                fill="#1E2838", outline="#2F3E55", width=1.2
            )
            self.canvas.create_text(
                (corner_x1 + corner_x2) / 2, (y1 + y2) / 2,
                text=row_labels[r], font=("Consolas", 12, "bold"), fill=THEME["text_primary"]
            )
            
        # 4. Tập hợp màu các nhóm
        cell_colors = {}
        for idx, grp in enumerate(self.groups):
            color = grp.get('color', GROUP_PALETTE[idx % len(GROUP_PALETTE)])
            for cell_str in grp.get('cells', []):
                parts = cell_str.split(',')
                r, c = int(parts[0]), int(parts[1])
                if (r, c) not in cell_colors:
                    cell_colors[(r, c)] = []
                cell_colors[(r, c)].append(color)

        # 5. Vẽ từng ô trong lưới thẳng tắp, tiếp giáp chuẩn xác
        for r in range(num_rows):
            for c in range(num_cols):
                x1 = corner_x2 + c * self.cell_w
                y1 = corner_y2 + r * self.cell_h
                x2 = x1 + self.cell_w
                y2 = y1 + self.cell_h
                
                raw_val = self.matrix[r][c] if r < len(self.matrix) and c < len(self.matrix[r]) else 0
                is_x = str(raw_val).upper() in ('X', 'D')
                is_one = (raw_val == 1 or raw_val == '1')
                is_hover = (self.hover_cell == (r, c))
                
                # Màu sắc ô dịu mắt, tương phản chuẩn theo chế độ SOP / POS
                if is_x:
                    bg_color = THEME["cell_x_bg"]
                    border_color = THEME["cell_x_border"]
                    val_text = "X"
                    val_color = THEME["cell_x_fg"]
                    minterm_color = "#FCD34D"
                elif is_one:
                    bg_color = THEME["cell_1_bg"]
                    border_color = THEME["cell_1_border"]
                    val_text = "1"
                    if self.mode == "POS":
                        val_color = THEME["cell_0_fg"]      # Ở POS, số 1 là màu xám chì bình thường
                        minterm_color = THEME["text_muted"]
                    else:
                        val_color = THEME["cell_1_fg"]      # Ở SOP, số 1 là màu xanh lá nổi bật
                        minterm_color = "#86EFAC"
                else:
                    bg_color = THEME["cell_0_bg"]
                    border_color = THEME["cell_0_border"]
                    val_text = "0"
                    if self.mode == "POS":
                        val_color = THEME["cell_1_fg"]      # Ở POS, số 0 là màu xanh lá nổi bật
                        minterm_color = "#86EFAC"
                    else:
                        val_color = THEME["cell_0_fg"]      # Ở SOP, số 0 là màu xám chì bình thường
                        minterm_color = THEME["text_muted"]
                    
                # Vẽ ô lưới thẳng tắp, hoàn toàn không bị méo lệch
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=bg_color,
                    outline=border_color,
                    width=1.2,
                    tags=(f"cell_{r}_{c}", "kmap_cell")
                )
                
                # Viền hover nổi bật khi rê chuột
                if is_hover:
                    self.canvas.create_rectangle(
                        x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                        outline=THEME["accent_cyan"],
                        width=2
                    )
                
                # Minterm góc trên bên phải (rõ nét, không mờ tịt)
                minterm = cell_to_minterm(r, c, self.num_vars)
                self.canvas.create_text(
                    x2 - 6, y1 + 6,
                    text=f"m{minterm}",
                    font=("Consolas", 8, "bold" if is_one or is_x else "normal"),
                    fill=minterm_color,
                    anchor="ne"
                )
                
                # Giá trị số ở tâm ô
                self.canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2 + 1,
                    text=val_text,
                    font=("Consolas", 16, "bold"),
                    fill=val_color
                )
                
        # 6. Vẽ đường bao nhóm (Loops) phong cách capsule bo tròn với cạnh thẳng tuyệt đối
        self._draw_group_loops(corner_x2, corner_y2, num_rows, num_cols)
        
    def _draw_group_loops(self, origin_x: int, origin_y: int, num_rows: int, num_cols: int):
        """Vẽ viền bo tròn capsule chuẩn cho các nhóm ô, cạnh thẳng tắp, góc bo cong tròn mượt mà."""
        offset = 4
        
        for grp_idx, grp in enumerate(self.groups):
            color = grp.get('color', GROUP_PALETTE[grp_idx % len(GROUP_PALETTE)])
            cells = grp.get('cells', [])
            if not cells:
                continue
                
            coords = [tuple(map(int, c.split(','))) for c in cells]
            rows = [r for r, c in coords]
            cols = [c for r, c in coords]
            
            min_r, max_r = min(rows), max(rows)
            min_c, max_c = min(cols), max(cols)
            
            is_col_wrap = (0 in cols and (num_cols - 1) in cols and len(set(cols)) < num_cols)
            is_row_wrap = (0 in rows and (num_rows - 1) in rows and len(set(rows)) < num_rows)
            
            pad = offset + (grp_idx % 3) * 2
            
            if not is_col_wrap and not is_row_wrap:
                # Nhóm liền mạch: vẽ khung capsule bo tròn chuẩn xác
                x1 = origin_x + min_c * self.cell_w + pad
                y1 = origin_y + min_r * self.cell_h + pad
                x2 = origin_x + (max_c + 1) * self.cell_w - pad
                y2 = origin_y + (max_r + 1) * self.cell_h - pad
                
                draw_rounded_rect(
                    self.canvas,
                    x1, y1, x2, y2,
                    radius=10,
                    outline=color,
                    width=2.5,
                    fill="",
                    tags="group_loop"
                )
            else:
                # Nhóm bao biên: vẽ các đoạn viền bo tròn từng phần
                for r, c in coords:
                    x1 = origin_x + c * self.cell_w + pad
                    y1 = origin_y + r * self.cell_h + pad
                    x2 = origin_x + (c + 1) * self.cell_w - pad
                    y2 = origin_y + (r + 1) * self.cell_h - pad
                    draw_rounded_rect(
                        self.canvas,
                        x1, y1, x2, y2,
                        radius=8,
                        outline=color,
                        width=2.5,
                        fill="",
                        tags="group_loop"
                    )

    def _on_mouse_move(self, event):
        """Xử lý hover qua các ô."""
        if not self.problem:
            return
        dims = get_kmap_dimensions(self.num_vars)
        corner_x2 = self.margin_x + self.header_w
        corner_y2 = self.margin_y + self.header_h
        
        if event.x >= corner_x2 and event.y >= corner_y2:
            c = (event.x - corner_x2) // self.cell_w
            r = (event.y - corner_y2) // self.cell_h
            if 0 <= r < dims['num_rows'] and 0 <= c < dims['num_cols']:
                if self.hover_cell != (r, c):
                    self.hover_cell = (r, c)
                    self.redraw()
                return
                
        if self.hover_cell is not None:
            self.hover_cell = None
            self.redraw()
            
    def _on_mouse_leave(self, event):
        if self.hover_cell is not None:
            self.hover_cell = None
            self.redraw()
