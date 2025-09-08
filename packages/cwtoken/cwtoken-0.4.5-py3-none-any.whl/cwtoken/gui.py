import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from .key_manager import cwapi
from .utils import QueryWrapper
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
import json
import textwrap

class run_gui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.client = None
        self.query = None
        self.df = None
        self.title("POSTGREST data request")
        self.geometry("300x220")
        self.show_login()
    
    #------ Login -------
    
    def try_login(self):
        clubcode = self.clubcode_entry.get()
        api_token = self.token_entry.get()
        save_credentials = self.save_cred.get()
        
        try:
            self.client = cwapi(api_token, clubcode=clubcode)
            if save_credentials == 1:
                config_dir = Path.home() / ".cwtoken"
                config_dir.mkdir(exist_ok=True)
                cred_path = config_dir / "static_api.env"
                with open(cred_path, "w") as f:
                    f.write(f"CLUBCODE={self.client.clubcode}\nAPI_TOKEN={self.client.api_token}\n")

            self.show_main_app()
        except:
            messagebox.showerror("Login Failed", "Invalid clubcode or API token.")
        
        

    
    def show_login(self):
        self.title("Clubwise Login")

        tk.Label(self, text="Enter Clubcode:").pack(pady=5)
        self.clubcode_entry = tk.Entry(self)
        self.clubcode_entry.pack()
        
        tk.Label(self, text="Enter API Token:").pack(pady=5)
        self.token_entry = tk.Entry(self, show="*")
        self.token_entry.pack()
        
        self.save_cred = tk.IntVar()
        tk.Checkbutton(self, text="Save credentials?", variable=self.save_cred).pack()
        config_dir = Path.home() / ".cwtoken"
        cred_path = config_dir / "static_api.env"

        if cred_path.exists():
            try:
                with open(cred_path, 'r') as f:
                    load_dotenv(dotenv_path=cred_path)
                    clubcode = os.getenv("CLUBCODE")
                    api_token = os.getenv("API_TOKEN")

                    self.clubcode_entry.insert(0, clubcode)
                    self.token_entry.insert(0, api_token)
            except ValueError:
                print("Credential file format invalid.")

        tk.Button(self, text="Login", command=self.try_login).pack(pady=20)
    
    #------ Main page --------
    
    def show_main_app(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.minsize(600, 600)
        self.query = None

        self.geometry("800x600")
        self.title("POSTGREST data request")
        self.columnconfigure(0, weight=1)

        # --- Top Frame ---
        top_frame = tk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Welcome
        tk.Label(
            top_frame, text=f"Welcome! Clubcode: {self.client.clubcode}", font=("Arial", 14)
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        # Description
        desc_text = (
            "Use the Query Constructor to build and manage your queries: \n\n"
            "1. Add the table you want to query, then press Add.\n"
            "2. Add columns, filters, orders, or limits, pressing Add after each entry.\n"
            "3. Save or load queries at any time to reuse them later.\n"
            "4. Press Run Query to fetch results.\n"
            "5. Save results directly from the results page for future use.\n"
            "6. Generate standalone Python scripts to run your queries outside the app.\n\n"
            "You can also switch to Full URL mode to enter a complete endpoint URL directly."
        )
        tk.Label(top_frame, text=desc_text, justify="left", wraplength=600).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5,10))

        # Query type radio buttons
        self.query_type = tk.IntVar(value=1)  # default to constructor
        
        # Options buttons row
        options_frame = tk.Frame(top_frame)
        options_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        tk.Button(options_frame, text="Save query", command=self.save_query).pack(side="left")
        tk.Button(options_frame, text="Load query", command=self.load_update).pack(side="left", padx=10)
        
        # Constructor and Full URL frames
        self.constructor_frame = tk.Frame(self)
        self.constructor_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.url_frame = tk.Frame(self)
        self.url_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        tk.Label(self.url_frame, text="Full URL:").pack(side="left")
        self.url_entry = tk.Entry(self.url_frame)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(self.url_frame, text="Add", command=self.start_raw_query).pack(side="left", padx=5)
        
        self.url_frame.grid_remove()  # hide by default

        tk.Radiobutton(top_frame, text="Query constructor", variable=self.query_type, value=1,
                       command=self.switch_query_type).grid(row=3, column=0, sticky="w")
        tk.Radiobutton(top_frame, text="Full URL", variable=self.query_type, value=2,
                       command=self.switch_query_type).grid(row=3, column=1, sticky="w")
        
        # --- Preview update functions ---
        self.query_preview_var = tk.StringVar(value="Query preview:")

        # Table row
        table_row = tk.Frame(self.constructor_frame)
        table_row.pack(fill="x", pady=2)
        tk.Label(table_row, text="Table:").pack(side="left")
        self.table_entry = tk.Entry(table_row, width=20)
        self.table_entry.pack(side="left", padx=5)
        tk.Button(table_row, text="Add", command=self.start_query).pack(side="left", padx=5)

        # Select row
        select_row = tk.Frame(self.constructor_frame)
        select_row.pack(fill="x", pady=2)
        tk.Label(select_row, text="Select:").pack(side="left")
        self.select_entry = tk.Entry(select_row, width=50)
        self.select_entry.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(select_row, text="Add",command=self.add_select).pack(side="left", padx=5)
        tk.Button(select_row, text="Clear", command=self.clear_select).pack(side="left", padx=5)
        
        
        # Filter row
        filter_row = tk.Frame(self.constructor_frame)
        filter_row.pack(fill="x", pady=2)
        tk.Label(filter_row, text="Filter:").pack(side="left")
        self.filter_entry = tk.Entry(filter_row, width=50)
        self.filter_entry.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(filter_row, text="Add",command=self.add_filters).pack(side="left", padx=5)
        tk.Button(filter_row, text="Clear", command=self.clear_filters).pack(side="left", padx=5)
        
        # Order row
        order_row = tk.Frame(self.constructor_frame)
        order_row.pack(fill="x", pady=2)
        tk.Label(order_row, text="Order:").pack(side="left")
        self.order_column_entry = tk.Entry(order_row, width=30)
        self.order_column_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.order_dir_combo = ttk.Combobox(order_row, values=["asc", "desc"], width=10)
        self.order_dir_combo.current(0)
        self.order_dir_combo.pack(side="left", padx=5)
        
        tk.Button(order_row, text="Add", command=self.add_order).pack(side="left", padx=5)
        tk.Button(order_row, text="Clear", command=self.clear_orders).pack(side="left", padx=5)
        
        # Limit row
        limit_row = tk.Frame(self.constructor_frame)
        limit_row.pack(fill="x", pady=2)
        tk.Label(limit_row, text="Limit:").pack(side="left")
        self.limit_entry = tk.Entry(limit_row, width=20)
        self.limit_entry.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(limit_row, text="Add", command=self.add_limit).pack(side="left", padx=5)
        tk.Button(limit_row, text="Clear", command=self.clear_limit).pack(side="left", padx=5)
        
        # ------- Bottom Frame ---
        bottom_frame = tk.Frame(self)
        bottom_frame.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        tk.Label(bottom_frame, textvariable=self.query_preview_var, justify="left", wraplength=700).pack(fill="x", pady=(0,10))
        tk.Button(bottom_frame, text="Run query", command=self.run_query).pack(side="left", padx=5)
        tk.Button(bottom_frame, text="Clear query", command=self.clear_query).pack(side="left", padx=5)
    
    #----- Query helpers -------
    def add_select(self):
        try:
            self.query.select(self.select_entry.get())
            self.select_entry.delete(0, tk.END)
            self.update_preview()
        except:
            messagebox.showerror("Error", "Please enter a table before adding selects.")
            
    def add_filters(self):
        try:
            self.query.filters(self.filter_entry.get())
            self.filter_entry.delete(0, tk.END)
            self.update_preview()
        except:
            messagebox.showerror("Error", "Please enter a table before adding filters.")
    
    def add_order(self):
        try:
            col = self.order_column_entry.get()
            direction = self.order_dir_combo.get()
            direction = False if direction == "asc" else True
            if col:
                self.query.order(col, desc=direction)
                self.order_column_entry.delete(0, tk.END)
                self.update_preview()
        except:
            messagebox.showerror("Error", "Please enter a table before adding orders.")
    def add_limit(self):
        try:
            self.query.limit(self.limit_entry.get())
            self.filter_entry.delete(0, tk.END)
            self.update_preview()
        except:
            messagebox.showerror("Error", "Please enter a table before adding limits.")
    
    def switch_query_type(self):
        if self.query_type.get() == 1:
            self.constructor_frame.grid()
            self.url_frame.grid_remove()
            self.clear_query()
        else:
            self.constructor_frame.grid_remove()
            self.url_frame.grid()
            self.clear_query()
    
    def update_preview(self):
        if self.query:
            wrapped_query = QueryWrapper(self.query)
            self.query_preview_var.set("Query preview: " + wrapped_query.full_url())
        else:
            self.query_preview_var.set("Query preview:")
    
    def start_query(self):
        self.query = self.client.table(self.table_entry.get())
        self.update_preview()
        
    def start_raw_query(self):
        self.query = self.client.raw_query(self.url_entry.get())
        self.update_preview()
    
    def clear_query(self):
        self.query = None
        self.update_preview()
    
    def clear_select(self):
        if self.query:
            self.query.clear_select()
            self.update_preview()
            
    def clear_filters(self):
        if self.query:
            self.query.clear_filters()
            self.update_preview()
    
    def clear_orders(self):
        if self.query:
            self.query.clear_orders()
            self.update_preview()
    
    def clear_limit(self):
        if self.query:
            self.query.clear_limit()
            self.update_preview()
    
    #------------- Save/load ------
    
    def save_query(self):
        wrapped_query = QueryWrapper(self.query)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Query As"
        )
        if not file_path:
            return
        data = {
            "query": wrapped_query.full_url(),
            "table": wrapped_query.get_table(),
            "select": wrapped_query.get_select(),
            "filters": wrapped_query.get_filters(),
            "order": wrapped_query.get_orders(),
            "limit": wrapped_query.get_limit(),
            "query_type": self.query.query_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "club_code": self.client.clubcode,
            "last_run_at": datetime.now(timezone.utc).isoformat(),
            "load_count": 1,
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Query + metadata saved to {file_path}")

    def load_update(self):
        self.load_query()
        self.update_preview()

    def load_query(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Open query file"
        )
        if not file_path:
            return
          
        with open(file_path, 'r') as json_File:
            load_file = json.load(json_File)
        if load_file["query_type"] == "Constructor":
            if self.query_type.get() == 1:
                self.query = self.client.table(load_file["table"])
                if load_file.get("select"):
                    self.query.select(load_file.get("select"))
                if load_file.get("filters"):
                    self.query._filters = load_file.get("filters")
                if load_file.get("order"):
                    self.query.order(load_file.get("order"))
                if load_file.get("limit"):
                    self.query.limit(load_file["limit"])
            else:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, load_file["query"])
                #self.query = self.client.raw_query(load_file["query"])
        else:
            if self.query_type.get() == 2:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, load_file["query"])
                #self.query = self.client.raw_query(load_file["query"])
            else:
                messagebox.showerror("Error", "Cannot load a Raw query into constructor, please use full url mode.")
        load_file["load_count"] = load_file["load_count"] + 1
        load_file["last_run_at"] = datetime.now(timezone.utc).isoformat()
        with open(file_path, "w") as f:
            json.dump(load_file, f, indent=4)

    #------ Execution -------------
    
    def insert_keywords(self):
        today = datetime.today().date()
        keywords = {
            "today": today,
            "tomorrow": today + timedelta(days=1),
            "yesterday": today - timedelta(days=1),
            "beginning_of_month": today.replace(day=1)
        }
        if self.query.query_type == "Constructor":
            for i, f in enumerate(self.query._filters):
                self.query._filters[i] = f.format(**keywords)
        else:
            self.query.full_query = self.query.full_query.format(**keywords)

    def run_query(self):
        if not self.query:
            messagebox.showerror("Input Error", "Please enter a query URL.")
            return
        if not self.client.access_token:
            messagebox.showerror("Error", "Access token missing. Please login again.")
            return
        self.insert_keywords()
        wrapped_query = QueryWrapper(self.query)
        print(f"Running query: {wrapped_query.full_url()}")
        try:
            self.df = wrapped_query.run()
            if self.df is None:
                messagebox.showerror("Error", "Invalid query")
                return
            self.show_results()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    #--------- Results page ------
    
    def show_results(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.geometry("800x600")
        self.minsize(600, 540)
        self.title("Query Results")

        if not self.df.empty:
            container = tk.Frame(self)
            container.pack(fill="both", expand=True, padx=50, pady=10)

            display_df = tk.LabelFrame(container, text="Your query results")
            display_df.pack(fill="both", expand=True)

            table_frame = tk.Frame(display_df)
            table_frame.pack(fill="both", expand=True)

            tv1 = ttk.Treeview(table_frame)
            tv1.grid(row=0, column=0, sticky="nsew")

            # Scrollbars
            treescrolly = tk.Scrollbar(table_frame, orient="vertical", command=tv1.yview)
            treescrolly.grid(row=0, column=1, sticky="ns")

            treescrollx = tk.Scrollbar(table_frame, orient="horizontal", command=tv1.xview)
            treescrollx.grid(row=1, column=0, sticky="ew")

            # Configure scroll
            tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)

            # Make grid expandable
            table_frame.rowconfigure(0, weight=1)
            table_frame.columnconfigure(0, weight=1)
            
            tv1["columns"] = list(self.df.columns)
            tv1["show"] = "headings"
            
            for column in tv1["columns"]:
                tv1.heading(column, text=column)
                tv1.column(column, width=150, stretch=False)
            df_rows = self.df.to_numpy().tolist()
            tv1["displaycolumns"] = ()
            for row in df_rows:
                tv1.insert("", "end", values=row)
            tv1["displaycolumns"] = list(self.df.columns)
        else:
            tk.Label(self, text="Query returned no results. \n This may be because the data request matched no records. \n If you expected results, please double-check your clubcode and query settings.", font=("Arial", 14)).pack(pady=10, anchor="w", padx=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Save to CSV", command=self.save_file).pack(side="left", padx=20)
        tk.Button(button_frame, text="Generate PY file", command=self.generatepy).pack(side="left", padx=20)
        tk.Button(button_frame, text="Back to Query Creator", command=self.show_main_app).pack(side="left", padx=20)

    #------------- Export helpers ----------
    
    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save CSV As"
        )
        if not file_path:
            return
        self.df.to_csv(file_path)
        print(f"CSV saved to {file_path}")

    def generatepy(self):
        wrapped_query = QueryWrapper(self.query)
        script_content = textwrap.dedent(f"""
            from cwtoken import cwapi
            from datetime import datetime, timedelta

            today = datetime.today().date()
            keywords = {{
                "today": today,
                "tomorrow": today + timedelta(days=1),
                "yesterday": today - timedelta(days=1),
                "beginning_of_month": today.replace(day=1)
            }}

            clubcode = '{self.client.clubcode}'
            api_token = '{self.client.api_token}'
            
            client = cwapi(api_token=api_token,clubcode=clubcode)
            
            raw_request = '{wrapped_query.full_url()}'
            request = raw_request.format(**keywords)
            
            df = client.raw_query(request).fetch()
            print(df)
        """)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("py files", "*.py")],
            title="Save PY As"
        )
        if not file_path:
            return
        with open(file_path, "w") as f:
            f.write(script_content)
        print(f"PY file saved to {file_path}")


def main():
    app = run_gui()
    app.mainloop()

if __name__ == "__main__":
    main()
