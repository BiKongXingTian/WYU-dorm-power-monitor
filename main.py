# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import time
import sys

from PIL import Image, ImageDraw
import pystray

from config_store import load_config, save_config
from power_api import query_power
from notifier import send_toast


def _make_icon_image(size=64):
    """生成一个简单的托盘图标，避免依赖外部 ico 文件。"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r = size // 2 - 4
    c = size // 2
    draw.ellipse((c - r, c - r, c + r, c + r), fill="#2196F3")
    draw.text((c - 14, c - 10), "电", fill="white")
    return img


class DormPowerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("宿舍电量监控")
        self.root.geometry("420x320")
        self.root.resizable(False, False)

        self.config = load_config()
        self._monitor: threading.Thread | None = None
        self._stop = threading.Event()
        self._tray_icon: pystray.Icon | None = None

        self._build_ui()
        self._load_config_to_ui()
        self._setup_tray()

        # 拦截右上角关闭按钮：隐藏窗口，保留托盘
        self.root.protocol("WM_DELETE_WINDOW", self._hide_to_tray)

    # ---------- UI ----------
    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=16)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="楼栋", font=("Microsoft YaHei", 10)).grid(
            row=0, column=0, sticky="w", pady=4
        )
        self.ent_building = ttk.Entry(frm, width=12)
        self.ent_building.grid(row=0, column=1, pady=4)

        ttk.Label(frm, text="房间号", font=("Microsoft YaHei", 10)).grid(
            row=1, column=0, sticky="w", pady=4
        )
        self.ent_room = ttk.Entry(frm, width=12)
        self.ent_room.grid(row=1, column=1, pady=4)

        ttk.Label(frm, text="低电量阈值(度)", font=("Microsoft YaHei", 10)).grid(
            row=2, column=0, sticky="w", pady=4
        )
        self.ent_threshold = ttk.Entry(frm, width=12)
        self.ent_threshold.grid(row=2, column=1, pady=4)

        ttk.Label(frm, text="检查间隔(分钟)", font=("Microsoft YaHei", 10)).grid(
            row=3, column=0, sticky="w", pady=4
        )
        self.ent_interval = ttk.Entry(frm, width=12)
        self.ent_interval.grid(row=3, column=1, pady=4)

        btn_save = ttk.Button(frm, text="保存配置", command=self._save)
        btn_save.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        self.power = ttk.Label(
            frm, text="点击「开始监控」查询电量", font=("Microsoft YaHei", 11)
        )
        self.power.grid(row=5, column=0, columnspan=2, pady=8)

        btn_start = ttk.Button(frm, text="开始监控", command=self._start)
        btn_start.grid(row=6, column=0, pady=10, sticky="e", padx=(0, 6))

        btn_stop = ttk.Button(frm, text="停止监控", command=self._stop_monitor)
        btn_stop.grid(row=6, column=1, pady=10, sticky="w", padx=(6, 0))

    def _load_config_to_ui(self):
        self.ent_building.insert(0, str(self.config["dorm_building"]))
        self.ent_room.insert(0, str(self.config["dorm_room"]))
        self.ent_threshold.insert(0, str(self.config["low_power_threshold"]))
        self.ent_interval.insert(0, str(self.config["check_interval_minutes"]))

    # ---------- 配置 ----------
    def _save(self):
        try:
            self.config["dorm_building"] = self.ent_building.get().strip()
            self.config["dorm_room"] = self.ent_room.get().strip()
            self.config["low_power_threshold"] = float(
                self.ent_threshold.get().strip()
            )
            self.config["check_interval_minutes"] = int(
                self.ent_interval.get().strip()
            )
            save_config(self.config)
            # 只在单独点「保存配置」时弹窗，开始监控时不弹
            try:
                messagebox.showinfo("提示", "配置已保存")
            except Exception:
                pass
        except ValueError as e:
            messagebox.showerror("错误", f"输入格式有误：{e}")

    def _read_ui_config(self):
        """从界面读取并校验配置，失败抛异常。"""
        self.config["dorm_building"] = self.ent_building.get().strip()
        self.config["dorm_room"] = self.ent_room.get().strip()
        self.config["low_power_threshold"] = float(
            self.ent_threshold.get().strip()
        )
        self.config["check_interval_minutes"] = int(
            self.ent_interval.get().strip()
        )
        save_config(self.config)

    # ---------- 监控 ----------
    def _start(self):
        try:
            self._read_ui_config()
        except ValueError as e:
            messagebox.showerror("错误", f"输入格式有误：{e}")
            return

        if self._monitor and self._monitor.is_alive():
            messagebox.showinfo("提示", "监控已在运行")
            return

        self._stop.clear()
        self._monitor = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor.start()
        self.power.config(text="监控已启动，正在查询...", foreground="blue")

    def _stop_monitor(self):
        self._stop.set()
        self.power.config(text="监控已停止", foreground="gray")
        send_toast("宿舍电量监控", "监控已停止")

    def _monitor_loop(self):
        threshold = self.config["low_power_threshold"]
        interval = self.config["check_interval_minutes"] * 60
        alerted = False

        while not self._stop.is_set():
            result = query_power(
                self.config["dorm_building"], self.config["dorm_room"]
            )
            self.root.after(0, self._update, result)

            if result["success"]:
                if result["remaining"] <= threshold and not alerted:
                    send_toast(
                         "宿舍电量不足",
                         f"您的宿舍 {result.get('room_name','')} 预存电量"
                         f"剩余 {result['remaining']} 度，请及时充值。",
                    )
                    alerted = True
                elif result["remaining"] > threshold:
                    alerted = False

            self._stop.wait(interval)

    def _update(self, result):
        t = datetime.now().strftime("%H:%M:%S")
        if result["success"]:
            low = result["remaining"] <= float(self.config["low_power_threshold"])
            self.power.config(
                text=(
                    f"{result.get('apart_name','')}-{result.get('room_name','')} "
                    f"剩余 {result['remaining']} 度  {t}"
                ),
                foreground="red" if low else "green",
            )
        else:
            self.power.config(text=f"{result['msg']}  {t}", foreground="red")

    # ---------- 系统托盘 ----------
    def _setup_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("显示窗口", self._show_window, default=True),
            pystray.MenuItem("停止监控", self._stop_monitor),
            pystray.MenuItem("完全退出", self._quit_app),
        )
        image = _make_icon_image()
        self._tray_icon = pystray.Icon(
            "WYU-Dorm-Power", image, "宿舍电量监控", menu
        )
        # 在独立线程启动托盘，不阻塞 Tkinter
        threading.Thread(target=self._tray_icon.run, daemon=True).start()

    def _hide_to_tray(self):
        self.root.withdraw()
        send_toast("宿舍电量监控", "已最小化到托盘，监控仍在后台运行")

    def _show_window(self, icon=None, item=None):
        if self._tray_icon:
            self._tray_icon.stop()
        self.root.after(0, self._restore_window)

    def _restore_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.root.attributes("-topmost", True)
        self.root.after(100, lambda: self.root.attributes("-topmost", False))
        self._setup_tray()

    def _quit_app(self, icon=None, item=None):
        self._stop.set()
        if self._tray_icon:
            self._tray_icon.stop()
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass
        sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = DormPowerApp(root)
    root.mainloop()