import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
import re
import subprocess
import threading
from pathlib import Path

class NaraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NARA Pension Grabber")
        self.root.geometry("460x280")

        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Enter NARA URL or NAID:").pack(pady=(0, 5))
        self.input_entry = ttk.Entry(main_frame, width=50)
        self.input_entry.pack(pady=5)
        
        self.progress = ttk.Progressbar(main_frame, length=350, mode='determinate')
        self.progress.pack(pady=20)

        self.status_label = ttk.Label(main_frame, text="Ready.")
        self.status_label.pack()

        self.download_btn = ttk.Button(main_frame, text="Generate PDF", command=self.start_thread)
        self.download_btn.pack(pady=10)

    def extract_id(self, text):
        match = re.search(r'(\d{8,10})', text)
        return match.group(1) if match else None

    def start_thread(self):
        threading.Thread(target=self.process_nara, daemon=True).start()

    def process_nara(self):
        naid = self.extract_id(self.input_entry.get().strip())
        if not naid:
            messagebox.showerror("Error", "Invalid NAID or URL.")
            return

        self.download_btn.config(state='disabled')
        temp_dir = Path(f"temp_{naid}")
        
        try:
            self.status_label.config(text="Contacting NARA...")
            api_url = f"https://catalog.archives.gov/api/v2/records/{naid}"
            data = requests.get(api_url, timeout=15).json()

            objects = data.get('record', {}).get('digitalObjects', [])
            urls = [obj.get('accessUrl') for obj in objects if obj.get('accessUrl')]
            
            temp_dir.mkdir(exist_ok=True)
            image_files = []

            for i, url in enumerate(urls):
                self.status_label.config(text=f"Downloading page {i+1}...")
                img_path = temp_dir / f"p_{i:03d}.jpg"
                img_path.write_bytes(requests.get(url).content)
                image_files.append(str(img_path))
                self.progress['value'] = (i+1)/len(urls)*100

            pdf_name = f"NARA_{naid}.pdf"
            subprocess.run(["img2pdf"] + image_files + ["-o", pdf_name])
            
            for f in image_files: os.remove(f)
            temp_dir.rmdir()
            
            messagebox.showinfo("Success", f"Created {pdf_name}")
            subprocess.run(["xdg-open", "."])

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.download_btn.config(state='normal')
            self.progress['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = NaraApp(root)
    root.mainloop()