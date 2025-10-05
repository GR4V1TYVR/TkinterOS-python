import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess, os, sys, time, urllib.request
from html.parser import HTMLParser

# ======================
# INITIAL SETUP
# ======================

root = tk.Tk()
root.title("TkinterOS")
root.attributes("-fullscreen", True)
root.configure(bg="#1e1e2f")

theme = tk.StringVar(value="Dark")
open_windows = []
button_widgets = []
terminal_open_count = 0  # For BSOD trigger

# ======================
# CLOCK + TASKBAR
# ======================

taskbar = tk.Frame(root, bg="#2e2e3f", height=30)
taskbar.pack(side="bottom", fill="x")
clock_label = tk.Label(taskbar, font=("Segoe UI", 10), fg="white", bg="#2e2e3f")
clock_label.pack(side="right", padx=10)

def update_clock():
    clock_label.config(text=time.strftime("%H:%M:%S"))
    root.after(1000, update_clock)
update_clock()

# ======================
# DESKTOP LAYOUT
# ======================

left_panel = tk.Frame(root, bg="#1e1e2f", width=200)
left_panel.pack(side="left", fill="y")
main_area = tk.Frame(root, bg="#1e1e2f")
main_area.pack(side="left", fill="both", expand=True)

title = tk.Label(main_area, text="Welcome to TkinterOS", font=("Segoe UI", 24, "bold"), fg="white", bg="#1e1e2f")
title.pack(pady=(40, 20))
taskbar_label = tk.Label(taskbar, text="TkinterOS Taskbar", font=("Segoe UI", 10), fg="white", bg="#2e2e3f")
taskbar_label.pack(side="left", padx=10)
window_list_frame = tk.Frame(taskbar, bg="#2e2e3f")
window_list_frame.pack(side="left", padx=10)

# ======================
# WINDOW MANAGEMENT
# ======================

def refresh_window_list():
    for widget in window_list_frame.winfo_children():
        widget.destroy()
    for title, win in open_windows:
        btn = tk.Button(window_list_frame, text=title, font=("Segoe UI", 9),
                        fg="white", bg="#2e2e3f", relief="flat",
                        command=lambda w=win: w.deiconify())
        btn.pack(side="left", padx=5)

def register_window(title, window):
    open_windows.append((title, window))
    refresh_window_list()
    def on_close():
        remove_window(window)
        window.destroy()
    window.protocol("WM_DELETE_WINDOW", on_close)

def remove_window(window):
    global open_windows
    open_windows = [(t, w) for t, w in open_windows if w != window]
    refresh_window_list()

def add_window_controls(win):
    control = tk.Frame(win, bg="gray")
    control.pack(fill="x")
    tk.Button(control, text="_", command=win.iconify, width=3).pack(side="right")
    tk.Button(control, text="🗖", command=lambda: win.state('zoomed'), width=3).pack(side="right")
    tk.Button(control, text="✖", command=lambda: [remove_window(win), win.destroy()], width=3).pack(side="right")

# ======================
# BSOD FUNCTION
# ======================

def trigger_bsod():
    bsod = tk.Toplevel(root)
    bsod.attributes("-fullscreen", True)
    bsod.configure(bg="#0000aa")
    bsod.lift()
    bsod.focus_force()
    bsod.attributes("-topmost", True)

    tk.Label(bsod, text="TkinterOS has encountered a problem and needs to restart.",
             font=("Segoe UI", 24, "bold"), fg="white", bg="#0000aa").pack(pady=(60, 10))
    tk.Label(bsod, text=(
        ":(\n\nThe issue appears to be: TERMINAL_OVERUSE_EXCEPTION\n\n"
        "You’ve opened or overloaded the Terminal too many times.\n\n"
        "Technical details:\n*** STOP: 0xTKOS0005 (TooMuchTerminal, 0x00000005, 0x00000000, 0x00000000)\n\n"
        "TkinterOS will restart automatically in 5 seconds."
    ), font=("Consolas", 12), fg="white", bg="#0000aa", justify="left").pack(padx=40, pady=20)

    def restart_system():
        root.destroy()
        python = sys.executable
        os.execl(python, python, *sys.argv)

    bsod.after(5000, restart_system)

# ======================
# APPLICATIONS
# ======================

def open_notepad():
    pad = tk.Toplevel(root)
    pad.title("Notepad")
    pad.geometry("500x400")
    pad.configure(bg="#f0f0f0")
    add_window_controls(pad)
    text_area = tk.Text(pad, wrap="word", font=("Segoe UI", 12))
    text_area.pack(expand=True, fill="both")

    def save_file():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text_area.get("1.0", tk.END))

    tk.Button(pad, text="Save", command=save_file, bg="#0078D7", fg="white").pack(fill="x")
    register_window("Notepad", pad)

