import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import time
from plyer import notification

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.load_settings()

        # Timer state
        self.is_running = False
        self.is_work = True
        self.remaining = self.work_duration * 60
        self.progress_max = self.remaining

        # GUI setup
        self.setup_gui()
        self.update_display()

    def setup_gui(self):
        self.time_label = tk.Label(self.root, font=('Helvetica', 48))
        self.time_label.pack(pady=20)

        self.progress = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.progress.pack(pady=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        self.start_btn = tk.Button(btn_frame, text="Start", command=self.start_timer, width=10)
        self.pause_btn = tk.Button(btn_frame, text="Pause", command=self.pause_timer, width=10, state=tk.DISABLED)
        self.reset_btn = tk.Button(btn_frame, text="Reset", command=self.reset_timer, width=10)
        self.settings_btn = tk.Button(self.root, text="Settings", command=self.show_settings)

        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        self.settings_btn.pack(pady=10)

    def load_settings(self):
        self.settings_file = os.path.expanduser("~/.pomodoro_settings.json")
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.work_duration = settings.get('work', 25)
                    self.break_duration = settings.get('break', 5)
            else:
                self.work_duration = 25
                self.break_duration = 5
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {str(e)}")
            self.work_duration = 25
            self.break_duration = 5

    def save_settings(self):
        try:
            settings = {
                'work': self.work_duration,
                'break': self.break_duration
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.run_timer()

    def pause_timer(self):
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)

    def reset_timer(self):
        self.is_running = False
        self.is_work = True
        self.remaining = self.work_duration * 60
        self.progress_max = self.remaining
        self.update_display()
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)

    def run_timer(self):
        if self.is_running:
            self.remaining -= 1
            self.update_display()

            if self.remaining <= 0:
                self.is_running = False
                self.toggle_phase()
                try:
                    notification.notify(
                        title="Time's up!",
                        message=f"Time for {'break' if self.is_work else 'work'}!",
                        timeout=10
                    )
                except Exception as e:
                    messagebox.showwarning("Notification Error", "Could not show desktop notification")
            else:
                self.root.after(1000, self.run_timer)

    def toggle_phase(self):
        self.is_work = not self.is_work
        duration = self.break_duration * 60 if self.is_work else self.work_duration * 60
        self.remaining = duration
        self.progress_max = duration
        self.update_display()
        if self.is_running:
            self.root.after(1000, self.run_timer)

    def update_display(self):
        mins, secs = divmod(self.remaining, 60)
        self.time_label.config(text=f"{mins:02d}:{secs:02d}")
        progress_value = self.progress_max - self.remaining
        self.progress['value'] = (progress_value / self.progress_max) * 100

    def show_settings(self):
        self.pause_timer()
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")

        tk.Label(settings_window, text="Work Duration (minutes):").grid(row=0, column=0, padx=10, pady=5)
        work_entry = tk.Entry(settings_window)
        work_entry.insert(0, str(self.work_duration))
        work_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(settings_window, text="Break Duration (minutes):").grid(row=1, column=0, padx=10, pady=5)
        break_entry = tk.Entry(settings_window)
        break_entry.insert(0, str(self.break_duration))
        break_entry.grid(row=1, column=1, padx=10, pady=5)

        def save_and_close():
            try:
                new_work = int(work_entry.get())
                new_break = int(break_entry.get())
                if new_work <= 0 or new_break <= 0:
                    raise ValueError
                self.work_duration = new_work
                self.break_duration = new_break
                self.save_settings()
                self.reset_timer()
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter positive integer values")

        save_btn = tk.Button(settings_window, text="Save", command=save_and_close)
        save_btn.grid(row=2, columnspan=2, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = PomodoroTimer(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application crashed: {str(e)}")
