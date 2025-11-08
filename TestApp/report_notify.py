import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

# ==============================
#   1️⃣ Hàm lấy doanh thu thật
# ==============================
def get_revenue(year, month):
    conn = sqlite3.connect("billing.db")
    c = conn.cursor()
    # Chỉ lấy các phòng đã thanh toán
    c.execute("SELECT room, total_amount FROM billing WHERE payment_status='Paid'")
    rows = c.fetchall()
    conn.close()
    return dict(rows)

# ==============================
#   2️⃣ Giao diện Báo cáo
# ==============================
def show_monthly_report(parent):
    parent.withdraw()
    win = tk.Toplevel(parent)
    win.title("📈 Báo cáo doanh thu tháng")

    def on_close():
        win.destroy()
        parent.deiconify()
    win.protocol("WM_DELETE_WINDOW", on_close)

    header = tk.Frame(win)
    header.pack(fill='x', padx=5, pady=5)
    tk.Button(header, text="⬅️ Quay lại", command=on_close).pack(side='left')

    top = tk.Frame(win)
    top.pack(padx=10, pady=5, anchor="w")

    current = datetime.now()
    year_var = tk.IntVar(value=current.year)
    month_var = tk.IntVar(value=current.month)

    tk.Label(top, text="Năm:").grid(row=0, column=0)
    tk.Spinbox(top, from_=2000, to=2100, textvariable=year_var, width=6).grid(row=0, column=1, padx=5)
    tk.Label(top, text="Tháng:").grid(row=0, column=2)
    tk.Spinbox(top, from_=1, to=12, textvariable=month_var, width=4).grid(row=0, column=3, padx=5)

    result = tk.Text(win, width=60, height=15, state='disabled')
    result.pack(padx=10, pady=5)

    def on_report():
        y, m = int(year_var.get()), int(month_var.get())
        data = get_revenue(y, m)
        total = sum(data.values())
        result.config(state='normal')
        result.delete(1.0, tk.END)
        result.insert(tk.END, f"Báo cáo doanh thu tháng {y}-{m:02d}\n\n")
        for room, amount in data.items():
            result.insert(tk.END, f"{room}: {amount:.0f} VND\n")
        result.insert(tk.END, f"\nTổng doanh thu: {total:.0f} VND\n")
        result.config(state='disabled')

    ttk.Button(top, text="📊 Tổng hợp", command=on_report).grid(row=0, column=4, padx=5)

# ==============================
#   3️⃣ Gửi Thông báo
# ==============================
def show_notify_window(parent):
    parent.withdraw()
    win = tk.Toplevel(parent)
    win.title("📣 Gửi thông báo")

    def on_close():
        win.destroy()
        parent.deiconify()
    win.protocol("WM_DELETE_WINDOW", on_close)

    header = tk.Frame(win)
    header.pack(fill='x', padx=5, pady=5)
    tk.Button(header, text="⬅️ Quay lại", command=on_close).pack(side='left')

    content = tk.Frame(win)
    content.pack(fill="both", expand=True)

    def clear_content():
        for w in content.winfo_children():
            w.destroy()

    def render_type_selection():
        clear_content()
        tk.Button(content, text="✉️ Thông báo chung", font=("Segoe UI", 14, "bold"),
                  bg="#FFFFFF", padx=20, pady=18, command=render_common).grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        tk.Button(content, text="💬 Thông báo riêng", font=("Segoe UI", 14, "bold"),
                  bg="#FFFFFF", padx=20, pady=18, command=render_private).grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def render_common():
        clear_content()
        tk.Button(content, text="⬅️ Quay lại", command=render_type_selection).pack(anchor='w', padx=5, pady=5)
        predefined = [
            "Cầu thang máy bị hỏng vui lòng dùng thang bộ.",
            "Nước bị cắt 1 ngày mọi người hãy chuẩn bị kĩ.",
            "Ngày mai đến lịch đổ rác, mọi người hãy mang rác ra ngoài."
        ]
        common_vars = [tk.BooleanVar() for _ in predefined]
        for i, msg in enumerate(predefined):
            tk.Checkbutton(content, text=msg, variable=common_vars[i], anchor='w').pack(anchor='w')

        tk.Label(content, text="📝 Nhập thông báo:").pack(anchor='w')
        common_manual = tk.Text(content, height=3, width=40)
        common_manual.pack()

        status = tk.StringVar(value="Chưa gửi")
        tk.Label(content, textvariable=status).pack(side="bottom", fill="x")

        def send_all():
            selected = [predefined[i] for i, v in enumerate(common_vars) if v.get()]
            manual = common_manual.get("1.0", tk.END).strip()
            msg = " ".join(selected + ([manual] if manual else []))
            if not msg:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung thông báo.")
                return
            print("Gửi thông báo chung:", msg)
            status.set("✅ Đã gửi thông báo chung tới tất cả các phòng.")

        ttk.Button(content, text="📤 Gửi", command=send_all).pack(pady=5)

    def render_private():
        clear_content()
        tk.Button(content, text="⬅️ Quay lại", command=render_type_selection).pack(anchor='w', padx=5, pady=5)
        rooms_list = tk.Listbox(content, selectmode='multiple', height=6)
        rooms_list.pack()
        for r in ["P101", "P102", "P103", "P201", "P202", "P203"]:
            rooms_list.insert(tk.END, r)
        tk.Label(content, text="📝 Nhập thông báo:").pack(anchor='w')
        text_box = tk.Text(content, height=3, width=40)
        text_box.pack()
        status = tk.StringVar(value="Chưa gửi")
        tk.Label(content, textvariable=status).pack(side="bottom", fill="x")

        def send_private():
            indices = rooms_list.curselection()
            if not indices:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một phòng.")
                return
            message = text_box.get("1.0", tk.END).strip()
            if not message:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung thông báo.")
                return
            selected_rooms = [rooms_list.get(i) for i in indices]
            print(f"Gửi thông báo tới {selected_rooms}: {message}")
            status.set(f"✅ Đã gửi thông báo tới {len(selected_rooms)} phòng.")

        ttk.Button(content, text="📤 Gửi", command=send_private).pack(pady=5)

    render_type_selection()

