# auth_module.py
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
import hashlib
from datetime import datetime
import re

DB_PATH = "nhatro.db"

# -----------------------
# KHỞI TẠO BẢNG CẦN THIẾT
# -----------------------
def _ensure_user_table():
    conn = sqlite3.connect(DB_PATH)
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

# ensure tables exist at import
_try1 = _ensure_user_table()
_try2 = _ensure_tenant_tables()

# -----------------------
# HÀM HỖ TRỢ VALIDATION CHUNG (dùng ở đăng ký và tenant info)
# -----------------------
def _validate_fullname(name):
    return bool(re.match(r"^[A-Za-zÀ-ỹ\s]+$", name))

def _validate_email_gmail(email):
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email))

def _validate_phone(phone):
    return bool(re.match(r"^0\d{9}$", phone))

def _validate_cccd(cccd):
    return bool(re.match(r"^\d{9}$", cccd) or re.match(r"^\d{12}$", cccd))

def _validate_birth_date(birth):
    try:
        datetime.strptime(birth, "%d/%m/%Y")
        return True
    except Exception:
        return False

def _hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def validate_password_strength(pw):
    if len(pw) < 8:
        return "Mật khẩu phải có ít nhất 8 ký tự!"
    if not re.search(r"[A-Z]", pw):
        return "Mật khẩu phải chứa ít nhất 1 chữ in hoa!"
    if not re.search(r"[a-z]", pw):
        return "Mật khẩu phải chứa ít nhất 1 chữ thường!"
    if not re.search(r"[0-9]", pw):
        return "Mật khẩu phải chứa ít nhất 1 chữ số!"
    return None

# -----------------------
# REGISTER: giữ giao diện gốc (cả chủ trọ & người thuê)
# -----------------------
def register_user(parent, vaitro, title):
    """
    vaitro: 1 = chủ trọ, 2 = người thuê
    title: string hiển thị trên cửa sổ
    """
    _ensure_user_table()
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

        # required basic check
        if not all([data["HoTen"], data["Username"], data["Password"], data["Confirm"], data["SDT"], data["Email"]]):
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ các trường bắt buộc.")
            return

        # password match
        if data["Password"] != data["Confirm"]:
            messagebox.showerror("Lỗi", "Mật khẩu nhập lại không khớp.")
            return

        # fullname
        if not _validate_fullname(data["HoTen"]):
            messagebox.showerror("Lỗi", "Họ tên chỉ được chứa chữ cái và khoảng trắng.")
            return

        # birth if present
        if data["NgaySinh"]:
            if not _validate_birth_date(data["NgaySinh"]):
                messagebox.showerror("Lỗi", "Ngày sinh không hợp lệ! Định dạng dd/mm/yyyy.")
                return

        # email gmail
        if not _validate_email_gmail(data["Email"]):
            messagebox.showerror("Lỗi", "Email không hợp lệ! Vui lòng nhập Gmail.")
            return

        # phone
        if not _validate_phone(data["SDT"]):
            messagebox.showerror("Lỗi", "Số điện thoại không hợp lệ! Phải gồm 10 chữ số và bắt đầu bằng 0.")
            return

        # cccd
        if data["CCCD"]:
            if not _validate_cccd(data["CCCD"]):
                messagebox.showerror("Lỗi", "CCCD/CMND phải gồm 9 hoặc 12 chữ số.")
                return

        # username
        if len(data["Username"]) < 4 or " " in data["Username"]:
            messagebox.showerror("Lỗi", "Tên đăng nhập phải có ít nhất 4 ký tự và không chứa khoảng trắng.")
            return

        # password strength
        pw_err = validate_password_strength(data["Password"])
        if pw_err:
            messagebox.showerror("Lỗi", pw_err)
            return

        # save to DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            hashed_pw = _hash_password(data["Password"])
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
# FORGOT PASSWORD (đặt lại trực tiếp theo Cách 1)
# -----------------------
def _forgot_password_flow(parent, role):
    """
    role: 1 for owner, 2 for tenant
    """
    top = tk.Toplevel(parent)
    top.title("Quên mật khẩu")
    top.geometry("360x220")
    top.config(bg="#f9f9f9")

    tk.Label(top, text="Đặt lại mật khẩu", font=("Arial", 12, "bold"), bg="#f9f9f9").pack(pady=8)
    tk.Label(top, text="Tên đăng nhập:", bg="#f9f9f9").pack()
    username_entry = tk.Entry(top, width=32); username_entry.pack(pady=5)
    tk.Label(top, text="Email đã đăng ký (Gmail):", bg="#f9f9f9").pack()
    email_entry = tk.Entry(top, width=32); email_entry.pack(pady=5)

    def verify_and_reset():
        u = username_entry.get().strip()
        e = email_entry.get().strip()
        if not u or not e:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ thông tin.")
            return
        if not _validate_email_gmail(e):
            messagebox.showerror("Lỗi", "Email không hợp lệ. Vui lòng nhập Gmail.")
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM User WHERE Username=? AND Email=? AND VaiTro=?", (u, e, role))
        user = c.fetchone()
        conn.close()
        if not user:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản với thông tin vừa nhập.")
            return
        # mở form reset
        reset_win = tk.Toplevel(top)
        reset_win.title("Đặt mật khẩu mới")
        reset_win.geometry("340x200")
        reset_win.config(bg="#f9f9f9")
        tk.Label(reset_win, text="Mật khẩu mới:", bg="#f9f9f9").pack(pady=6)
        pw1 = tk.Entry(reset_win, show="*", width=30); pw1.pack(pady=4)
        tk.Label(reset_win, text="Xác nhận mật khẩu:", bg="#f9f9f9").pack(pady=6)
        pw2 = tk.Entry(reset_win, show="*", width=30); pw2.pack(pady=4)

        def do_reset():
            p1 = pw1.get().strip(); p2 = pw2.get().strip()
            if not p1 or not p2:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập mật khẩu mới và xác nhận.")
                return
            if p1 != p2:
                messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp."); return
            pw_err = validate_password_strength(p1)
            if pw_err:
                messagebox.showerror("Lỗi", pw_err); return
            hashed = _hash_password(p1)
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE User SET Password=? WHERE Username=?", (hashed, u))
            conn.commit(); conn.close()
            messagebox.showinfo("Thành công", "Đặt lại mật khẩu thành công! Vui lòng đăng nhập lại.")
            reset_win.destroy(); top.destroy()

        tk.Button(reset_win, text="Xác nhận", bg="#4CAF50", fg="white", width=16, command=do_reset).pack(pady=12)

    tk.Button(top, text="Xác minh", bg="#4CAF50", fg="white", width=16, command=verify_and_reset).pack(pady=12)

