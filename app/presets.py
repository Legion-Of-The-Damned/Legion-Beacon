import os
import json
import tkinter as tk
from tkinter import Toplevel, Listbox, Button, Entry, Label, END

class PresetManager:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.presets_file = os.path.join(os.path.expanduser("~"), ".config", "LNWEL", "presets.json")
        os.makedirs(os.path.dirname(self.presets_file), exist_ok=True)

        self.window = Toplevel(self.parent)
        self.window.title("Управление пресетами")
        self.window.geometry("450x350")
        self.window.configure(bg=app.theme_bg)

        self.listbox = Listbox(
            self.window,
            bg=app.accent_dark,
            fg=app.theme_fg,
            font=("Consolas", 10),
            selectbackground=app.accent_red,
            selectforeground="white",
            highlightthickness=0
        )
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self.window, bg=app.theme_bg)
        btn_frame.pack(fill="x", padx=10, pady=5)

        def make_button(text, command, bg_color):
            btn = Button(
                btn_frame,
                text=text,
                command=command,
                bg=bg_color,
                fg="white",
                activebackground=app.button_hover,
                activeforeground="white",
                font=("Consolas", 10, "bold"),
                bd=0,
                relief="flat",
                padx=10,
                pady=5,
                cursor="hand2"
            )
            btn.pack(side="left", padx=5)
            btn.bind("<Enter>", lambda e: btn.config(bg=app.button_hover))
            btn.bind("<Leave>", lambda e: btn.config(bg=bg_color))
            return btn

        make_button("Загрузить", self.load_selected, "#2980b9")
        make_button("Сохранить как", self.save_new, "#27ae60")
        make_button("Удалить", self.delete_selected, "#c0392b")

        self.refresh_list()

    # ---------------------- Работа с файлами ----------------------
    def load_presets(self):
        if os.path.exists(self.presets_file):
            try:
                with open(self.presets_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_presets(self, presets):
        os.makedirs(os.path.dirname(self.presets_file), exist_ok=True)
        with open(self.presets_file, "w", encoding="utf-8") as f:
            json.dump(presets, f, indent=4, ensure_ascii=False)

    # ---------------------- UI ----------------------
    def refresh_list(self):
        self.listbox.delete(0, END)
        presets = self.load_presets()
        for name in presets.keys():
            self.listbox.insert(END, name)

    # ---------------------- Действия ----------------------
    def load_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            self.show_info("Выберите пресет для загрузки.")
            return
        name = self.listbox.get(sel[0])
        presets = self.load_presets()
        data = presets.get(name, {})
        self.apply_preset(data)
        self.show_info(f"Пресет '{name}' успешно загружен.")

    def save_new(self):
        self.input_window("Введите имя пресета:", self._save_new_callback)

    def _save_new_callback(self, name):
        if not name:
            self.show_info("Имя пресета не может быть пустым.")
            return
        if not name.endswith(".json"):
            name += ".json"
        presets = self.load_presets()
        presets[name] = self.collect_preset()
        self.save_presets(presets)
        self.refresh_list()
        self.show_info(f"Пресет '{name}' успешно сохранён.")

    def delete_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            self.show_info("Выберите пресет для удаления.")
            return
        name = self.listbox.get(sel[0])
        self.confirm_window(f"Удалить пресет '{name}'?", lambda: self._delete_confirmed(name))

    def _delete_confirmed(self, name):
        presets = self.load_presets()
        presets.pop(name, None)
        self.save_presets(presets)
        self.refresh_list()
        self.show_info(f"Пресет '{name}' успешно удалён.")

    # ---------------------- Сбор данных ----------------------
    def collect_preset(self):
        app = self.app
        data = {
            "url": app.url_entry.get().strip(),
            "username": app.username_entry.get().strip(),
            "avatar": app.avatar_entry.get().strip(),
            "content": app.content_text.get("1.0", "end").strip(),
            "embeds": []
        }

        for e in app.embed_entries:
            embed = {}
            for k, v in e.items():
                if k == "frame":
                    continue
                if isinstance(v, tk.Entry):
                    embed[k] = v.get().strip()
                elif isinstance(v, tk.Text):
                    embed[k] = v.get("1.0", "end").strip()
                elif isinstance(v, tk.StringVar):
                    embed[k] = v.get().strip()
                else:
                    embed[k] = str(v)
            data["embeds"].append(embed)
        return data

    def apply_preset(self, data):
        app = self.app
        app.url_entry.delete(0, "end")
        app.url_entry.insert(0, data.get("url", ""))
        app.username_entry.delete(0, "end")
        app.username_entry.insert(0, data.get("username", ""))
        app.avatar_entry.delete(0, "end")
        app.avatar_entry.insert(0, data.get("avatar", ""))
        app.content_text.delete("1.0", "end")
        app.content_text.insert("1.0", data.get("content", ""))

        for e in app.embed_entries:
            e["frame"].destroy()
        app.embed_entries.clear()

        for embed_data in data.get("embeds", []):
            app.add_embed()
            last = app.embed_entries[-1]
            for k, v in embed_data.items():
                widget = last.get(k)
                if isinstance(widget, tk.Entry):
                    widget.delete(0, "end")
                    widget.insert(0, v)
                elif isinstance(widget, tk.Text):
                    widget.delete("1.0", "end")
                    widget.insert("1.0", v)
                elif isinstance(widget, tk.StringVar):
                    widget.set(v)

    # ---------------------- Окна сообщений ----------------------
    def show_info(self, text):
        info_window = Toplevel(self.window)
        info_window.title("✅ Готово")
        info_window.configure(bg=self.app.theme_bg)
        info_window.geometry("350x100")
        info_window.resizable(False, False)

        label = Label(info_window, text=text, bg=self.app.theme_bg, fg="white", font=("Consolas", 11))
        label.pack(expand=True, pady=20)

        ok_btn = Button(
            info_window,
            text="ОК",
            command=info_window.destroy,
            bg="#27ae60",
            fg="white",
            activebackground="#2ecc71",
            font=("Consolas", 10, "bold"),
            bd=0,
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        ok_btn.pack()

    def input_window(self, prompt, callback):
        win = Toplevel(self.window)
        win.title("Введите имя")
        win.configure(bg=self.app.theme_bg)
        win.geometry("350x120")
        win.resizable(False, False)

        Label(win, text=prompt, bg=self.app.theme_bg, fg="white", font=("Consolas", 11)).pack(pady=(15,5))
        entry = Entry(win, font=("Consolas", 11))
        entry.pack(pady=5, fill="x", padx=20)

        Button(win, text="ОК", command=lambda: [callback(entry.get()), win.destroy()],
               bg="#27ae60", fg="white", font=("Consolas", 10, "bold"),
               bd=0, relief="flat", padx=10, pady=5, cursor="hand2").pack(pady=10)

    def confirm_window(self, prompt, callback):
        win = Toplevel(self.window)
        win.title("Подтверждение")
        win.configure(bg=self.app.theme_bg)
        win.geometry("350x120")
        win.resizable(False, False)

        Label(win, text=prompt, bg=self.app.theme_bg, fg="white", font=("Consolas", 11)).pack(pady=(15,5))

        btn_frame = tk.Frame(win, bg=self.app.theme_bg)
        btn_frame.pack(pady=10)

        Button(btn_frame, text="Да", command=lambda: [callback(), win.destroy()],
               bg="#27ae60", fg="white", font=("Consolas", 10, "bold"),
               bd=0, relief="flat", padx=10, pady=5, cursor="hand2").pack(side="left", padx=10)

        Button(btn_frame, text="Нет", command=win.destroy,
               bg="#c0392b", fg="white", font=("Consolas", 10, "bold"),
               bd=0, relief="flat", padx=10, pady=5, cursor="hand2").pack(side="left", padx=10)
