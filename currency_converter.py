import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

API_KEY = os.getenv("API_KEY")  # Получаем API-ключ из переменной окружения
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/" if API_KEY else None
HISTORY_FILE = "history.json"

class CurrencyConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Currency Converter")
        self.geometry("450x500")
        self.resizable(False, False)
        self.history = self.load_history()
        self.build_gui()

    def build_gui(self):
        # Заголовок
        tk.Label(self, text="Currency Converter", font=("Arial", 16, "bold")).pack(pady=10)

        # Фрейм для виджетов
        frame = tk.Frame(self)
        frame.pack(pady=10)

        # Валюты
        tk.Label(frame, text="From:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(frame, text="To:").grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.from_combo = ttk.Combobox(frame, width=10)
        self.to_combo = ttk.Combobox(frame, width=10)
        self.from_combo.grid(row=1, column=0, padx=5, pady=5)
        self.to_combo.grid(row=1, column=1, padx=5, pady=5)

        # Сумма
        tk.Label(frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(frame, width=15)
        self.amount_entry.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Кнопка
        ttk.Button(self, text="Convert", command=self.convert).pack(pady=10)

        # Результат
        self.result_label = tk.Label(self, text="", font=("Arial", 14))
        self.result_label.pack(pady=10)

        # Таблица истории
        self.tree = ttk.Treeview(self, columns=("from", "to", "amount", "result"), show="headings")
        self.tree.heading("from", text="From")
        self.tree.heading("to", text="To")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("result", text="Result")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Загрузка валют и истории
        self.populate_currencies()
        self.update_history_view()

    def populate_currencies(self):
        if not API_URL:
            messagebox.showerror("Ошибка", "API-ключ не установлен. Работает только демо-режим.")
            currencies = ["USD", "EUR", "RUB"]
        else:
            try:
                response = requests.get(f"{API_URL}/latest/USD")
                data = response.json()
                currencies = list(data["conversion_rates"].keys())
            except Exception as e:
                messagebox.showerror("Ошибка API", str(e))
                return

        self.from_combo["values"] = currencies
        self.to_combo["values"] = currencies
        self.from_combo.current(0)
        self.to_combo.current(1)

    def convert(self):
        src = self.from_combo.get()
        dest = self.to_combo.get()
        amount_str = self.amount_entry.get()

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительное число в поле суммы.")
            return

        if not API_URL:
            result = amount * 0.9  # Демо-режим
            rate = 0.9
            messagebox.showinfo("Демо-режим", "Используются фиктивные курсы.")
        else:
            try:
                response = requests.get(f"{API_URL}/pair/{src}/{dest}/{amount}")
                data = response.json()
                result = data["conversion_result"]
                rate = data["conversion_rate"]
            except Exception as e:
                messagebox.showerror("Ошибка API", str(e))
                return

        self.result_label.config(text=f"{amount} {src} = {result:.2f} {dest}")

        # Сохранение в историю
        entry = {
            "from": src,
            "to": dest,
            "amount": amount,
            "result": result,
            "rate": rate,
            "timestamp": tk.datetime.datetime.now().isoformat()
        }
        self.history.append(entry)
        self.save_history()

    def load_history(self):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_history(self):
        with open(HISTORY_FILE, "w") as f:
            json.dump(self.history, f)

    def update_history_view(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

    def on_closing(self):
      self.destroy()

if __name__ == "__main__":
    app = CurrencyConverterApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
