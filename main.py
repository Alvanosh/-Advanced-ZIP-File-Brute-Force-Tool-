import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import pyzipper  # Library for handling ZIP file encryption
import hashlib
import os
from tkinter import font as tkFont

class BruteForceTool:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 Advanced ZIP Brute Force Tool 🚀")
        self.root.geometry("600x650")
        self.root.configure(bg="#1e1e1e")  # Darker theme

        # Custom Font for Bold Text
        bold_font = tkFont.Font(family="Helvetica", size=10, weight="bold")

        # Initialize variables
        self.running = False
        self.attempts = 0
        self.start_time = None
        self.zip_file = None

        # Create GUI elements
        self.zip_label = ttk.Label(root, text="🎯 ZIP File:", background="#1e1e1e", foreground="white", font=bold_font)
        self.zip_label.pack(pady=5)

        self.zip_entry = ttk.Entry(root, width=60)
        self.zip_entry.pack(pady=5)

        self.browse_zip_button = ttk.Button(root, text="📁 Browse ZIP File", command=self.browse_zip_file)
        self.browse_zip_button.pack(pady=5)

        self.password_label = ttk.Label(root, text="🔑 Custom Password List (txt file):", background="#1e1e1e", foreground="white", font=bold_font)
        self.password_label.pack(pady=5)

        self.password_entry = ttk.Entry(root, width=60)
        self.password_entry.pack(pady=5)

        self.browse_button = ttk.Button(root, text="📁 Browse Password List", command=self.browse_file)
        self.browse_button.pack(pady=5)

        self.start_button = ttk.Button(root, text="🚀 Start Brute Force", command=self.start_brute_force)
        self.start_button.pack(pady=20)

        self.stop_button = ttk.Button(root, text="✋ Stop", command=self.stop_brute_force, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.progress_label = ttk.Label(root, text="📊 Progress:", background="#1e1e1e", foreground="white", font=bold_font)
        self.progress_label.pack(pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(pady=5, fill=tk.X)

        self.status_label = ttk.Label(root, text="📋 Status:", background="#1e1e1e", foreground="white", font=bold_font)
        self.status_label.pack(pady=5)

        self.status_text = tk.Text(root, height=10, width=60, bg="#2e2e2e", fg="white")
        self.status_text.pack(pady=5)
        self.status_text.config(state=tk.DISABLED)

        # Real-time statistics
        self.stats_label = ttk.Label(root, text="📈 Real-time Stats: 0 attempts", background="#1e1e1e", foreground="white", font=bold_font)
        self.stats_label.pack(pady=5)

        # Pause and Resume Buttons
        self.pause_button = ttk.Button(root, text="⏸ Pause", command=self.pause_brute_force, state=tk.DISABLED)
        self.pause_button.pack(pady=5)

        self.resume_button = ttk.Button(root, text="▶️ Resume", command=self.resume_brute_force, state=tk.DISABLED)
        self.resume_button.pack(pady=5)

    def browse_zip_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
        if file_path:
            self.zip_entry.delete(0, tk.END)
            self.zip_entry.insert(0, file_path)
            self.zip_file = file_path

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, file_path)

    def start_brute_force(self):
        password_file = self.password_entry.get()

        if not self.zip_file or not password_file:
            messagebox.showerror("⚠️ Input Error", "Please provide both ZIP file and password list.")
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)

        self.start_time = time.time()

        # Create a new thread for the brute force attack
        thread = threading.Thread(target=self.brute_force_attack, args=(self.zip_file, password_file))
        thread.start()

    def stop_brute_force(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.DISABLED)

    def pause_brute_force(self):
        self.running = False
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)

    def resume_brute_force(self):
        if not self.running:
            self.running = True
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)

            # Restart brute force attack in a new thread
            password_file = self.password_entry.get()
            thread = threading.Thread(target=self.brute_force_attack, args=(self.zip_file, password_file))
            thread.start()

    def brute_force_attack(self, zip_file, password_file):
        try:
            with open(password_file, "r") as file:
                passwords = file.readlines()
                total_passwords = len(passwords)

                for idx, password in enumerate(passwords):
                    if not self.running:
                        break
                    password = password.strip()

                    # Try to open the ZIP file with the current password
                    if self.try_zip_password(zip_file, password):
                        self.update_status(f"✅ Password found: {password}")
                        self.update_status("🔥 Password cracked successfully!")
                        self.stop_brute_force()
                        break

                    self.attempts += 1
                    self.update_progress(idx + 1, total_passwords)

                    # Update real-time statistics
                    self.update_stats(total_passwords)

                else:
                    self.update_status("❌ Password not found in list.")
        except Exception as e:
            self.update_status(f"⚠️ Error: {str(e)}")
            self.stop_brute_force()

    def try_zip_password(self, zip_file, password):
        try:
            with pyzipper.AESZipFile(zip_file) as zf:
                zf.pwd = password.encode()  # Set password
                zf.extractall()  # Try to extract the contents
                return True
        except (RuntimeError, pyzipper.BadZipFile, pyzipper.LargeZipFile):
            return False

    def update_progress(self, current, total):
        progress = (current / total) * 100
        self.progress_var.set(progress)
        self.root.update_idletasks()

    def update_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.config(state=tk.DISABLED)

    def update_stats(self, total_passwords):
        elapsed_time = time.time() - self.start_time
        attempts_per_second = self.attempts / elapsed_time if elapsed_time > 0 else 0
        estimated_time = (total_passwords - self.attempts) / attempts_per_second if attempts_per_second > 0 else float('inf')

        self.stats_label.config(
            text=f"📈 Real-time Stats: {self.attempts} attempts, {attempts_per_second:.2f} attempts/sec, "
                 f"⏱ Elapsed Time: {elapsed_time:.2f} sec, 🕒 Estimated Time Left: {estimated_time:.2f} sec"
        )

# Main loop
if __name__ == "__main__":
    root = tk.Tk()
    app = BruteForceTool(root)
    root.mainloop()
