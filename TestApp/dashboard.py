import tkinter as tk
from tkinter import messagebox
from billing import BillingApp
from report_notify import show_report_menu

def open_owner_dashboard(parent, owner_id, owner_name):
    dashboard = tk.Toplevel(parent)
    dashboard.title(f"Bảng điều khiển - Chủ trọ {owner_name}")
    dashboard.geometry("420x420")
    dashboard.config(bg="#f4f4f4")

    tk.Label(dashboard, text=f"Xin chào, Chủ trọ {owner_name}", font=("Arial", 14, "bold"), bg="#f4f4f4").pack(pady=18)

    tk.Button(dashboard, text="📋 Quản lý thông tin", width=28, height=2, bg="#4CAF50", fg="white",
              font=("Arial", 11, "bold"), command=lambda: messagebox.showinfo("Chức năng", "Quản lý thông tin")).pack(pady=8)

    tk.Button(dashboard, text="💰 Quản lý tài chính (Hóa đơn)", width=28, height=2, bg="#2196F3", fg="white",
              font=("Arial", 11, "bold"), command=lambda: BillingApp(dashboard, readonly=False)).pack(pady=8)

    tk.Button(dashboard, text="📊 Báo cáo & Thông báo", width=28, height=2, bg="#FF9800", fg="white",
              font=("Arial", 11, "bold"), command=lambda: show_report_menu(dashboard)).pack(pady=8)

    tk.Button(dashboard, text="Đăng xuất", width=16, bg="red", fg="white",
              font=("Arial", 11, "bold"), command=dashboard.destroy).pack(pady=20)
