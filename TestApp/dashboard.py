# dashboard.py
import tkinter as tk
from tkinter import messagebox
from billing import BillingApp
from report_notify import show_report_menu
import sqlite3

DB_PATH = "nhatro.db"

def _get_owner_username_by_id(owner_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT Username FROM User WHERE User_ID=?", (owner_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def _count_pending_requests_for_owner(owner_username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM RentalRequests WHERE owner_username=? AND status='Chờ duyệt'", (owner_username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def open_owner_dashboard(parent, owner_id, owner_name):
    dashboard = tk.Toplevel(parent)
    dashboard.title(f"Bảng điều khiển - Chủ trọ {owner_name}")
    dashboard.geometry("420x420")
    dashboard.config(bg="#f4f4f4")

    # Top frame: greeting (left) and bell (right)
    top_frame = tk.Frame(dashboard, bg="#f4f4f4")
    top_frame.pack(fill='x', pady=(12,4), padx=8)

    lbl = tk.Label(top_frame, text=f"Xin chào, Chủ trọ {owner_name}", font=("Arial", 14, "bold"), bg="#f4f4f4")
    lbl.pack(side='left', padx=(8,0))

    # Get owner username to count notifications
    owner_username = _get_owner_username_by_id(owner_id)
    pending_count = _count_pending_requests_for_owner(owner_username) if owner_username else 0

    # Bell (on the right)
    bell_text = tk.StringVar(value=f"🔔 {pending_count}" if pending_count > 0 else "🔔")
    def on_bell_click():
        _open_requests_window(dashboard, owner_username, bell_text)
    
    # --- Biểu tượng 🔔 thông báo ---
    def on_hover(e):
        bell_btn.config(bg="#ff4444")

    def on_leave(e):
        bell_btn.config(bg=bell_color)

    # 🔔 Nếu có yêu cầu thuê mới -> màu đỏ cam, không thì xám
    bell_color = "#ff5555" if pending_count > 0 else "#dddddd"

    bell_btn = tk.Button(
        top_frame,
        text="🔔",        # <== Biểu tượng y hệt như bạn muốn
        font=("Arial", 14, "bold"),
        bg=bell_color,
        fg="white",
        activebackground="#ff3333",
        activeforeground="white",
        bd=0,
        relief="flat",
        cursor="hand2",
        command=on_bell_click,
        width=2,
        height=1
    )
    bell_btn.bind("<Enter>", on_hover)
    bell_btn.bind("<Leave>", on_leave)
    bell_btn.pack(side='right', padx=(0, 8))
    

    # Main buttons
    btn_frame = tk.Frame(dashboard, bg="#f4f4f4")
    btn_frame.pack(pady=18)

    tk.Button(btn_frame, text="📋 Quản lý thông tin", width=28, height=2, bg="#4CAF50", fg="white",
              font=("Arial", 11, "bold"), command=lambda: messagebox.showinfo("Chức năng", "Quản lý thông tin")).pack(pady=8)

    tk.Button(btn_frame, text="💰 Quản lý tài chính (Hóa đơn)", width=28, height=2, bg="#2196F3", fg="white",
              font=("Arial", 11, "bold"), command=lambda: BillingApp(dashboard, readonly=False)).pack(pady=8)

    tk.Button(btn_frame, text="📊 Báo cáo & Thông báo", width=28, height=2, bg="#FF9800", fg="white",
              font=("Arial", 11, "bold"), command=lambda: show_report_menu(dashboard)).pack(pady=8)

    tk.Button(dashboard, text="Đăng xuất", width=16, bg="red", fg="white",
              font=("Arial", 11, "bold"), command=dashboard.destroy).pack(pady=20)

def _open_requests_window(parent, owner_username, bell_text_var):
    """
    Mở cửa sổ danh sách các yêu cầu gửi tới owner_username.
    bell_text_var là tk.StringVar của nút chuông để cập nhật số lượng.
    """
    if not owner_username:
        messagebox.showwarning("Lỗi", "Không xác định được username chủ trọ.")
        return

    win = tk.Toplevel(parent)
    win.title("Yêu cầu thuê trọ")
    win.geometry("640x420")

    header = tk.Frame(win)
    header.pack(fill='x', pady=6, padx=6)
    tk.Button(header, text="⬅️ Quay lại", command=win.destroy).pack(side='left')

    # Table-like list of requests
    list_frame = tk.Frame(win)
    list_frame.pack(fill='both', expand=True, padx=8, pady=8)

    canvas = tk.Canvas(list_frame)
    scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
    scrollable = tk.Frame(canvas)

    scrollable.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Load requests
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, tenant_username, status, created_at FROM RentalRequests WHERE owner_username=? ORDER BY created_at DESC", (owner_username,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        tk.Label(scrollable, text="Chưa có yêu cầu thuê trọ nào.", fg="gray").pack(pady=12)
    else:
        for req in rows:
            req_id, tenant_un, status, created_at = req
            frame = tk.Frame(scrollable, bd=1, relief="groove", padx=8, pady=6)
            frame.pack(fill='x', pady=6, padx=6)

            tk.Label(frame, text=f"Người thuê: {tenant_un}", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky='w')
            tk.Label(frame, text=f"Ngày gửi: {created_at}", fg="gray").grid(row=0, column=1, sticky='e', padx=8)
            tk.Label(frame, text=f"Trạng thái: {status}", fg="blue").grid(row=1, column=0, sticky='w', pady=(4,0))

            btns = tk.Frame(frame)
            btns.grid(row=1, column=1, sticky='e')

            def make_view_closure(rid=req_id):
                return lambda: _view_request_detail(win, rid, owner_username, bell_text_var, refresh_list=False)
            tk.Button(btns, text="👁️ Xem chi tiết", command=make_view_closure()).pack(side='left', padx=4)

            if status == "Chờ duyệt":
                def make_accept_closure(rid=req_id, tenant=tenant_un):
                    return lambda: _update_request_status(win, rid, "Được chấp nhận", owner_username, bell_text_var)
                def make_reject_closure(rid=req_id):
                    return lambda: _update_request_status(win, rid, "Bị từ chối", owner_username, bell_text_var)
                tk.Button(btns, text="✅ Chấp nhận", command=make_accept_closure(), bg="#28a745", fg="white").pack(side='left', padx=4)
                tk.Button(btns, text="❌ Từ chối", command=make_reject_closure(), bg="#dc3545", fg="white").pack(side='left', padx=4)

def _view_request_detail(parent, request_id, owner_username, bell_text_var, refresh_list=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT tenant_username, status, created_at FROM RentalRequests WHERE id=?", (request_id,))
    req = c.fetchone()
    if not req:
        conn.close()
        messagebox.showerror("Lỗi", "Không tìm thấy yêu cầu.")
        return
    tenant_username, status, created_at = req
    # Load tenant info
    c.execute("SELECT full_name, gender, birth_date, phone, email, job, cccd, note FROM TenantInfo WHERE tenant_username=?", (tenant_username,))
    tinfo = c.fetchone()
    conn.close()

    win = tk.Toplevel(parent)
    win.title(f"Chi tiết yêu cầu #{request_id}")
    win.geometry("480x520")
    frm = tk.Frame(win)
    frm.pack(padx=12, pady=12, fill='both', expand=True)

    tk.Label(frm, text=f"Yêu cầu từ: {tenant_username}", font=("Arial", 12, "bold")).pack(anchor='w')
    tk.Label(frm, text=f"Ngày gửi: {created_at}", fg="gray").pack(anchor='w')

    if tinfo:
        labels = ["Họ và tên", "Giới tính", "Ngày sinh", "SĐT", "Email", "Nghề nghiệp", "CCCD", "Ghi chú"]
        for label, val in zip(labels, tinfo):
            tk.Label(frm, text=f"{label}: {val if val else '-'}", anchor='w', justify='left', wraplength=440).pack(anchor='w', pady=(6,0))
    else:
        tk.Label(frm, text="Không có thông tin chi tiết người thuê.", fg="gray").pack(anchor='w')

    def accept():
        _update_request_status(win, request_id, "Được chấp nhận", owner_username, bell_text_var)
        win.destroy()
    def reject():
        _update_request_status(win, request_id, "Bị từ chối", owner_username, bell_text_var)
        win.destroy()

    btn_frame = tk.Frame(frm)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="✅ Chấp nhận", command=accept, bg="#28a745", fg="white", width=12).pack(side='left', padx=6)
    tk.Button(btn_frame, text="❌ Từ chối", command=reject, bg="#dc3545", fg="white", width=12).pack(side='left', padx=6)

def _update_request_status(parent, request_id, new_status, owner_username, bell_text_var):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE RentalRequests SET status=? WHERE id=?", (new_status, request_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Cập nhật", f"Yêu cầu đã được cập nhật: {new_status}")
    # Cập nhật lại số trên chuông
    pending = _count_pending_requests_for_owner(owner_username)
    bell_text_var.set(f"🔔 {pending}" if pending and pending > 0 else "🔔")
    # Close parent windows or refresh if needed

