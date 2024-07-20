import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import psutil
import time
import threading
import datetime
import os

app_usage = {}
data_dir = r"C:\Users\basti\OneDrive\Bureau\prog\app_tracker\donnée_temps_app"

# Crée le dossier "app_tracker" s'il n'existe pas
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

def track_app_usage():
    global current_day
    while True:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_times']):
            try:
                with proc.oneshot():
                    # Get the process name and CPU times
                    process_name = proc.info['name']
                    cpu_times = proc.info['cpu_times']
                    
                    # Initialize if not present
                    if process_name not in app_usage:
                        app_usage[process_name] = 0
                    
                    # Increment by the user time (converted to minutes)
                    app_usage[process_name] += cpu_times.user / 60
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        time.sleep(1)
        check_new_day()

def check_new_day():
    global current_day
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if today != current_day:
        save_data_to_excel(current_day)
        app_usage.clear()
        current_day = today

def save_data_to_excel(day):
    df = pd.DataFrame(list(app_usage.items()), columns=['Application', 'Time (minutes)'])
    filename = os.path.join(data_dir, f"{day}.xlsx")
    df.to_excel(filename, index=False)

class AppTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Suivi des Applications")
        self.geometry("800x600")

        self.figure = plt.Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.update_chart()

    def update_chart(self):
        self.ax.clear()
        apps = [app for app, time in app_usage.items() if time > 10]
        times = [time for time in app_usage.values() if time > 10]
        self.ax.bar(apps, times)
        self.ax.set_ylabel('Temps (minutes)')
        self.ax.set_xlabel('Applications')
        self.ax.set_title('Temps passé sur chaque application (plus de 10 minutes)')
        self.canvas.draw()
        self.after(1000, self.update_chart)  # Update every second

if __name__ == "__main__":
    current_day = datetime.datetime.now().strftime("%Y-%m-%d")
    
    tracker_thread = threading.Thread(target=track_app_usage)
    tracker_thread.daemon = True
    tracker_thread.start()

    app = AppTracker()
    app.mainloop()
