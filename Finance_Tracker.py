import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import os

# --- Configuration ---
API_KEY = "69039b2ef08c5941e17651e7"
DATA_FILE = "finance_data.json"
SETTINGS_FILE = "settings.json"
CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD"]

# --- Class 1: Transaction ---
class Transaction:
    def __init__(self, original_amount, currency, category, type_, date=None):
        self.original_amount = float(original_amount)
        self.currency = currency
        self.category = category
        self.type = type_
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            "original_amount": self.original_amount,
            "currency": self.currency,
            "category": self.category,
            "type": self.type,
            "date": self.date
        }

# --- Class 2: API Handler ---
class CurrencyConverter:
    def __init__(self):
        self.base_url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair"
        self.rates_cache = {} # Simple caching to reduce API calls

    def get_conversion_rate(self, from_curr, to_curr):
        if from_curr == to_curr:
            return 1.0
        
        # Check cache first
        pair = f"{from_curr}_{to_curr}"
        if pair in self.rates_cache:
            return self.rates_cache[pair]

        try:
            url = f"{self.base_url}/{from_curr}/{to_curr}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            rate = data['conversion_rate']
            self.rates_cache[pair] = rate
            return rate
        except Exception as e:
            print(f"API Error: {e}")
            return None

# --- Class 3: Logic Manager ---
class FinanceManager:
    def __init__(self):
        self.transactions = []
        self.home_currency = "USD" # Default
        self.load_settings()
        self.load_data()

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        self.save_data()

    def update_transaction(self, index, new_trans):
        if 0 <= index < len(self.transactions):
            self.transactions[index] = new_trans
            self.save_data()

    def delete_transaction(self, index):
        if 0 <= index < len(self.transactions):
            del self.transactions[index]
            self.save_data()

    def save_data(self):
        try:
            data = [t.to_dict() for t in self.transactions]
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        if not os.path.exists(DATA_FILE): return
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                self.transactions = [Transaction(i['original_amount'], i['currency'], i['category'], i['type'], i['date']) for i in data]
        except: pass

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump({"home_currency": self.home_currency}, f)
        except: pass

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    self.home_currency = json.load(f).get("home_currency", "USD")
            except: pass

