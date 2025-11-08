# auth_module.py
from dashboard import open_owner_dashboard  # không import app_nhatro!
import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import hashlib

def validate_password(pw):
    # (bạn có hàm validate_password trong app_nhatro.py; nếu muốn giữ, có thể chuyển vào đây)
    if len(pw) < 8:
        return "Mật khẩu phải có ít nhất 8 ký tự!"
    if not any(c.isupper() for c in pw):
        return "Mật khẩu phải chứa ít nhất 1 chữ in hoa!"
    if not any(c.islower() for c in pw):
        return "Mật khẩu phải chứa ít nhất 1 chữ thường!"
    if not any(c.isdigit() for c in pw):
        return "Mật khẩu phải chứa ít nhất 1 chữ số!"
    return None

# -----------------------
# ĐĂNG NHẬP CHỦ TRỌ
# -----------------------
def open_owner_login(parent):
    login_window = tk.Toplevel(parent)
    login_window.title("Đăng nhập - Chủ trọ")
    login_window.geometry("360x340")
    login_window.config(bg="#f9f9f9")

    tk.Label(login_window, text="Đăng nhập dành cho Chủ trọ", font=("Arial", 14, "bold"), bg="#f9f9f9").pack(pady=18)

    tk.Label(login_window, text="Tên đăng nhập:", bg="#f9f9f9").pack()
    username_entry = tk.Entry(login_window, width=30)
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Mật khẩu:", bg="#f9f9f9").pack()
    password_entry = tk.Entry(login_window, width=30, show="*")
    password_entry.pack(pady=5)

    show_password_var = tk.BooleanVar()
    tk.Checkbutton(login_window, text="Hiện mật khẩu", variable=show_password_var,
                   bg="#f9f9f9", command=lambda: password_entry.config(show="" if show_password_var.get() else "*")).pack()

    def login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        conn = sqlite3.connect("nhatro.db")
        c = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        c.execute("SELECT * FROM User WHERE Username=? AND Password=? AND VaiTro=1", (username, hashed_pw))
        user = c.fetchone()
        conn.close()
        if user:
            messagebox.showinfo("Đăng nhập thành công", f"Chào mừng, Chủ trọ {user[4]}!")
            login_window.destroy()
            open_owner_dashboard(parent, user[0], user[4])
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu sai!")

    def forgot_password():
        forgot_window = tk.Toplevel(login_window)
        forgot_window.title("Quên mật khẩu - Chủ trọ")
        forgot_window.geometry("360x250")
        forgot_window.config(bg="#f9f9f9")
        tk.Label(forgot_window, text="Nhập thông tin để đặt lại mật khẩu", font=("Arial", 12, "bold"), bg="#f9f9f9").pack(pady=12)
        tk.Label(forgot_window, text="Tên đăng nhập:", bg="#f9f9f9").pack()
        f_username = tk.Entry(forgot_window, width=30); f_username.pack(pady=5)
        tk.Label(forgot_window, text="Số điện thoại đã đăng ký:", bg="#f9f9f9").pack()
        f_phone = tk.Entry(forgot_window, width=30); f_phone.pack(pady=5)

        def verify_user():
            u = f_username.get().strip()
            phone = f_phone.get().strip()
            conn = sqlite3.connect("nhatro.db")
            c = conn.cursor()
            c.execute("SELECT * FROM User WHERE Username=? AND SDT=? AND VaiTro=1", (u, phone))
            user = c.fetchone()
            conn.close()
            if user:
                reset_window = tk.Toplevel(forgot_window)
                reset_window.title("Đặt lại mật khẩu")
                reset_window.geometry("320x220")
                reset_window.config(bg="#f9f9f9")
                tk.Label(reset_window, text="Mật khẩu mới:", bg="#f9f9f9").pack(pady=6)
                new_pw = tk.Entry(reset_window, width=30, show="*"); new_pw.pack(pady=4)
                tk.Label(reset_window, text="Xác nhận mật khẩu:", bg="#f9f9f9").pack(pady=6)
                confirm_pw = tk.Entry(reset_window, width=30, show="*"); confirm_pw.pack(pady=4)
                def reset_password():
                    if new_pw.get() != confirm_pw.get():
                        messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!"); return
                    pw_error = validate_password(new_pw.get())
                    if pw_error:
                        messagebox.showerror("Lỗi", pw_error); return
                    hashed_pw = hashlib.sha256(new_pw.get().encode()).hexdigest()
                    conn = sqlite3.connect("nhatro.db"); c = conn.cursor()
                    c.execute("UPDATE User SET Password=? WHERE Username=?", (hashed_pw, u))
                    conn.commit(); conn.close()
                    messagebox.showinfo("Thành công", "Mật khẩu đã được đặt lại!")
                    reset_window.destroy(); forgot_window.destroy()
                tk.Button(reset_window, text="Xác nhận", bg="#4CAF50", fg="white", width=16, command=reset_password).pack(pady=12)
            else:
                messagebox.showerror("Lỗi", "Tên đăng nhập hoặc số điện thoại không đúng!")

        tk.Button(forgot_window, text="Xác nhận", bg="#4CAF50", fg="white", width=16, command=verify_user).pack(pady=16)

    tk.Button(login_window, text="Đăng nhập", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", width=18, command=login).pack(pady=10)
    tk.Button(login_window, text="Chưa có tài khoản? Đăng ký ngay", font=("Arial", 10, "underline"),
              bg="#f9f9f9", fg="blue", bd=0, cursor="hand2",
              command=lambda: messagebox.showinfo("Đăng ký", "Mời đăng ký từ giao diện chính")).pack(pady=4)
    tk.Button(login_window, text="Quên mật khẩu?", font=("Arial", 10, "underline"),
              bg="#f9f9f9", fg="red", bd=0, cursor="hand2", command=forgot_password).pack(pady=4)

# -----------------------
# ĐĂNG NHẬP NGƯỜI THUÊ
# -----------------------
def open_tenant_page(parent):
    login_window = tk.Toplevel(parent)
    login_window.title("Đăng nhập - Người thuê")
    login_window.geometry("360x320")
    login_window.config(bg="#f9f9f9")

    tk.Label(login_window, text="Đăng nhập dành cho Người thuê", font=("Arial", 14, "bold"), bg="#f9f9f9").pack(pady=18)

    tk.Label(login_window, text="Tên đăng nhập:", bg="#f9f9f9").pack()
    username_entry = tk.Entry(login_window, width=30); username_entry.pack(pady=5)

    tk.Label(login_window, text="Mật khẩu:", bg="#f9f9f9").pack()
    password_entry = tk.Entry(login_window, width=30, show="*"); password_entry.pack(pady=5)

    # 🆕 Thêm checkbox "Hiện mật khẩu"
    show_password_var = tk.BooleanVar()
    tk.Checkbutton(
        login_window,
        text="Hiện mật khẩu",
        variable=show_password_var,
        bg="#f9f9f9",
        command=lambda: password_entry.config(show="" if show_password_var.get() else "*")
    ).pack()

    def login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        conn = sqlite3.connect("nhatro.db"); c = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        c.execute("SELECT * FROM User WHERE Username=? AND Password=? AND VaiTro=0", (username, hashed_pw))
        user = c.fetchone(); conn.close()
        if user:
            messagebox.showinfo("Đăng nhập thành công", f"Chào mừng, {user[4]}!")
            login_window.destroy()

            # Giao diện tạm thời cho người thuê
            tenant_window = tk.Toplevel(parent)
            tenant_window.title("Trang người thuê")
            tenant_window.geometry("420x300")
            tenant_window.config(bg="#f9f9f9")

            tk.Label(tenant_window, text=f"Xin chào, {user[4]}", font=("Arial", 14, "bold"), bg="#f9f9f9").pack(pady=20)
            tk.Label(tenant_window, text="Tính năng dành cho người thuê đang được phát triển...",
             font=("Arial", 11), bg="#f9f9f9", fg="gray").pack(pady=10)

            tk.Button(tenant_window, text="Đăng xuất", bg="red", fg="white", width=14,
              command=tenant_window.destroy).pack(pady=20)
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu sai!")

    def forgot_password():
        forgot_window = tk.Toplevel(login_window)
        forgot_window.title("Quên mật khẩu - Người thuê")
        forgot_window.geometry("360x250")
        forgot_window.config(bg="#f9f9f9")
        tk.Label(forgot_window, text="Nhập thông tin để đặt lại mật khẩu", font=("Arial", 12, "bold"), bg="#f9f9f9").pack(pady=12)
        tk.Label(forgot_window, text="Tên đăng nhập:", bg="#f9f9f9").pack()
        f_username = tk.Entry(forgot_window, width=30); f_username.pack(pady=5)
        tk.Label(forgot_window, text="Số điện thoại đã đăng ký:", bg="#f9f9f9").pack()
        f_phone = tk.Entry(forgot_window, width=30); f_phone.pack(pady=5)

        def verify_user():
            u = f_username.get().strip(); phone = f_phone.get().strip()
            conn = sqlite3.connect("nhatro.db"); c = conn.cursor()
            c.execute("SELECT * FROM User WHERE Username=? AND SDT=? AND VaiTro=0", (u, phone))
            user = c.fetchone(); conn.close()
            if user:
                reset_window = tk.Toplevel(forgot_window)
                reset_window.title("Đặt lại mật khẩu"); reset_window.geometry("320x220"); reset_window.config(bg="#f9f9f9")
                tk.Label(reset_window, text="Mật khẩu mới:", bg="#f9f9f9").pack(pady=6)
                new_pw = tk.Entry(reset_window, width=30, show="*"); new_pw.pack(pady=4)
                tk.Label(reset_window, text="Xác nhận mật khẩu:", bg="#f9f9f9").pack(pady=6)
                confirm_pw = tk.Entry(reset_window, width=30, show="*"); confirm_pw.pack(pady=4)
                def reset_password():
                    if new_pw.get() != confirm_pw.get():
                        messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!"); return
                    if len(new_pw.get()) < 6:
                        messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!"); return
                    hashed_pw = hashlib.sha256(new_pw.get().encode()).hexdigest()
                    conn = sqlite3.connect("nhatro.db"); c = conn.cursor()
                    c.execute("UPDATE User SET Password=? WHERE Username=?", (hashed_pw, u)); conn.commit(); conn.close()
                    messagebox.showinfo("Thành công", "Mật khẩu đã được đặt lại!"); reset_window.destroy(); forgot_window.destroy()
                tk.Button(reset_window, text="Xác nhận", bg="#4CAF50", fg="white", width=16, command=reset_password).pack(pady=12)
            else:
                messagebox.showerror("Lỗi", "Tên đăng nhập hoặc số điện thoại không đúng!")

        tk.Button(forgot_window, text="Xác nhận", bg="#4CAF50", fg="white", width=16, command=verify_user).pack(pady=16)

    tk.Button(login_window, text="Đăng nhập", font=("Arial", 11, "bold"), bg="#2196F3", fg="white", width=18, command=login).pack(pady=10)
    tk.Button(login_window, text="Chưa có tài khoản? Đăng ký ngay", font=("Arial", 10, "underline"),
              bg="#f9f9f9", fg="blue", bd=0, cursor="hand2", command=lambda: messagebox.showinfo("Đăng ký", "Mời đăng ký từ giao diện chính")).pack(pady=4)
    tk.Button(login_window, text="Quên mật khẩu?", font=("Arial", 10, "underline"),
              bg="#f9f9f9", fg="red", bd=0, cursor="hand2", command=forgot_password).pack(pady=4)
