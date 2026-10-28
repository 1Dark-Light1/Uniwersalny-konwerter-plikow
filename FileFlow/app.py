"""Prosty interfejs graficzny FileFlow."""
import logging
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from converter import ConversionRequest, available_targets, execute

logging.basicConfig(filename="konwerter.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
BG = "#F3F6FB"
BLUE = "#315EFB"

class ConverterApp:
    def __init__(self, root):
        self.root = root
        root.title("FileFlow — konwerter plików")
        root.geometry("780x540")
        root.minsize(680, 480)
        root.configure(bg=BG)
        self.source = tk.StringVar()
        self.output = tk.StringVar(value=str(Path.cwd()))
        self.target = tk.StringVar()
        self.status = tk.StringVar(value="Wybierz plik do konwersji.")
        self.events = queue.Queue()
        self.setup_style()
        self.build_window()
        root.after(100, self.check_events)

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground="#172033", font=("Segoe UI", 10))
        style.configure("Heading.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Hint.TLabel", foreground="#667085", font=("Segoe UI", 9))
        style.configure("TEntry", padding=8)
        style.configure("TCombobox", padding=7)
        style.configure("TButton", padding=8, font=("Segoe UI", 9))
        style.configure("Go.TButton", background=BLUE, foreground="white",
                        padding=12, font=("Segoe UI", 10, "bold"))
        style.map("Go.TButton", background=[("active", "#2448CC")])

    def build_window(self):
        main = ttk.Frame(self.root, padding=26)
        main.pack(fill="both", expand=True)
        ttk.Label(main, text="FILEFLOW", foreground=BLUE).pack(anchor="w")
        ttk.Label(main, text="Konwerter plików", style="Heading.TLabel").pack(anchor="w", pady=(3, 4))
        ttk.Label(main, text="Wybierz plik, format i miejsce zapisu.",
                  style="Hint.TLabel").pack(anchor="w", pady=(0, 22))
        card = ttk.Frame(main, padding=20)
        card.pack(fill="both", expand=True)

        ttk.Label(card, text="Plik źródłowy").pack(anchor="w")
        row = ttk.Frame(card); row.pack(fill="x", pady=(5, 15))
        ttk.Entry(row, textvariable=self.source).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Przeglądaj", command=self.choose_source).pack(side="left", padx=(8, 0))

        ttk.Label(card, text="Format docelowy").pack(anchor="w")
        self.formats = ttk.Combobox(card, textvariable=self.target, state="readonly")
        self.formats.pack(fill="x", pady=(5, 15))

        ttk.Label(card, text="Katalog zapisu").pack(anchor="w")
        row = ttk.Frame(card); row.pack(fill="x", pady=(5, 18))
        ttk.Entry(row, textvariable=self.output).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Wybierz", command=self.choose_output).pack(side="left", padx=(8, 0))

        self.button = ttk.Button(card, text="Konwertuj plik →", style="Go.TButton", command=self.convert)
        self.button.pack(fill="x", pady=(0, 14))
        ttk.Label(card, textvariable=self.status, wraplength=650).pack(anchor="w")
        ttk.Label(main, text="Obsługiwane: CSV · JSON · TXT · DOCX · PDF",
                  style="Hint.TLabel").pack(anchor="w", pady=(12, 0))

    def choose_source(self):
        filename = filedialog.askopenfilename(
            title="Wybierz plik",
            filetypes=[("Obsługiwane pliki", "*.csv *.json *.txt *.docx *.pdf"),
                       ("Wszystkie pliki", "*.*")]
        )
        if not filename:
            return
        self.source.set(filename)
        targets = available_targets(Path(filename))
        self.formats["values"] = targets
        self.target.set(targets[0] if targets else "")
        self.status.set(f"Dostępne formaty: {', '.join(targets)}" if targets
                        else "Nie ma obsługiwanej konwersji dla tego pliku.")

    def choose_output(self):
        folder = filedialog.askdirectory(title="Wybierz katalog zapisu")
        if folder:
            self.output.set(folder)

    def convert(self):
        source = Path(self.source.get().strip())
        output = Path(self.output.get().strip())
        target = self.target.get().strip()
        if not self.source.get().strip() or not self.output.get().strip() or not target:
            messagebox.showerror("Brak danych", "Wybierz plik, format i katalog zapisu.")
            return
        if not source.is_file():
            messagebox.showerror("Błąd", "Plik źródłowy nie istnieje.")
            return
        if not output.is_dir():
            messagebox.showerror("Błąd", "Katalog zapisu nie istnieje.")
            return
        if target not in available_targets(source):
            messagebox.showerror("Błąd", "Ta konwersja nie jest obsługiwana.")
            return
        self.button.configure(state="disabled")
        self.status.set("Konwersja w toku...")
        request = ConversionRequest(source, target, output)
        threading.Thread(target=self.run_conversion, args=(request,), daemon=True).start()

    def run_conversion(self, request):
        try:
            self.events.put(("ok", str(execute(request))))
        except Exception as error:
            logging.exception("Błąd konwersji")
            self.events.put(("error", str(error)))

    def check_events(self):
        try:
            while True:
                result, message = self.events.get_nowait()
                self.button.configure(state="normal")
                if result == "ok":
                    self.status.set("Konwersja zakończona pomyślnie.")
                    messagebox.showinfo("Gotowe", f"Zapisano plik:\n{message}")
                else:
                    self.status.set("Konwersja nie powiodła się.")
                    messagebox.showerror("Błąd konwersji", message)
        except queue.Empty:
            pass
        self.root.after(100, self.check_events)

def main():
    root = tk.Tk()
    ConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