# --- Class 4: The GUI ---
class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Global Finance Manager")
        self.root.geometry("900x650")
        
        # Initialize Logic
        self.manager = FinanceManager()
        self.converter = CurrencyConverter()

        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        # --- Top Bar: Settings ---
        top_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        top_frame.pack(fill="x")
        
        tk.Label(top_frame, text="Global Finance Tracker", font=("Helvetica", 16, "bold"), bg="#f0f0f0").pack(side="left", padx=20)
        
        # Base Currency Selector
        tk.Label(top_frame, text="Base Currency:", bg="#f0f0f0").pack(side="right", padx=5)
        self.var_home_currency = tk.StringVar(value=self.manager.home_currency)
        curr_menu = ttk.Combobox(top_frame, textvariable=self.var_home_currency, values=CURRENCIES, width=5, state="readonly")
        curr_menu.pack(side="right", padx=20)
        curr_menu.bind("<<ComboboxSelected>>", self.change_base_currency)

        # --- Main Content Area ---
        main_content = tk.Frame(self.root, padx=20, pady=10)
        main_content.pack(fill="both", expand=True)

        # 1. INPUT SECTION 
        left_frame = ttk.LabelFrame(main_content, text="Transaction Details")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Amount
        ttk.Label(left_frame, text="Amount:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_amount = ttk.Entry(left_frame)
        self.entry_amount.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Currency
        ttk.Label(left_frame, text="Currency:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.combo_currency = ttk.Combobox(left_frame, values=CURRENCIES, state="readonly")
        self.combo_currency.current(0)
        self.combo_currency.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Category
        ttk.Label(left_frame, text="Category:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.combo_category = ttk.Combobox(left_frame, values=["Food", "Transport", "Rent", "Salary", "Freelance", "Shopping", "Bills"], state="readonly")
        self.combo_category.current(0)
        self.combo_category.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Type
        ttk.Label(left_frame, text="Type:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.combo_type = ttk.Combobox(left_frame, values=["Income", "Expense"], state="readonly")
        self.combo_type.current(1) # Default Expense
        self.combo_type.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # Buttons
        btn_frame = tk.Frame(left_frame)
        btn_frame.grid(row=4, columnspan=2, pady=20)
        
        self.btn_add = ttk.Button(btn_frame, text="Add Transaction", command=self.add_transaction)
        self.btn_add.pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Show Analytics", command=self.show_chart).pack(side="left", padx=5)

        # 2. LIST SECTION 
        right_frame = ttk.LabelFrame(main_content, text="History (Double-click to Edit)")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Treeview Scrollbar
        scrollbar = ttk.Scrollbar(right_frame)
        scrollbar.pack(side="right", fill="y")

        # Treeview
        cols = ("Date", "Category", "Original", "Converted", "Type")
        self.tree = ttk.Treeview(right_frame, columns=cols, show="headings", yscrollcommand=scrollbar.set)
        
        self.tree.heading("Date", text="Date")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Original", text="Original")
        self.tree.heading("Converted", text="Value (Base)")
        self.tree.heading("Type", text="Type")

        self.tree.column("Date", width=90)
        self.tree.column("Category", width=100)
        self.tree.column("Original", width=110)
        self.tree.column("Converted", width=110)
        self.tree.column("Type", width=80)
        
        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        # Bind Double Click for Edit
        self.tree.bind("<Double-1>", self.on_double_click)

        # 3. BALANCE BAR 
        bottom_frame = tk.Frame(self.root, bg="#333", pady=10)
        bottom_frame.pack(fill="x", side="bottom")
        
        self.lbl_balance = tk.Label(bottom_frame, text="Total Balance: ...", font=("Arial", 14, "bold"), fg="white", bg="#333")
        self.lbl_balance.pack()

        # Grid Config
        main_content.columnconfigure(1, weight=1)
        main_content.rowconfigure(0, weight=1)

    # --- Logic Hook Functions ---
    def change_base_currency(self, event):
        new_curr = self.var_home_currency.get()
        self.manager.home_currency = new_curr
        self.manager.save_settings()
        self.refresh_data() # Re-calculate everything

    def add_transaction(self):
        try:
            amt = float(self.entry_amount.get())
            curr = self.combo_currency.get()
            cat = self.combo_category.get()
            typ = self.combo_type.get()
            
            t = Transaction(amt, curr, cat, typ)
            self.manager.add_transaction(t)
            
            self.entry_amount.delete(0, tk.END)
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Error", "Invalid Amount")

    def refresh_data(self):
        # Clear Tree
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        total_balance = 0
        base = self.manager.home_currency
        
        # Update Columns for new currency
        self.tree.heading("Converted", text=f"Value ({base})")

        for idx, t in enumerate(self.manager.transactions):
            # Calculate Real-Time Value
            rate = self.converter.get_conversion_rate(t.currency, base)
            if rate is None:
                val_str = "Error"
                converted_val = 0
            else:
                converted_val = t.original_amount * rate
                val_str = f"{converted_val:.2f} {base}"

            # Update Balance
            if t.type == "Income":
                total_balance += converted_val
            else:
                total_balance -= converted_val

            # Insert into Table
            orig_str = f"{t.original_amount} {t.currency}"
            self.tree.insert("", tk.END, iid=idx, values=(t.date, t.category, orig_str, val_str, t.type))

        # Update Bottom Label
        self.lbl_balance.config(text=f"Total Balance: {total_balance:.2f} {base}")

    def on_double_click(self, event):
        item_id = self.tree.selection()[0]
        idx = int(item_id)
        t = self.manager.transactions[idx]
        
        # Ask user what to do
        action = messagebox.askyesno("Edit Transaction", "Yes to Edit, No to Delete (Cancel to do nothing)")
        
        if action: # Edit
            new_amt = simpledialog.askfloat("Edit", f"New Amount (Old: {t.original_amount}):", initialvalue=t.original_amount)
            if new_amt is not None:
                t.original_amount = new_amt
                self.manager.update_transaction(idx, t)
                self.refresh_data()
        else: # Delete logic check
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this?"):
                self.manager.delete_transaction(idx)
                self.refresh_data()

    def show_chart(self):
        base = self.manager.home_currency
        expenses = {}
        
        for t in self.manager.transactions:
            if t.type == "Expense":
                rate = self.converter.get_conversion_rate(t.currency, base)
                val = t.original_amount * (rate if rate else 0)
                expenses[t.category] = expenses.get(t.category, 0) + val
        
        if not expenses:
            messagebox.showinfo("Info", "No expenses.")
            return

        plt.figure(figsize=(7, 7))
        plt.pie(list(expenses.values()), labels=list(expenses.keys()), autopct='%1.1f%%')
        plt.title(f"Expenses Breakdown ({base})")
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()