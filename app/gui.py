import os
import sys
import tkinter as tk
from tkinter import messagebox, colorchooser
from datetime import datetime
from .utils import create_entry, create_text, styled_label
from .presets import PresetManager
from .webhook import send_webhook_payload


class WebhookApp:
    def __init__(self, root):
        self.root = root
        self.theme_bg = "#0c0c12"
        self.theme_fg = "#e0e0e0"
        self.accent_red = "#c0392b"
        self.accent_dark = "#1a1a1a"
        self.button_hover = "#e74c3c"
        self.embed_entries = []

        self.root.configure(bg=self.theme_bg)

        # Основной интерфейс
        self.main_frame = tk.Frame(root, bg=self.theme_bg)
        self.main_frame.pack(fill="both", expand=True)

        # Скроллинг
        self.canvas = tk.Canvas(self.main_frame, bg=self.theme_bg, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.theme_bg)
        self.scrollable_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind("<Configure>", self.resize_canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Иконка
        icon_path = self.resource_path("icon.png")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        # Построение интерфейса
        self.build_gui()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def resize_canvas(self, event):
        self.canvas.itemconfig(self.scrollable_window, width=event.width)

    def build_gui(self):
        btn_style = {
            "bg": self.accent_dark,
            "fg": self.theme_fg,
            "activebackground": self.button_hover,
            "activeforeground": "white",
            "bd": 0,
            "font": ("Consolas", 10, "bold"),
            "padx": 12,
            "pady": 6,
            "relief": "flat",
            "cursor": "hand2"
        }

        def hover_effect(widget, hover_bg):
            widget.bind("<Enter>", lambda e: widget.config(bg=hover_bg))
            widget.bind("<Leave>", lambda e: widget.config(bg=btn_style["bg"]))

        # ==== Управление пресетами ====
        preset_frame = tk.LabelFrame(
            self.scrollable_frame,
            text=" ⚔️ Управление пресетами ",
            bg=self.theme_bg,
            fg=self.accent_red,
            font=("Consolas", 12, "bold"),
            padx=10,
            pady=10,
            relief="groove",
            bd=2
        )
        preset_frame.pack(fill="x", expand=True, padx=12, pady=10)

        preset_btn = tk.Button(
            preset_frame,
            text="📂 Управление пресетами",
            command=lambda: PresetManager(self.root, self),
            **btn_style
        )
        preset_btn.pack(side="left", padx=5)
        hover_effect(preset_btn, "#2980b9")

        clear_btn = tk.Button(
            preset_frame,
            text="🧹 Очистить",
            command=self.clear_all_fields,
            bg="#800000",
            fg="white",
            activebackground="#b71c1c",
            font=("Consolas", 10, "bold"),
            padx=12,
            pady=6,
            relief="flat",
            cursor="hand2"
        )
        clear_btn.pack(side="left", padx=5)

        send_btn = tk.Button(
            preset_frame,
            text="🚀 Отправить",
            command=self.send_webhook,
            bg=self.accent_red,
            fg="white",
            activebackground="#ff3333",
            activeforeground="white",
            bd=0,
            font=("Consolas", 12, "bold"),
            padx=22,
            pady=8,
            relief="flat",
            cursor="hand2"
        )
        send_btn.pack(side="right", padx=5)
        hover_effect(send_btn, "#e74c3c")

        # ==== Вебхук настройки ====
        webhook_frame = tk.LabelFrame(
            self.scrollable_frame,
            text=" 🔗 Вебхук настройки ",
            bg=self.theme_bg,
            fg=self.accent_red,
            font=("Consolas", 12, "bold"),
            padx=10,
            pady=10,
            relief="groove",
            bd=2
        )
        webhook_frame.pack(fill="x", expand=True, padx=12, pady=10)

        styled_label(webhook_frame, "Вебхук URL:").pack(anchor="w", pady=2)
        self.url_entry = create_entry(webhook_frame)
        self.url_entry.pack(fill="x", expand=True, pady=3)

        styled_label(webhook_frame, "Имя пользователя:").pack(anchor="w", pady=2)
        self.username_entry = create_entry(webhook_frame)
        self.username_entry.pack(fill="x", expand=True, pady=3)

        styled_label(webhook_frame, "URL аватара:").pack(anchor="w", pady=2)
        self.avatar_entry = create_entry(webhook_frame)
        self.avatar_entry.pack(fill="x", expand=True, pady=3)

        # ==== Сообщение ====
        message_frame = tk.LabelFrame(
            self.scrollable_frame,
            text=" 💬 Сообщение ",
            bg=self.theme_bg,
            fg=self.accent_red,
            font=("Consolas", 12, "bold"),
            padx=10,
            pady=10,
            relief="groove",
            bd=2
        )
        message_frame.pack(fill="x", expand=True, padx=12, pady=10)

        styled_label(message_frame, "Текст сообщения:").pack(anchor="w", pady=2)
        self.content_text = create_text(message_frame, height=6)
        self.content_text.pack(fill="x", expand=True, pady=4)

        # ==== Embed ====
        embed_btn = tk.Button(
            self.scrollable_frame,
            text="➕ Добавить Embed",
            command=self.add_embed,
            **btn_style
        )
        embed_btn.pack(padx=12, pady=(8, 20))
        hover_effect(embed_btn, "#8e44ad")

    def add_embed(self):
        embed_frame = tk.LabelFrame(
            self.scrollable_frame,
            text=f" 🖼️ Embed {len(self.embed_entries) + 1} ",
            bg=self.theme_bg,
            fg=self.accent_red,
            font=("Consolas", 11, "bold"),
            padx=10,
            pady=10,
            relief="ridge",
            bd=2
        )
        embed_frame.pack(fill="x", expand=True, padx=12, pady=8)

        # Заголовок Embed
        styled_label(embed_frame, "Заголовок:").pack(anchor="w", pady=2)
        title_entry = create_entry(embed_frame)
        title_entry.pack(fill="x", expand=True, pady=2)

        # Описание Embed
        styled_label(embed_frame, "Описание:").pack(anchor="w", pady=2)
        desc_text = create_text(embed_frame, height=4)
        desc_text.pack(fill="x", expand=True, pady=2)

        # Цвет Embed через colorchooser
        styled_label(embed_frame, "Цвет Embed:").pack(anchor="w", pady=2)
        color_var = tk.StringVar(master=self.root, value="#FFFFFF")

        def choose_color():
            color_code = colorchooser.askcolor(title="Выберите цвет")[1]
            if color_code:
                color_var.set(color_code)
                color_btn.config(bg=color_code)

        color_btn = tk.Button(embed_frame, text="Выбрать цвет", command=choose_color, bg=color_var.get(), fg="white")
        color_btn.pack(fill="x", expand=True, pady=2)

        # URL изображения
        styled_label(embed_frame, "URL изображения:").pack(anchor="w", pady=2)
        image_entry = create_entry(embed_frame)
        image_entry.pack(fill="x", expand=True, pady=2)

        # Footer
        styled_label(embed_frame, "Footer текст:").pack(anchor="w", pady=2)
        footer_text_entry = create_entry(embed_frame)
        footer_text_entry.pack(fill="x", expand=True, pady=2)

        styled_label(embed_frame, "URL иконки Footer:").pack(anchor="w", pady=2)
        footer_icon_entry = create_entry(embed_frame)
        footer_icon_entry.pack(fill="x", expand=True, pady=2)

        # Author
        styled_label(embed_frame, "Автор (имя):").pack(anchor="w", pady=2)
        author_name_entry = create_entry(embed_frame)
        author_name_entry.pack(fill="x", expand=True, pady=2)

        styled_label(embed_frame, "URL иконки автора:").pack(anchor="w", pady=2)
        author_icon_entry = create_entry(embed_frame)
        author_icon_entry.pack(fill="x", expand=True, pady=2)

        # URL Embed
        styled_label(embed_frame, "URL Embed:").pack(anchor="w", pady=2)
        embed_url_entry = create_entry(embed_frame)
        embed_url_entry.pack(fill="x", expand=True, pady=2)

        # Timestamp с кнопками
        styled_label(embed_frame, "Добавить Timestamp:").pack(anchor="w", pady=2)
        timestamp_var = tk.BooleanVar(master=self.root, value=False)

        def set_timestamp_true():
            timestamp_var.set(True)

        def set_timestamp_false():
            timestamp_var.set(False)

        timestamp_frame = tk.Frame(embed_frame, bg=self.theme_bg)
        timestamp_frame.pack(fill="x", expand=True, pady=2)
        btn_true = tk.Button(timestamp_frame, text="Да", command=set_timestamp_true, bg="#27ae60", fg="white")
        btn_false = tk.Button(timestamp_frame, text="Нет", command=set_timestamp_false, bg="#c0392b", fg="white")
        btn_true.pack(side="left", expand=True, fill="x", padx=2)
        btn_false.pack(side="left", expand=True, fill="x", padx=2)

        # Добавляем Embed в список
        self.embed_entries.append({
            "frame": embed_frame,
            "title": title_entry,
            "description": desc_text,
            "color": color_var,
            "image": image_entry,
            "footer_text": footer_text_entry,
            "footer_icon": footer_icon_entry,
            "author_name": author_name_entry,
            "author_icon": author_icon_entry,
            "url": embed_url_entry,
            "timestamp_var": timestamp_var
        })

    def clear_all_fields(self):
        self.content_text.delete("1.0", "end")
        self.username_entry.delete(0, "end")
        self.avatar_entry.delete(0, "end")
        self.url_entry.delete(0, "end")
        for e in self.embed_entries:
            e["frame"].destroy()
        self.embed_entries.clear()
        messagebox.showinfo("Очистка", "Все поля были очищены.")

    def send_webhook(self):
        url = self.url_entry.get().strip()
        username = self.username_entry.get().strip()
        avatar_url = self.avatar_entry.get().strip()
        content = self.content_text.get("1.0", "end").strip()
        role_ids = []
        embeds = []

        if not url:
            messagebox.showerror("Ошибка", "Введите Webhook URL.")
            return

        for e in self.embed_entries:
            embed_data = {
                "title": e["title"].get().strip(),
                "description": e["description"].get("1.0", "end").strip(),
                "color": e["color"].get(),
                "image": e["image"].get().strip(),
                "footer_text": e["footer_text"].get().strip(),
                "footer_icon": e["footer_icon"].get().strip(),
                "author_name": e["author_name"].get().strip(),
                "author_icon": e["author_icon"].get().strip(),
                "url": e["url"].get().strip()
            }

            if e["timestamp_var"].get():
                embed_data["timestamp"] = datetime.utcnow().isoformat()

            if any(embed_data.values()):
                embeds.append(embed_data)

        send_webhook_payload(url, username, avatar_url, content, role_ids, embeds)