def open_calculator():
    calc = tk.Toplevel(root)
    calc.title("Calculator")
    calc.geometry("300x400")
    calc.configure(bg="#f0f0f0")
    add_window_controls(calc)
    expr = tk.StringVar()

    def press(num): expr.set(expr.get() + str(num))
    def clear(): expr.set("")
    def equal():
        try:
            expr.set(str(eval(expr.get())))
        except:
            expr.set("Error")

    entry = tk.Entry(calc, textvariable=expr, font=("Segoe UI", 18), bd=5, relief="ridge", justify="right")
    entry.pack(fill="x", padx=10, pady=10)

    buttons = [
        ('7','8','9','/'),('4','5','6','*'),
        ('1','2','3','-'),('0','.','=','+')
    ]
    frame = tk.Frame(calc)
    frame.pack()
    for row in buttons:
        r = tk.Frame(frame)
        r.pack(expand=True, fill="both")
        for ch in row:
            action = lambda x=ch: equal() if x=='=' else press(x)
            tk.Button(r, text=ch, font=("Segoe UI", 14),
                      command=action, width=5, height=2).pack(side="left", expand=True, fill="both")
    tk.Button(calc, text="Clear", command=clear, bg="#d9534f", fg="white").pack(fill="x", padx=10, pady=10)
    register_window("Calculator", calc)

def open_terminal():
    global terminal_open_count
    terminal_open_count += 1
    if terminal_open_count >= 5:
        trigger_bsod()
        return

    term = tk.Toplevel(root)
    term.title("Terminal")
    term.geometry("600x400")
    term.configure(bg="black")
    add_window_controls(term)
    text = tk.Text(term, bg="black", fg="white", font=("Consolas", 12), insertbackground="white")
    text.pack(expand=True, fill="both")
    text.insert(tk.END, "TkinterOS Terminal\n> ")
    text.focus()

    def enter(event):
        line = text.get("1.0", "end-1c").split("\n")[-1][2:].strip()
        if line == "help":
            text.insert(tk.END, "\nCommands: help, echo, clear, exit \n> ")
        elif line.startswith("echo "):
            text.insert(tk.END, "\n" + line[5:] + "\n> ")
        elif line == "clear":
            text.delete("1.0", tk.END)
            text.insert(tk.END, "TkinterOS Terminal\n> ")
        elif line == "exit":
            term.destroy()
            remove_window(term)
        elif line == "system.fail_all":
            trigger_bsod()
        else:
            text.insert(tk.END, "\nUnknown command\n> ")
        text.see(tk.END)
        return "break"

    text.bind("<Return>", enter)
    register_window("Terminal", term)

def open_browser():
    browser = tk.Toplevel(root)
    browser.title("Browser")
    browser.geometry("800x600")
    browser.configure(bg="#f0f0f0")
    add_window_controls(browser)

    url = tk.StringVar(value="https://example.com")

    class Extractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text = []
            self.ignore = False
        def handle_starttag(self, t, a):
            if t in ("script", "style"): self.ignore = True
        def handle_endtag(self, t):
            if t in ("script", "style"): self.ignore = False
        def handle_data(self, d):
            if not self.ignore and d.strip(): self.text.append(d.strip())
        def get(self): return "\n".join(self.text)

    def load():
        u = url.get().strip()
        if not u.startswith("http"):
            u = "https://" + u
        url.set(u)
        try:
            html = urllib.request.urlopen(u).read().decode("utf-8", "ignore")
            p = Extractor()
            p.feed(html)
            t.delete("1.0", tk.END)
            t.insert(tk.END, p.get())
        except Exception as e:
            t.delete("1.0", tk.END)
            t.insert(tk.END, str(e))

    top = tk.Frame(browser, bg="#f0f0f0")
    top.pack(fill="x", padx=10, pady=5)
    tk.Entry(top, textvariable=url, font=("Segoe UI", 12), width=60).pack(side="left", padx=5)
    tk.Button(top, text="Go", command=load).pack(side="left")
    t = tk.Text(browser, wrap="word", font=("Consolas", 10))
    t.pack(expand=True, fill="both", padx=10, pady=10)
    register_window("Browser", browser)

