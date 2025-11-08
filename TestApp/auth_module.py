# auth_module.py
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
import hashlib
from datetime import datetime
import re

DB_PATH = "nhatro.db"

# -----------------------
# TẠO BẢNG CẦN THIẾT
# -----------------------
def _ensure_tenant_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS TenantInfo (
            tenant_username TEXT PRIMARY KEY,
            full_name TEXT,
            gender TEXT,
            birth_date TEXT,
            phone TEXT,
            email TEXT,
            job TEXT,
            cccd TEXT,
            note TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS RentalRequests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_username TEXT,
            owner_username TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

_ensure_tenant_tables()

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
        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM User WHERE Username=? AND Password=? AND VaiTro=1", (username, hashed_pw))
        user = c.fetchone()
        conn.close()
        if user:
            messagebox.showinfo("Đăng nhập thành công", f"Chào mừng, Chủ trọ {user[4]}!")
            login_window.destroy()
            from dashboard import open_owner_dashboard
            open_owner_dashboard(parent, user[0], user[4])
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu sai!")

    tk.Button(login_window, text="Đăng nhập", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
              width=18, command=login).pack(pady=12)

# -----------------------
# ĐĂNG NHẬP NGƯỜI THUÊ
# -----------------------
def open_tenant_page(parent):
    login_window = tk.Toplevel(parent)
    login_window.title("Đăng nhập - Người thuê")
    login_window.geometry("360x340")
    login_window.config(bg="#f9f9f9")

    tk.Label(login_window, text="Đăng nhập dành cho Người thuê", font=("Arial", 14, "bold"), bg="#f9f9f9").pack(pady=18)

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
        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM User WHERE Username=? AND Password=? AND VaiTro=2", (username, hashed_pw))
        user = c.fetchone()
        conn.close()
        if user:
            messagebox.showinfo("Đăng nhập thành công", f"Chào mừng, {user[4]}!")
            login_window.destroy()
            _open_tenant_info_window(parent, username, user[4])
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu sai!")

    tk.Button(login_window, text="Đăng nhập", bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
              width=18, command=login).pack(pady=12)

# -----------------------
# GIAO DIỆN CUNG CẤP THÔNG TIN
# -----------------------
def _open_tenant_info_window(parent, tenant_username, tenant_display_name):
    _ensure_tenant_tables()
    win = tk.Toplevel(parent)
    win.title("Thông tin người thuê")
    win.geometry("480x580")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT full_name, gender, birth_date, phone, email, job, cccd, note FROM TenantInfo WHERE tenant_username=?", (tenant_username,))
    row = c.fetchone()
    conn.close()

    fields = {
        "full_name": tk.StringVar(value=row[0] if row else tenant_display_name),
        "gender": tk.StringVar(value=row[1] if row else ""),
        "birth_date": tk.StringVar(value=row[2] if row else ""),
        "phone": tk.StringVar(value=row[3] if row else ""),
        "email": tk.StringVar(value=row[4] if row else ""),
        "job": tk.StringVar(value=row[5] if row else ""),
        "cccd": tk.StringVar(value=row[6] if row else ""),
        "note": tk.StringVar(value=row[7] if row else "")
    }

    frm = tk.Frame(win)
    frm.pack(padx=12, pady=12, fill='both', expand=True)

    tk.Label(frm, text="🧾 Cung cấp thông tin chi tiết để liên hệ với chủ trọ", font=("Arial", 12, "bold")).pack(pady=6)

    def _row(label_text, var):
        tk.Label(frm, text=label_text, anchor='w').pack(fill='x', pady=(8,0))
        e = tk.Entry(frm, textvariable=var, width=40)
        e.pack()
        return e

    _row("Họ và tên:", fields["full_name"])

    tk.Label(frm, text="Giới tính:", anchor='w').pack(fill='x', pady=(8,0))
    gender_box = ttk.Combobox(frm, textvariable=fields["gender"], values=["Nam", "Nữ", "Khác"], width=37, state="readonly")
    gender_box.pack()

    _row("Ngày sinh (dd/mm/yyyy):", fields["birth_date"])
    _row("Số điện thoại:", fields["phone"])
    _row("Email (Gmail):", fields["email"])
    _row("Nghề nghiệp:", fields["job"])
    _row("CCCD/CMND:", fields["cccd"])

    tk.Label(frm, text="Ghi chú thêm:", anchor='w').pack(fill='x', pady=(8,0))
    note_box = tk.Text(frm, height=4, width=44)
    if row and row[7]:
        note_box.insert("1.0", row[7])
    note_box.pack()

    status_var = tk.StringVar(value="")

    def save_info():
        note_text = note_box.get("1.0", tk.END).strip()
        full_name = fields["full_name"].get().strip()
        email = fields["email"].get().strip()
        phone = fields["phone"].get().strip()
        cccd = fields["cccd"].get().strip()
        birth = fields["birth_date"].get().strip()

        # --- Kiểm tra dữ liệu ---
        if not full_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập họ tên."); return
        if not re.match(r"^[A-Za-zÀ-ỹ\s]+$", full_name):
            messagebox.showerror("Lỗi", "Họ tên chỉ được chứa chữ cái và khoảng trắng."); return
        if email and not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email):
            messagebox.showerror("Lỗi", "Email không hợp lệ! Vui lòng nhập Gmail."); return
        if phone and not re.match(r"^0\d{9}$", phone):
            messagebox.showerror("Lỗi", "Số điện thoại phải có 10 chữ số và bắt đầu bằng 0."); return
        if cccd and not (re.match(r"^\d{9}$", cccd) or re.match(r"^\d{12}$", cccd)):
            messagebox.showerror("Lỗi", "CCCD/CMND phải gồm 9 hoặc 12 chữ số."); return
        if birth:
            try:
                datetime.strptime(birth, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Lỗi", "Ngày sinh không hợp lệ! Định dạng dd/mm/yyyy."); return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            REPLACE INTO TenantInfo (tenant_username, full_name, gender, birth_date, phone, email, job, cccd, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tenant_username, full_name, fields["gender"].get(), birth, phone, email, fields["job"].get(), cccd, note_text))
        conn.commit()
        conn.close()

        status_var.set("✅ Thông tin đã được lưu!")
        _open_find_owner_window(win, tenant_username)

    tk.Button(frm, text="💾 Lưu thông tin", bg="#4CAF50", fg="white", width=20, command=save_info).pack(pady=10)
    tk.Label(frm, textvariable=status_var, fg="green").pack()

# -----------------------
# GIAO DIỆN TÌM CHỦ TRỌ VÀ GỬI YÊU CẦU
# -----------------------
def _open_find_owner_window(parent_win, tenant_username):
    win = tk.Toplevel(parent_win)
    win.title("Tìm chủ trọ theo username")
    win.geometry("480x320")

    frm = tk.Frame(win)
    frm.pack(padx=12, pady=12, fill='both', expand=True)

    tk.Label(frm, text="🔍 Tìm chủ trọ (nhập username):", font=("Arial", 12, "bold")).pack(anchor='w')
    username_var = tk.StringVar()
    tk.Entry(frm, textvariable=username_var, width=40).pack(pady=6)

    result_frame = tk.Frame(frm)
    result_frame.pack(fill='both', expand=True, pady=6)

    info_text = tk.Text(result_frame, height=8, state='disabled')
    info_text.pack(fill='both', expand=True)

    status_var = tk.StringVar(value="")

    def search_owner():
        uname = username_var.get().strip()
        if not uname:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập username của chủ trọ.")
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT Username, HoTen, Email, SDT FROM User WHERE Username=? AND VaiTro=1", (uname,))
        row = c.fetchone()
        conn.close()
        info_text.config(state='normal')
        info_text.delete("1.0", tk.END)
        if row:
            info_text.insert(tk.END, f"Username: {row[0]}\nHọ tên: {row[1]}\nEmail: {row[2]}\nSĐT: {row[3]}\n")
            status_var.set("✅ Chủ trọ tìm thấy. Bạn có thể gửi yêu cầu.")
        else:
            status_var.set("❌ Không tìm thấy chủ trọ với username này.")
        info_text.config(state='disabled')

    def send_request():
        uname = username_var.get().strip()
        if not uname:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập username của chủ trọ.")
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT Username FROM User WHERE Username=? AND VaiTro=1", (uname,))
        row = c.fetchone()
        if not row:
            conn.close()
            messagebox.showerror("Lỗi", "Không tìm thấy chủ trọ.")
            return
        c.execute("SELECT id FROM RentalRequests WHERE tenant_username=? AND owner_username=? AND status='Chờ duyệt'", (tenant_username, uname))
        exist = c.fetchone()
        if exist:
            conn.close()
            messagebox.showinfo("Thông báo", "Bạn đã gửi yêu cầu tới chủ trọ này và đang chờ duyệt.")
            return
        now = datetime.now().isoformat()
        c.execute("INSERT INTO RentalRequests (tenant_username, owner_username, status, created_at) VALUES (?, ?, ?, ?)", (tenant_username, uname, "Chờ duyệt", now))
        conn.commit()
        conn.close()
        messagebox.showinfo("Thành công", "Yêu cầu đã được gửi tới chủ trọ.")
        win.destroy()

    btn_frame = tk.Frame(frm)
    btn_frame.pack(pady=6)
    tk.Button(btn_frame, text="🔍 Tìm kiếm", command=search_owner, width=12).grid(row=0, column=0, padx=8)
    tk.Button(btn_frame, text="📤 Gửi yêu cầu", command=send_request, width=12).grid(row=0, column=1, padx=8)

    tk.Label(frm, textvariable=status_var, fg="green").pack()