# ==============================
#   4️⃣ Gửi Cảnh báo
# ==============================
def show_warning_window(parent):
    parent.withdraw()
    win = tk.Toplevel(parent)
    win.title("⚠️ Gửi cảnh báo")

    def on_close():
        win.destroy()
        parent.deiconify()
    win.protocol("WM_DELETE_WINDOW", on_close)

    header = tk.Frame(win)
    header.pack(fill='x', padx=5, pady=5)
    tk.Button(header, text="⬅️ Quay lại", command=on_close).pack(side='left')

    left = tk.LabelFrame(win, text="⚠️ Chọn phòng nhận cảnh báo:")
    left.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    rooms_list = tk.Listbox(left, selectmode='multiple', height=6)
    for r in ["P101", "P102", "P103", "P201", "P202", "P203"]:
        rooms_list.insert(tk.END, r)
    rooms_list.pack()

    right = tk.LabelFrame(win, text="🔔 Nội dung cảnh báo:")
    right.pack(side="right", fill="both", expand=True, padx=5, pady=5)
    predefined = ["Bạn đã quá hạn nộp tiền trọ.", "Hợp đồng sắp hết hạn, vui lòng gia hạn."]
    warn_vars = [tk.BooleanVar() for _ in predefined]
    for i, msg in enumerate(predefined):
        tk.Checkbutton(right, text=msg, variable=warn_vars[i], anchor='w').pack(anchor='w')
    tk.Label(right, text="📝 Nhập cảnh báo:").pack(anchor='w')
    manual = tk.Text(right, height=3, width=40)
    manual.pack()

    status = tk.StringVar(value="Chưa gửi")
    tk.Label(win, textvariable=status).pack(side="bottom", fill="x")

    def send_warning():
        indices = rooms_list.curselection()
        if not indices:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một phòng.")
            return
        msg = " ".join([predefined[i] for i, v in enumerate(warn_vars) if v.get()])
        manual_msg = manual.get("1.0", tk.END).strip()
        if manual_msg:
            msg += (" " + manual_msg)
        if not msg.strip():
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung cảnh báo.")
            return
        selected = [rooms_list.get(i) for i in indices]
        print(f"Gửi cảnh báo tới {selected}: {msg}")
        status.set(f"✅ Đã gửi cảnh báo tới {len(selected)} phòng.")

    ttk.Button(right, text="📤 Gửi", command=send_warning).pack(pady=5)
def show_report_menu(parent):
    """Hiển thị menu có 3 lựa chọn: Báo cáo, Gửi thông báo, Gửi cảnh báo"""
    parent.withdraw()
    win = tk.Toplevel(parent)
    win.title("📊 Báo cáo & Thông báo")

    def on_close():
        win.destroy()
        parent.deiconify()

    win.protocol("WM_DELETE_WINDOW", on_close)

    header = tk.Frame(win)
    header.pack(fill='x', padx=5, pady=5)
    tk.Button(header, text="⬅️ Quay lại", command=on_close).pack(side='left')

    frame = tk.Frame(win)
    frame.pack(padx=20, pady=20)

    tk.Button(frame, text="📈 Báo cáo doanh thu tháng",
              command=lambda: show_monthly_report(win),
              bg="#2196F3", fg="white", width=30, height=2).pack(pady=8)

    tk.Button(frame, text="📣 Gửi thông báo",
              command=lambda: show_notify_window(win),
              bg="#FFC107", fg="black", width=30, height=2).pack(pady=8)

    tk.Button(frame, text="⚠️ Gửi cảnh cáo",
              command=lambda: show_warning_window(win),
              bg="#F44336", fg="white", width=30, height=2).pack(pady=8)