# -----------------------
# ĐĂNG NHẬP CHỦ TRỌ
# -----------------------
def open_owner_login(parent):
    login_window = tk.Toplevel(parent)
    login_window.title("Đăng nhập - Chủ trọ")
    login_window.geometry("360x360")
    login_window.config(bg="#f9f9f9")

    tk.Label(login_window, text="Đăng nhập dành cho Chủ trọ", font=("Arial", 14, "bold"), bg="#f9f9f9").pack(pady=18)

    tk.Label(login_window, text="Tên đăng nhập:", bg="#f9f9f9").pack()
    username_entry = tk.Entry(login_window, width=30); username_entry.pack(pady=5)

    tk.Label(login_window, text="Mật khẩu:", bg="#f9f9f9").pack()
    password_entry = tk.Entry(login_window, width=30, show="*"); password_entry.pack(pady=5)

    show_password_var = tk.BooleanVar()
    tk.Checkbutton(login_window, text="Hiện mật khẩu", variable=show_password_var,
                   bg="#f9f9f9", command=lambda: password_entry.config(show="" if show_password_var.get() else "*")).pack()

    def login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return
        hashed_pw = _hash_password(password)
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT * FROM User WHERE Username=? AND Password=? AND VaiTro=1", (username, hashed_pw))
        user = c.fetchone(); conn.close()
        if user:
            messagebox.showinfo("Đăng nhập thành công", f"Chào mừng, Chủ trọ {user[4]}!")
            login_window.destroy()
            # Late import để tránh circular import
            from dashboard import open_owner_dashboard
            open_owner_dashboard(parent, user[0], user[4])
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu sai!")

    tk.Button(login_window, text="Đăng nhập", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
              width=18, command=login).pack(pady=10)

    # Quên mật khẩu (link nhỏ màu xanh giống gốc)
    q_label = tk.Label(login_window, text="Quên mật khẩu?", fg="blue", bg="#f9f9f9", cursor="hand2")
    q_label.pack()
    q_label.bind("<Button-1>", lambda e: _forgot_password_flow(login_window, 1))

    # Nút đăng ký link: mở dialog chọn đăng ký hay gọi register_user trực tiếp
    tk.Button(login_window, text="Chưa có tài khoản? Đăng ký ngay", font=("Arial", 10, "underline"),
              bg="#f9f9f9", fg="blue", bd=0, cursor="hand2",
              command=lambda: register_user(login_window, 1, "Đăng ký Chủ trọ")).pack(pady=6)

