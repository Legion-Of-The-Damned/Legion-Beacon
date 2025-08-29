import tkinter as tk

# === Тема для меток ===
theme_bg = "#0b1a2e"
theme_fg = "white"
entry_bg = "#1c2a3d"
entry_fg = "white"
entry_border = "#3b5c76"

def styled_label(parent, text: str) -> tk.Label:
    """Создаёт метку с заданной темой"""
    return tk.Label(parent, text=text, bg=theme_bg, fg=theme_fg, font=("Consolas", 10, "bold"))

def enable_copy_paste(widget):
    """Добавляет горячие клавиши копирования/вставки/выделения всего текста + поиск"""
    def select_all(event):
        if isinstance(widget, tk.Text):
            widget.tag_add("sel", "1.0", "end")
        elif isinstance(widget, tk.Entry):
            widget.select_range(0, 'end')
        return "break"

    def find_text(event):
        search_window = tk.Toplevel(widget)
        search_window.title("Поиск")
        search_window.geometry("250x60")
        search_window.transient(widget.winfo_toplevel())

        tk.Label(search_window, text="Найти:").pack(side="left", padx=5)
        search_entry = tk.Entry(search_window)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_entry.focus_set()

        def do_search():
            target = search_entry.get()
            if not target:
                return
            if isinstance(widget, tk.Text):
                widget.tag_remove("search_highlight", "1.0", "end")
                start = "1.0"
                while True:
                    pos = widget.search(target, start, stopindex="end")
                    if not pos:
                        break
                    end = f"{pos}+{len(target)}c"
                    widget.tag_add("search_highlight", pos, end)
                    start = end
                widget.tag_config("search_highlight", background="yellow")
            elif isinstance(widget, tk.Entry):
                content = widget.get()
                idx = content.find(target)
                if idx != -1:
                    widget.selection_range(idx, idx+len(target))
                    widget.icursor(idx+len(target))
            search_window.destroy()

        tk.Button(search_window, text="Найти", command=do_search).pack(side="right", padx=5)

    widget.bind("<Control-c>", lambda e: widget.event_generate("<<Copy>>"))
    widget.bind("<Control-x>", lambda e: widget.event_generate("<<Cut>>"))
    widget.bind("<Control-a>", select_all)
    widget.bind("<Control-f>", find_text)
    widget.bind("<Control-v>", safe_paste)

def safe_paste(event):
    try:
        clipboard = event.widget.selection_get(selection='CLIPBOARD')
    except tk.TclError:
        return "break"  # если буфер пустой

    if isinstance(event.widget, tk.Text):
        try:
            sel_start = event.widget.index("sel.first")
            sel_end = event.widget.index("sel.last")
            event.widget.delete(sel_start, sel_end)
        except tk.TclError:
            pass
        event.widget.insert("insert", clipboard)
    elif isinstance(event.widget, tk.Entry):
        try:
            event.widget.delete("sel.first", "sel.last")
        except tk.TclError:
            pass
        event.widget.insert("insert", clipboard)

    return "break"

def attach_context_menu(widget):
    """Добавляет правое меню Копировать/Вставить/Вырезать"""
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Копировать", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Вставить", command=lambda: safe_paste(tk.Event(widget=widget)))
    menu.add_command(label="Вырезать", command=lambda: widget.event_generate("<<Cut>>"))

    def show_menu(event):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    widget.bind("<Button-3>", show_menu)
    enable_copy_paste(widget)

def create_entry(parent, bg=entry_bg, fg=entry_fg, **kwargs) -> tk.Entry:
    """Создаёт Entry с тёмной темой и контекстным меню"""
    entry = tk.Entry(
        parent,
        bg=bg,
        fg=fg,
        bd=1,
        relief="flat",
        highlightthickness=1,
        highlightbackground=entry_border,
        highlightcolor="#28a745",
        insertbackground=fg,
        **kwargs
    )
    attach_context_menu(entry)
    return entry

def create_text(parent, height=3, wrap="word", bg=entry_bg, fg=entry_fg, **kwargs) -> tk.Text:
    """Создаёт Text с тёмной темой и контекстным меню"""
    text = tk.Text(
        parent,
        height=height,
        wrap=wrap,
        bg=bg,
        fg=fg,
        bd=1,
        relief="flat",
        highlightthickness=1,
        highlightbackground=entry_border,
        highlightcolor="#28a745",
        insertbackground=fg,
        **kwargs
    )
    attach_context_menu(text)
    return text
