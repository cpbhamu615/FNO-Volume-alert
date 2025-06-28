import yfinance as yf
import pandas as pd
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import threading
import time

# ✅ 1. Load stock list from local CSV file (with uppercase safety)
def get_fno_stocks():
    try:
        df = pd.read_csv("my_stocks.csv")
        if "SYMBOL" not in df.columns:
            print("❌ 'SYMBOL' column not found in CSV.")
            return []

        stock_list = df["SYMBOL"].dropna().unique().tolist()
        nse_symbols = [symbol.strip().upper() + ".NS" for symbol in stock_list if isinstance(symbol, str)]
        return nse_symbols
    except Exception as e:
        print(f"⚠️ Error reading CSV: {e}")
        return []

# ✅ 2. Get all stocks from CSV
fno_stocks = get_fno_stocks()

# ✅ 3. Main Logic to Check Volume
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

            # ✅ Use last full candle intelligently
            if now >= datetime.strptime("15:30", "%H:%M").time():
                # Market closed, use last candle (3:25 PM)
                latest_closed_candle = data.iloc[-1]
                min_volume_today = int(data["Volume"].min())
            else:
                # Market open, avoid current building candle
                latest_closed_candle = data.iloc[-2]
                min_volume_today = int(data["Volume"][:-1].min())

            latest_volume = int(latest_closed_candle["Volume"])
            is_lowest = latest_volume == min_volume_today
            volume_list.append((stock, latest_volume, is_lowest))

            if is_lowest:
                low_volume_found = True

        except Exception as e:
            output_text.insert(tk.END, f"❌ Error for {stock}: {str(e)}\n")

    # Sort and show
    volume_list.sort(key=lambda x: x[1])

    for stock, vol, is_lowest in volume_list:
        line = f"{stock.ljust(15)} | Volume: {str(vol).rjust(8)}"
        if is_lowest:
            line += "  ← 📉 Lowest Today"
        output_text.insert(tk.END, line + "\n")

    if low_volume_found:
    pass
    return jsonify({'alert': True, 'message': 'DL!'})

# ✅ 4. Auto refresh every 5 minutes
def auto_refresh():
    while True:
        check_and_display()
        time.sleep(300)

# ✅ 5. GUI Setup
window = tk.Tk()
window.title("🔍 F&O Stock Volume Monitor (CSV Mode)")
window.geometry("700x500")

label = tk.Label(window, text="📊 NSE F&O 5-Minute Volume Scanner (from CSV)", font=("Helvetica", 14, "bold"))
label.pack(pady=10)

scan_btn = tk.Button(window, text="🔄 Manual Scan", command=check_and_display, bg="green", fg="white", font=("Helvetica", 12))
scan_btn.pack(pady=5)

output_text = scrolledtext.ScrolledText(window, width=80, height=20, font=("Courier", 10))
output_text.pack(pady=10)

note = tk.Label(window, text="📂 CSV: my_stocks.csv | 🔁 Auto-refresh 5 min | 🔔 Alerts on new low volume", font=("Helvetica", 10, "italic"), fg="gray")
note.pack()

threading.Thread(target=auto_refresh, daemon=True).start()
window.mainloop()