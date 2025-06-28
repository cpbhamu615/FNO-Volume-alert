import yfinance as yf
import pandas as pd
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import threading
import time

def get_fno_stocks():
    try:
        df = pd.read_csv("my_stocks.csv")
        # ... existing code ...
    except Exception as e:
        print(f"⚠️ Error reading CSV: {e}")
        return []

fno_stocks = get_fno_stocks()

def check_and_display():
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"📅 Scan Time: {datetime.now().strftime('%H:%M:%S')}\n\n")

    volume_list = []
    low_volume_found = False
    now = datetime.now().time()

    for stock in fno_stocks:
        try:
            data = yf.download(stock, interval="5m", period="1d", progress=False)
            if len(data) < 2:
                continue
            # ... existing candle logic ...
            if is_lowest:
                low_volume_found = True
        except Exception as e:
            output_text.insert(tk.END, f"❌ Error for {stock}: {str(e)}\n")

    volume_list.sort(key=lambda x: x[1])
    for stock, vol, is_lowest in volume_list:
        line = f"{stock.ljust(15)} | Volume: {str(vol).rjust(8)}"
        if is_lowest:
            line += "  ← 📉 Lowest Today"
        output_text.insert(tk.END, line + "\n")

    # ➕ GUI में alert दिखाएँ
    if low_volume_found:
        output_text.insert(tk.END, "\n🔔 Low volume detected! 💤\n")

def auto_refresh():
    while True:
        check_and_display()
        time.sleep(300)

# GUI Setup
window = tk.Tk()
window.title("🔍 F&O Stock Volume Monitor")
window.geometry("700x500")

label = tk.Label(window, text="NSE F&O Volume Scanner", font=("Helvetica", 14, "bold"))
label.pack(pady=10)

scan_btn = tk.Button(window, text="🔄 Manual Scan", command=check_and_display,
                     bg="green", fg="white", font=("Helvetica", 12))
scan_btn.pack(pady=5)

output_text = scrolledtext.ScrolledText(window, width=80, height=20, font=("Courier", 10))
output_text.pack(pady=10)

note = tk.Label(window, text="📂 CSV: my_stocks.csv | 🔁 Auto-refresh 5 min",
                font=("Helvetica", 10, "italic"), fg="gray")
note.pack()

threading.Thread(target=auto_refresh, daemon=True).start()
window.mainloop()