def open_python_ide():
    ide = tk.Toplevel(root)
    ide.title("Python IDE")
    ide.geometry("800x600")
    ide.configure(bg="#f0f0f0")
    add_window_controls(ide)

    # Buttons frame (top)
    btn_frame = tk.Frame(ide, bg="#f0f0f0")
    btn_frame.pack(fill="x", padx=10, pady=(10, 0))

    # Frame for editor
    editor_frame = tk.Frame(ide)
    editor_frame.pack(expand=False, fill="both", padx=10, pady=(5,0))

    code_text = tk.Text(editor_frame, wrap="none", font=("Consolas", 12), height=20)
    code_text.pack(expand=False, fill="both")

    # Output label
    output_label = tk.Label(ide, text="Output:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0")
    output_label.pack(anchor="w", padx=10, pady=(5,0))

    # Output area
    output_text = tk.Text(ide, height=10, wrap="word", font=("Consolas", 12), bg="black", fg="white", insertbackground="white")
    output_text.pack(expand=False, fill="x", padx=10, pady=(0,10))

    def run_code():
        code = code_text.get("1.0", tk.END)
        output_text.delete("1.0", tk.END)
        try:
            local_ns = {}
            exec(code, {}, local_ns)
        except Exception:
            import traceback
            output_text.insert(tk.END, traceback.format_exc())

    def save_file():
        file_path = filedialog.asksaveasfilename(defaultextension=".py",
                                                 filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_text.get("1.0", tk.END))

    def open_file():
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                code_text.delete("1.0", tk.END)
                code_text.insert("1.0", f.read())

    # Buttons
    run = tk.Button(btn_frame, text="Run", command=run_code, bg="#28a745", fg="white")
    run.pack(side="left", padx=5)
    save = tk.Button(btn_frame, text="Save", command=save_file, bg="#0078D7", fg="white")
    save.pack(side="left", padx=5)
    openp = tk.Button(btn_frame, text="Open", command=open_file, bg="#ffc107", fg="black")
    openp.pack(side="left", padx=5)

    register_window("Python IDE", ide)

def open_file_explorer():
    explorer = tk.Toplevel(root)
    explorer.title("File Explorer")
    explorer.geometry("700x500")
    explorer.configure(bg="#f0f0f0")
    add_window_controls(explorer)

    path_var = tk.StringVar(value=os.getcwd())

    def update_list(path):
        listbox.delete(0, tk.END)
        try:
            for item in os.listdir(path):
                full = os.path.join(path, item)
                listbox.insert(tk.END, f"[DIR] {item}" if os.path.isdir(full) else item)
        except PermissionError:
            messagebox.showerror("Access Denied", "You do not have permission to open this folder.")

    def open_selected():
        sel = listbox.get(tk.ACTIVE)
        if not sel: return
        if sel.startswith("[DIR] "):
            new_path = os.path.join(path_var.get(), sel[6:])
            path_var.set(new_path)
            update_list(new_path)
        else:
            file_path = os.path.join(path_var.get(), sel)
            if sel.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                view = tk.Toplevel(explorer)
                view.title(sel)
                text_box = tk.Text(view, wrap="word")
                text_box.insert("1.0", text)
                text_box.pack(expand=True, fill="both")
            else:
                messagebox.showinfo("File", f"Simulated open: {file_path}")

    tk.Entry(explorer, textvariable=path_var, font=("Segoe UI", 11)).pack(fill="x", padx=10, pady=5)
    listbox = tk.Listbox(explorer, font=("Segoe UI", 11))
    listbox.pack(expand=True, fill="both", padx=10, pady=5)
    tk.Button(explorer, text="Open", command=open_selected, bg="#0078D7", fg="white").pack(pady=5)
    update_list(os.getcwd())
    register_window("File Explorer", explorer)

# ======================
# APP BUTTONS
# ======================

def create_button(label, command):
    b = tk.Button(left_panel, text=label, command=command,
                  font=("Segoe UI", 12), bg="#3a3a5a", fg="white",
                  width=18, height=2, relief="flat")
    b.pack(pady=10, padx=10, anchor="w")
    button_widgets.append(b)
    return b

apps = [
    ("📝 Notepad", open_notepad),
    ("🧮 Calculator", open_calculator),
    ("💻 Terminal", open_terminal),
    ("📁 File Explorer", open_file_explorer),
    ("🌐 Browser", open_browser),
    ("🐍 Python IDE", open_python_ide),
    ("❌ Exit", root.destroy)
]
for label, cmd in apps:
    create_button(label, cmd)

# ======================
# BOOTSCREEN
# ======================

def show_bootscreen():
    boot = tk.Toplevel(root)
    boot.title("Booting TkinterOS")
    boot.attributes("-fullscreen", True)
    boot.configure(bg="#222244")
    boot.attributes("-alpha", 1.0)
    boot.lift()
    boot.attributes("-topmost", True)
    boot.focus_force()

    tk.Label(boot, text="Welcome to TkinterOS", fg="white", bg="#222244",
             font=("Segoe UI", 40, "bold")).pack(expand=True)
    tk.Label(boot, text="Loading system...", fg="white", bg="#222244",
             font=("Segoe UI", 18)).pack(pady=20)

    def fade():
        alpha = boot.attributes("-alpha")
        if alpha > 0:
            alpha -= 0.05
            boot.attributes("-alpha", alpha)
            root.after(50, fade)
        else:
            boot.destroy()
            root.lift()
            root.attributes("-topmost", True)
            root.after(1000, lambda: root.attributes("-topmost", False))
            root.focus_force()

    root.after(3000, fade)

# ======================
# RUN
# ======================

if __name__ == "__main__":
    show_bootscreen()
    root.mainloop()
