import os
import sys
import requests
import tkinter as tk
from tkinter import messagebox, colorchooser
import json
from updater import check_for_update

# Проверка обновлений
check_for_update()

# Основной интерфейс
root = tk.Tk()
root.title("Legion Nexus Webhook Edition")
root.geometry("900x900")
root.minsize(700, 700)

# Путь к файлу с данными
data_file = "webhook_data.json"

def resource_path(relative_path):
    """Получить абсолютный путь к ресурсу, работает и в .exe, и в .py"""
    try:
        base_path = sys._MEIPASS  # PyInstaller временная папка
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Путь к иконке
icon_path = resource_path("icon.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

theme_bg = "#0b1a2e"
theme_entry = "#1c2a3d"
theme_fg = "white"
theme_button = "#3b5c76"
root.config(bg=theme_bg)

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

main_frame = tk.Frame(root, bg=theme_bg)
main_frame.grid(row=0, column=0, sticky="nsew")

canvas = tk.Canvas(main_frame, bg=theme_bg, highlightthickness=0)
scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollable_frame = tk.Frame(canvas, bg=theme_bg)
scrollable_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def resize_canvas(event):
    canvas.itemconfig(scrollable_window, width=event.width)

canvas.bind("<Configure>", resize_canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

embed_entries = []

def enable_copy_paste(widget):
    def select_all(event):
        widget.tag_add("sel", "1.0", "end") if isinstance(widget, tk.Text) else widget.select_range(0, 'end')
        return "break"

    widget.bind("<Control-c>", lambda e: widget.event_generate("<<Copy>>"))
    widget.bind("<Control-C>", lambda e: widget.event_generate("<<Copy>>"))
    widget.bind("<Control-v>", lambda e: widget.event_generate("<<Paste>>"))
    widget.bind("<Control-V>", lambda e: widget.event_generate("<<Paste>>"))
    widget.bind("<Control-x>", lambda e: widget.event_generate("<<Cut>>"))
    widget.bind("<Control-X>", lambda e: widget.event_generate("<<Cut>>"))
    widget.bind("<Control-a>", select_all)
    widget.bind("<Control-A>", select_all)

def attach_context_menu(widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Копировать", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Вставить", command=lambda: widget.event_generate("<<Paste>>"))

    def show_menu(event):
        menu.tk_popup(event.x_root, event.y_root)
    widget.bind("<Button-3>", show_menu)

    # Включаем горячие клавиши
    enable_copy_paste(widget)

# === Отправка webhook ===
def send_webhook():
    url = url_entry.get().strip()
    username = username_entry.get().strip()
    avatar_url = avatar_entry.get().strip()
    content = content_text.get("1.0", "end").strip()

    if not url:
        messagebox.showerror("Ошибка", "Пожалуйста, введите Webhook URL.")
        return

    payload = {
        "username": username if username else None,
        "avatar_url": avatar_url if avatar_url else None,
        "content": content if content else None,
        "embeds": []
    }

    for embed_data in embed_entries:
        embed = {}
        title = embed_data["title"].get().strip()
        description = embed_data["description"].get("1.0", "end").strip()
        color = embed_data["color"].get().strip()
        image_url = embed_data["image"].get().strip()
        thumb_url = embed_data["thumb"].get().strip()
        url_link = embed_data["url"].get().strip()

        if title:
            embed["title"] = title
        if description:
            embed["description"] = description
        if url_link:
            embed["url"] = url_link
        if color:
            try:
                embed["color"] = int(color.replace("#", ""), 16)
            except:
                messagebox.showwarning("Внимание", f"Неверный HEX цвет: {color}")
        if image_url:
            embed["image"] = {"url": image_url}
        if thumb_url:
            embed["thumbnail"] = {"url": thumb_url}

        if embed:
            payload["embeds"].append(embed)

    try:
        response = requests.post(url, json=payload)
        if response.status_code in [200, 204]:
            messagebox.showinfo("Успех", "Сообщение отправлено!")
        else:
            messagebox.showerror("Ошибка", f"Ошибка при отправке: {response.status_code}\n{response.text}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

# === Выбор цвета ===
def choose_color(embed_data):
    color = colorchooser.askcolor(initialcolor=embed_data["color"].get())[1]
    if color:
        embed_data["color"].delete(0, tk.END)
        embed_data["color"].insert(0, color)

# === Добавление Embed ===
def add_embed():
    frame = tk.LabelFrame(scrollable_frame, text=f"Embed {len(embed_entries)+1}", padx=5, pady=5, bg=theme_bg, fg=theme_fg)
    frame.pack(padx=10, pady=5, fill="x")
    embed_data = {}

    def styled_label(text, row):
        lbl = tk.Label(frame, text=text, bg=theme_bg, fg=theme_fg)
        lbl.grid(row=row, column=0, sticky="w")
        return lbl

    # Кнопка удаления блока
    def remove_embed():
        embed_entries.remove(embed_data)
        frame.destroy()

    # Кнопка "крестик" справа
    delete_btn = tk.Button(frame, text="❌", command=remove_embed, bg=theme_bg, fg="red", bd=0)
    delete_btn.grid(row=0, column=2, sticky="ne", padx=5)

    styled_label("Заголовок:", 0)
    embed_data["title"] = tk.Entry(frame, bg=theme_entry, fg=theme_fg, bd=0)
    embed_data["title"].grid(row=0, column=1, sticky="we", padx=5)
    attach_context_menu(embed_data["title"])

    styled_label("Описание:", 1)
    embed_data["description"] = tk.Text(frame, height=3, bg=theme_entry, fg=theme_fg, bd=0, wrap="word")
    embed_data["description"].grid(row=1, column=1, columnspan=2, sticky="we", padx=5)
    attach_context_menu(embed_data["description"])

    styled_label("Цвет (#HEX):", 2)
    embed_data["color"] = tk.Entry(frame, bg=theme_entry, fg=theme_fg, bd=0)
    embed_data["color"].insert(0, "#00ffcc")
    embed_data["color"].grid(row=2, column=1, columnspan=2, sticky="w", padx=5)
    attach_context_menu(embed_data["color"])

    # Кнопка выбора цвета (размещаем её рядом с полем ввода цвета)
    choose_color_btn = tk.Button(frame, text="Выбрать цвет", command=lambda: choose_color(embed_data), bg=theme_button, fg="white", bd=0)
    choose_color_btn.grid(row=2, column=2, padx=5, sticky="w")  # Размещаем кнопку в том же ряду, рядом с полем

    styled_label("URL изображения:", 3)
    embed_data["image"] = tk.Entry(frame, bg=theme_entry, fg=theme_fg, bd=0)
    embed_data["image"].grid(row=3, column=1, columnspan=2, sticky="we", padx=5)
    attach_context_menu(embed_data["image"])

    styled_label("URL миниатюры:", 4)
    embed_data["thumb"] = tk.Entry(frame, bg=theme_entry, fg=theme_fg, bd=0)
    embed_data["thumb"].grid(row=4, column=1, columnspan=2, sticky="we", padx=5)
    attach_context_menu(embed_data["thumb"])

    styled_label("Ссылка на заголовок (URL):", 5)
    embed_data["url"] = tk.Entry(frame, bg=theme_entry, fg=theme_fg, bd=0)
    embed_data["url"].grid(row=5, column=1, columnspan=2, sticky="we", padx=5)
    attach_context_menu(embed_data["url"])

    frame.grid_columnconfigure(1, weight=1)
    embed_entries.append(embed_data)

# === Основные поля ===
def styled_label(text):
    return tk.Label(scrollable_frame, text=text, bg=theme_bg, fg=theme_fg)

styled_label("Вебхук URL:").pack(anchor="w")
url_entry = tk.Entry(scrollable_frame, bg=theme_entry, fg=theme_fg, bd=0)
url_entry.pack(fill="x", padx=10)
attach_context_menu(url_entry)

styled_label("Имя пользователя:").pack(anchor="w")
username_entry = tk.Entry(scrollable_frame, bg=theme_entry, fg=theme_fg, bd=0)
username_entry.pack(fill="x", padx=10)
attach_context_menu(username_entry)

styled_label("URL аватара:").pack(anchor="w")
avatar_entry = tk.Entry(scrollable_frame, bg=theme_entry, fg=theme_fg, bd=0)
avatar_entry.pack(fill="x", padx=10)
attach_context_menu(avatar_entry)

styled_label("Обычное сообщение:").pack(anchor="w")
content_text = tk.Text(scrollable_frame, height=3, bg=theme_entry, fg=theme_fg, bd=0, wrap="word")
content_text.pack(fill="x", padx=10)
attach_context_menu(content_text)

button_frame = tk.Frame(scrollable_frame, bg=theme_bg)
button_frame.pack(side="bottom", fill="x", pady=20)

add_button = tk.Button(button_frame, text="Добавить Embed", command=add_embed, bg=theme_entry, fg=theme_fg, bd=0)
add_button.pack(side="left", padx=20)

# Зеленая кнопка "Отправить"
send_button = tk.Button(button_frame, text="Отправить", command=send_webhook, bg="#28a745", fg="white", height=2, bd=0)
send_button.pack(side="right", padx=20)

# Кнопка очистки
def clear_fields():
    url_entry.delete(0, tk.END)
    username_entry.delete(0, tk.END)
    avatar_entry.delete(0, tk.END)
    content_text.delete("1.0", tk.END)
    for embed_data in embed_entries:
        for key, entry in embed_data.items():
            if isinstance(entry, tk.Entry):
                entry.delete(0, tk.END)
            elif isinstance(entry, tk.Text):
                entry.delete("1.0", tk.END)

clear_button = tk.Button(button_frame, text="Очистить", command=clear_fields, bg="red", fg="white", height=2, bd=0)
clear_button.pack(side="left", padx=20)

root.mainloop()