# -----------------------
# ĐĂNG NHẬP NGƯỜI THUÊ
# -----------------------
def open_tenant_page(parent):
    login_window = tk.Toplevel(parent)
    login_window.title("Đăng nhập - Người thuê")
    login_window.geometry("360x360")
    login_window.config(bg="#f9f9f9")

    tk.Label(login_window, text="Đăng nhập dành cho Người thuê", font=("Arial", 14, "bold"), bg="#f9f9f9").pack(pady=18)

    tk.Label(login_window, text="Tên đăng nhập:", bg="#f9f9f9").pack()
    username_entry = tk.Entry(login_window, width=30); username_entry.pack(pady=5)

    tk.Label(login_window, text="Mật khẩu:", bg="#f9f9f9").pack()
    password_entry = tk.Entry(login_window, width=30, show="*"); password_entry.pack(pady=5)

    show_password_var = tk.BooleanVar()
    tk.Checkbutton(login_window, text="Hiện mật khẩu", variable=show_password_var,
                   bg="#f9f9f9", command=lambda: password_entry.config(show="" if show_password_var.get() else "*")).pack()

    def login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return
        hashed_pw = _hash_password(password)
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT * FROM User WHERE Username=? AND Password=? AND VaiTro=2", (username, hashed_pw))
        user = c.fetchone(); conn.close()
        if user:
            messagebox.showinfo("Đăng nhập thành công", f"Chào mừng, {user[4]}!")
            login_window.destroy()
            # mở giao diện người thuê để cung cấp thông tin, tìm chủ trọ
            _open_tenant_info_window(parent, username, user[4])
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu sai!")

    tk.Button(login_window, text="Đăng nhập", bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
              width=18, command=login).pack(pady=10)

    # Quên mật khẩu (link nhỏ màu xanh giống gốc)
    q_label = tk.Label(login_window, text="Quên mật khẩu?", fg="blue", bg="#f9f9f9", cursor="hand2")
    q_label.pack()
    q_label.bind("<Button-1>", lambda e: _forgot_password_flow(login_window, 2))

    # đăng ký link (mở register_user với vai trò người thuê)
    tk.Button(login_window, text="Chưa có tài khoản? Đăng ký ngay", font=("Arial", 10, "underline"),
              bg="#f9f9f9", fg="blue", bd=0, cursor="hand2",
              command=lambda: register_user(login_window, 2, "Đăng ký Người thuê")).pack(pady=6)

