#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BiaK - Game Đoán Hàm Số Bằng Bìa Karnaugh
File khởi động chính cho game
"""

import json
import sys
from pathlib import Path

# Cấu hình đường dẫn hỗ trợ cả chạy script và chạy file đóng gói PyInstaller .exe
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = Path(sys._MEIPASS).resolve()
else:
    PROJECT_ROOT = Path(__file__).parent.resolve()

CONFIG_FILE = PROJECT_ROOT / "config" / "game_config.json"


def load_config():
    """Load game configuration from JSON file."""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_welcome(config):
    """Print welcome message to console."""
    print("=" * 60)
    print(" 🎮 BIAK - GAME ĐOÁN HÀM SỐ BẰNG BÌA KARNAUGH 🎮 ")
    print("=" * 60)
    print()
    print(f"Phiên bản: {config.get('version', '1.0.0')}")
    print(f"Mô tả: {config.get('description', '')}")
    print()
    
    levels = config.get('grade_levels', {})
    print("💫 CÁC CẤP ĐỘ:")
    for level_key in ['basic', 'advanced']:
        if level_key in levels:
            l = levels[level_key]
            print(f"  • Cấp độ {l['name']}: {l['variables']} biến")
    
    print()
    print("📖 MÔ TẢ GAME:")
    print("  - Xem bìa Karnaugh với các nhóm đã xác định")
    print("  - Phân tích và đoán hàm logic đơn giản hóa")
    print("  - Hệ thống điểm số và cấp độ")
    print()
    print("=" * 60)
    print()


def load_database():
    """Tải database bài toán từ file JSON."""
    from game_data import load_all_problems
    return load_all_problems()


def run_cli_mode(config, db):
    """Chế độ chơi console đơn giản dành cho terminal / test."""
    from game_engine.kmap_parser import parse_grid_to_matrix, format_kmap_text
    from game_engine.validator import validate_answer
    from game_engine.scoring import ScoreManager
    
    print("🕹️ CHẾ ĐỘ CHƠI CONSOLE (CLI MODE)")
    print("Nhập 'q' hoặc 'exit' để thoát.\n")
    
    score_mgr = ScoreManager()
    all_probs = db['basic'] + db['advanced']
    
    for idx, prob in enumerate(all_probs):
        score_mgr.reset_problem_attempts()
        nvars = prob.get('num_vars', 3)
        grid = prob.get('kmap_grid', [])
        matrix = parse_grid_to_matrix(grid, nvars)
        
        print(f"\n--- [Bài {idx+1}/{len(all_probs)}: {prob['id']}] {prob['title']} ({nvars} biến) ---")
        print(format_kmap_text(matrix, nvars))
        print("Các nhóm đã khoanh:")
        for g in prob.get('groups', []):
            print(f"  • Nhóm {g['id']}: {g['cells']}")
            
        while True:
            try:
                ans = input("\n👉 Nhập hàm tối giản F = ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nTạm biệt!")
                return
                
            if ans.lower() in ('q', 'exit', 'quit'):
                print(f"\nKết thúc lượt chơi! Tổng điểm: {score_mgr.score}")
                return
            if not ans:
                continue
                
            res = validate_answer(ans, prob, nvars)
            attempt = score_mgr.record_attempt(
                problem_id=prob['id'],
                is_correct=res['is_correct'],
                user_answer=ans,
                difficulty=prob.get('difficulty', 1)
            )
            
            if res['is_correct']:
                print(f"🎉 Chính xác! (+{attempt.points_awarded} điểm)")
                print(f"📖 Lời giải: {prob.get('answer_explanation', '')}")
                break
            else:
                print(f"❌ {res['message']}")
                try_again = input("Bạn có muốn thử lại không? (y/n, enter=y): ").strip().lower()
                if try_again in ('n', 'no'):
                    print(f"Đáp án đúng là: F = {prob.get('answer')}")
                    print(f"Giải thích: {prob.get('answer_explanation', '')}")
                    break


def main():
    """Main entry point for the game."""
    try:
        config = load_config()
        print_welcome(config)
        
        # Load database
        db = load_database()
        print(f"📊 Database đã tải:")
        print(f"   - Bài toán cơ bản: {len(db['basic'])} bài")
        print(f"   - Bài toán nâng cao: {len(db['advanced'])} bài")
        print(f"   - Tổng: {len(db['basic']) + len(db['advanced'])} bài")
        print()
        
        # Kiểm tra tham số CLI
        if "--cli" in sys.argv:
            run_cli_mode(config, db)
        else:
            print("🚀 Game đang khởi động...")
            print("   (Chuyển sang GUI mode - vui lòng xem giao diện)")
            from gui.main_window import start_game
            start_game(config, db)
        
    except FileNotFoundError as e:
        print(f"❌ Lỗi: Không tìm thấy file cấu hình {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi: File cấu hình không hợp lệ - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
