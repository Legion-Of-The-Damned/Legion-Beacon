#!/usr/bin/env python3
import tkinter as tk
from app.gui import WebhookApp

def main():
    root = tk.Tk()
    
    root = tk.Tk()
    root.title("Legion Of The Damned Webhook Sender")
    root.geometry("900x700")

    app = WebhookApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