# -----------------------
# GIAO DIỆN NGƯỜI THUÊ: cung cấp thông tin chi tiết (với validate)
# -----------------------
def _open_tenant_info_window(parent, tenant_username, tenant_display_name):
    _ensure_tenant_tables()
    win = tk.Toplevel(parent)
    win.title("Thông tin người thuê")
    win.geometry("480x580")
    win.config(bg="#f9f9f9")

    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT full_name, gender, birth_date, phone, email, job, cccd, note FROM TenantInfo WHERE tenant_username=?", (tenant_username,))
    row = c.fetchone(); conn.close()

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

    frm = tk.Frame(win, bg="#f9f9f9")
    frm.pack(padx=12, pady=12, fill='both', expand=True)

    tk.Label(frm, text="🧾 Cung cấp thông tin chi tiết để liên hệ với chủ trọ", font=("Arial", 12, "bold"), bg="#f9f9f9").pack(pady=6)

    def _row(label_text, var):
        tk.Label(frm, text=label_text, anchor='w', bg="#f9f9f9").pack(fill='x', pady=(8,0))
        e = tk.Entry(frm, textvariable=var, width=40); e.pack()
        return e

    _row("Họ và tên:", fields["full_name"])

    tk.Label(frm, text="Giới tính:", anchor='w', bg="#f9f9f9").pack(fill='x', pady=(8,0))
    gender_box = ttk.Combobox(frm, textvariable=fields["gender"], values=["Nam", "Nữ", "Khác"], width=37, state="readonly")
    gender_box.pack()

    _row("Ngày sinh (dd/mm/yyyy):", fields["birth_date"])
    _row("Số điện thoại:", fields["phone"])
    _row("Email (Gmail):", fields["email"])
    _row("Nghề nghiệp:", fields["job"])
    _row("CCCD/CMND:", fields["cccd"])

    tk.Label(frm, text="Ghi chú thêm:", anchor='w', bg="#f9f9f9").pack(fill='x', pady=(8,0))
    note_box = tk.Text(frm, height=4, width=44)
    if row and row[7]:
        note_box.insert("1.0", row[7])
    note_box.pack()

    status_var = tk.StringVar(value="")

    def save_info():
        note_text = note_box.get("1.0", tk.END).strip()
        full_name = fields["full_name"].get().strip()
        gender = fields["gender"].get().strip()
        email = fields["email"].get().strip()
        phone = fields["phone"].get().strip()
        cccd = fields["cccd"].get().strip()
        birth = fields["birth_date"].get().strip()
        job = fields["job"].get().strip()

        # validation
        if not full_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập họ tên."); return
        if not _validate_fullname(full_name):
            messagebox.showerror("Lỗi", "Họ tên chỉ được chứa chữ cái và khoảng trắng."); return
        if email and not _validate_email_gmail(email):
            messagebox.showerror("Lỗi", "Email không hợp lệ! Vui lòng nhập Gmail."); return
        if phone and not _validate_phone(phone):
            messagebox.showerror("Lỗi", "Số điện thoại phải có 10 chữ số và bắt đầu bằng 0."); return
        if cccd and not _validate_cccd(cccd):
            messagebox.showerror("Lỗi", "CCCD/CMND phải gồm 9 hoặc 12 chữ số."); return
        if birth and not _validate_birth_date(birth):
            messagebox.showerror("Lỗi", "Ngày sinh không hợp lệ! Định dạng dd/mm/yyyy."); return

        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("""
            REPLACE INTO TenantInfo (tenant_username, full_name, gender, birth_date, phone, email, job, cccd, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tenant_username, full_name, gender, birth, phone, email, job, cccd, note_text))
        conn.commit(); conn.close()
        status_var.set("✅ Thông tin đã được lưu!")
        # open find owner window
        _open_find_owner_window(win, tenant_username)

    tk.Button(frm, text="💾 Lưu thông tin", bg="#4CAF50", fg="white", width=20, command=save_info).pack(pady=10)
    tk.Label(frm, textvariable=status_var, fg="green", bg="#f9f9f9").pack()

# -----------------------
# TÌM CHỦ TRỌ THEO USERNAME VÀ GỬI YÊU CẦU
# -----------------------
def _open_find_owner_window(parent_win, tenant_username):
    win = tk.Toplevel(parent_win)
    win.title("Tìm chủ trọ theo username")
    win.geometry("480x320")
    win.config(bg="#f9f9f9")

    frm = tk.Frame(win, bg="#f9f9f9")
    frm.pack(padx=12, pady=12, fill='both', expand=True)

    tk.Label(frm, text="🔍 Tìm chủ trọ (nhập username):", font=("Arial", 12, "bold"), bg="#f9f9f9").pack(anchor='w')
    username_var = tk.StringVar()
    tk.Entry(frm, textvariable=username_var, width=40).pack(pady=6)

    result_frame = tk.Frame(frm, bg="#f9f9f9")
    result_frame.pack(fill='both', expand=True, pady=6)

    info_text = tk.Text(result_frame, height=8, state='disabled')
    info_text.pack(fill='both', expand=True)

    status_var = tk.StringVar(value="")

    def search_owner():
        uname = username_var.get().strip()
        if not uname:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập username của chủ trọ."); return
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT Username, HoTen, Email, SDT FROM User WHERE Username=? AND VaiTro=1", (uname,))
        row = c.fetchone(); conn.close()
        info_text.config(state='normal'); info_text.delete("1.0", tk.END)
        if row:
            info_text.insert(tk.END, f"Username: {row[0]}\nHọ tên: {row[1]}\nEmail: {row[2]}\nSĐT: {row[3]}\n")
            status_var.set("✅ Chủ trọ tìm thấy. Bạn có thể gửi yêu cầu.")
        else:
            status_var.set("❌ Không tìm thấy chủ trọ với username này.")
        info_text.config(state='disabled')

    def send_request():
        uname = username_var.get().strip()
        if not uname:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập username của chủ trọ."); return
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT Username FROM User WHERE Username=? AND VaiTro=1", (uname,))
        row = c.fetchone()
        if not row:
            conn.close(); messagebox.showerror("Lỗi", "Không tìm thấy chủ trọ."); return
        c.execute("SELECT id FROM RentalRequests WHERE tenant_username=? AND owner_username=? AND status='Chờ duyệt'", (tenant_username, uname))
        exist = c.fetchone()
        if exist:
            conn.close(); messagebox.showinfo("Thông báo", "Bạn đã gửi yêu cầu tới chủ trọ này và đang chờ duyệt."); return
        now = datetime.now().isoformat()
        c.execute("INSERT INTO RentalRequests (tenant_username, owner_username, status, created_at) VALUES (?, ?, ?, ?)",
                  (tenant_username, uname, "Chờ duyệt", now))
        conn.commit(); conn.close()
        messagebox.showinfo("Thành công", "Yêu cầu đã được gửi tới chủ trọ.")
        win.destroy()

    btn_frame = tk.Frame(frm, bg="#f9f9f9"); btn_frame.pack(pady=6)
    tk.Button(btn_frame, text="🔍 Tìm kiếm", command=search_owner, width=12).grid(row=0, column=0, padx=8)
    tk.Button(btn_frame, text="📤 Gửi yêu cầu", command=send_request, width=12).grid(row=0, column=1, padx=8)
    tk.Label(frm, textvariable=status_var, fg="green", bg="#f9f9f9").pack()

# End of file
