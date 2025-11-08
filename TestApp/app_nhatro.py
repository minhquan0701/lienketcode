import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
import re
from datetime import datetime
import hashlib
from auth_module import open_owner_login, open_tenant_page  # đăng nhập

# -----------------------
# HÀM KIỂM TRA MẬT KHẨU MẠNH
# -----------------------
def validate_password(pw):
    if len(pw) < 8:
        return "Mật khẩu phải có ít nhất 8 ký tự!"
    if not re.search(r"[A-Z]", pw):
        return "Mật khẩu phải chứa ít nhất 1 chữ in hoa!"
    if not re.search(r"[a-z]", pw):
        return "Mật khẩu phải chứa ít nhất 1 chữ thường!"
    if not re.search(r"[0-9]", pw):
        return "Mật khẩu phải chứa ít nhất 1 chữ số!"
    return None  # hợp lệ

# -----------------------
# DATABASE INIT
# -----------------------
def init_db():
    conn = sqlite3.connect("nhatro.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS User (
            User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT UNIQUE,
            Password TEXT,
            VaiTro INTEGER,
            HoTen TEXT,
            NgaySinh TEXT,
            Email TEXT,
            SDT TEXT,
            CCCD TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------
# HÀM ĐĂNG KÝ CHUNG
# -----------------------
def register_user(parent, vaitro, title):
    reg_window = tk.Toplevel(parent)
    reg_window.title(title)
    reg_window.geometry("420x560")
    reg_window.config(bg="#f9f9f9")

    tk.Label(reg_window, text=title, font=("Arial", 14, "bold"), bg="#f9f9f9").pack(pady=12)

    fields = {}
    labels = [
        ("Họ và tên:", "HoTen"),
        ("Ngày sinh (dd/mm/yyyy):", "NgaySinh"),
        ("Email (Gmail):", "Email"),
        ("Số điện thoại:", "SDT"),
        ("CCCD/CMND:", "CCCD"),
        ("Tên đăng nhập:", "Username"),
        ("Mật khẩu:", "Password"),
        ("Nhập lại mật khẩu:", "Confirm")
    ]

    for label, key in labels:
        tk.Label(reg_window, text=label, bg="#f9f9f9").pack(anchor='w', padx=20)
        entry = tk.Entry(reg_window, width=40, show="*" if "Mật khẩu" in label else "")
        entry.pack(pady=4, padx=20)
        fields[key] = entry

    def do_register():
        data = {k: v.get().strip() for k, v in fields.items()}

        # 1. Kiểm tra bắt buộc
        if not all([data["HoTen"], data["Username"], data["Password"], data["Confirm"], data["SDT"], data["Email"]]):
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ các trường bắt buộc.")
            return

        # 2. Mật khẩu khớp
        if data["Password"] != data["Confirm"]:
            messagebox.showerror("Lỗi", "Mật khẩu nhập lại không khớp.")
            return

        # 3. Họ tên
        if not re.match(r"^[A-Za-zÀ-ỹ\s]+$", data["HoTen"]):
            messagebox.showerror("Lỗi", "Họ tên chỉ được chứa chữ cái và khoảng trắng.")
            return

        # 4. Ngày sinh
        parsed = None
        if data["NgaySinh"]:
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    parsed = datetime.strptime(data["NgaySinh"], fmt)
                    break
                except Exception:
                    continue
            if parsed is None:
                parts = data["NgaySinh"].replace("-", "/").split("/")
                if len(parts) == 3 and all(part.isdigit() for part in parts):
                    d, m, y = parts
                    d = d.zfill(2)
                    m = m.zfill(2)
                    try:
                        parsed = datetime.strptime(f"{d}/{m}/{y}", "%d/%m/%Y")
                    except Exception:
                        parsed = None
            if parsed is None:
                messagebox.showerror("Lỗi", "Ngày sinh không hợp lệ! Định dạng dd/mm/yyyy.")
                return

        # 5. Email Gmail
        if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", data["Email"]):
            messagebox.showerror("Lỗi", "Email không hợp lệ! Vui lòng nhập Gmail.")
            return

        # 6. SĐT
        if not re.match(r"^(0[0-9]{9})$", data["SDT"]):
            messagebox.showerror("Lỗi", "Số điện thoại không hợp lệ! Phải gồm 10 chữ số và bắt đầu bằng 0.")
            return

        # 7. CCCD
        if data["CCCD"]:
            if not re.match(r"^\d{9}$", data["CCCD"]) and not re.match(r"^\d{12}$", data["CCCD"]):
                messagebox.showerror("Lỗi", "CCCD/CMND phải gồm 9 hoặc 12 chữ số.")
                return

        # 8. Username
        if len(data["Username"]) < 4 or " " in data["Username"]:
            messagebox.showerror("Lỗi", "Tên đăng nhập phải có ít nhất 4 ký tự và không chứa khoảng trắng.")
            return

        # 9. Mật khẩu mạnh
        pw_error = validate_password(data["Password"])
        if pw_error:
            messagebox.showerror("Lỗi", pw_error)
            return

        # 10. Lưu vào DB (mã hóa mật khẩu)
        conn = sqlite3.connect("nhatro.db")
        c = conn.cursor()
        try:
            hashed_pw = hashlib.sha256(data["Password"].encode()).hexdigest()
            c.execute("""
                INSERT INTO User (Username, Password, VaiTro, HoTen, NgaySinh, Email, SDT, CCCD)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (data["Username"], hashed_pw, vaitro, data["HoTen"], data["NgaySinh"], data["Email"], data["SDT"], data["CCCD"]))
            conn.commit()
            role_text = "Chủ trọ" if vaitro == 1 else "Người thuê"
            messagebox.showinfo("Thành công", f"Đăng ký {role_text} thành công!")
            reg_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại.")
        finally:
            conn.close()

    tk.Button(reg_window, text="Đăng ký", bg="#4CAF50", fg="white",
              font=("Arial", 11, "bold"), width=18, command=do_register).pack(pady=16)

# -----------------------
# GIAO DIỆN CHÍNH
# -----------------------
def main():
    root = tk.Tk()
    root.title("Ứng dụng Quản lý Nhà trọ")
    root.geometry("440x360")
    root.config(bg="#f2f2f2")

    tk.Label(root, text="Chào mừng đến với Ứng dụng Quản lý Nhà trọ",
             font=("Arial", 14, "bold"), bg="#f2f2f2", wraplength=380, justify="center").pack(pady=28)

    tk.Button(root, text="👑 Chủ trọ", font=("Arial", 12, "bold"),
              bg="#4CAF50", fg="white", width=18, height=2,
              command=lambda: open_owner_login(root)).pack(pady=8)

    tk.Button(root, text="🏠 Người thuê", font=("Arial", 12, "bold"),
              bg="#2196F3", fg="white", width=18, height=2,
              command=lambda: open_tenant_page(root)).pack(pady=6)

    tk.Label(root, text="© 2025 - Ứng dụng Quản lý Nhà trọ", font=("Arial", 9), bg="#f2f2f2", fg="gray").pack(side="bottom", pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
