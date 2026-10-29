import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import yt_dlp


class App:
    def __init__(self, root):
        self.root = root
        root.title("برنامج تنزيل فيديوهات يوتيوب")
        root.geometry("640x400")
        root.resizable(False, False)

        self.folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.downloading = False

        pad = {"padx": 14, "pady": 6}

        tk.Label(root, text="رابط الفيديو أو قائمة التشغيل:",
                 font=("Arial", 11)).pack(anchor="e", **pad)
        self.url_entry = tk.Entry(root, font=("Arial", 11), justify="left")
        self.url_entry.pack(fill="x", **pad)

        row = tk.Frame(root)
        row.pack(fill="x", **pad)

        tk.Label(row, text="النوع:", font=("Arial", 11)).pack(side="right")
        self.mode = ttk.Combobox(
            row, state="readonly", width=22,
            values=["فيديو (أفضل جودة)", "فيديو 1080p", "فيديو 720p",
                    "فيديو 480p", "صوت فقط (MP3)"])
        self.mode.current(0)
        self.mode.pack(side="right", padx=8)

        folder_row = tk.Frame(root)
        folder_row.pack(fill="x", **pad)
        tk.Button(folder_row, text="اختيار المجلد",
                  command=self.choose_folder).pack(side="right")
        self.folder_label = tk.Label(folder_row, text=self.folder,
                                     font=("Arial", 9), anchor="e")
        self.folder_label.pack(side="right", padx=8)

        self.btn = tk.Button(root, text="تنزيل", font=("Arial", 13, "bold"),
                             bg="#2e7d32", fg="white", command=self.start)
        self.btn.pack(fill="x", padx=14, pady=10)

        self.progress = ttk.Progressbar(root, maximum=100)
        self.progress.pack(fill="x", **pad)

        self.status = tk.Label(root, text="جاهز", font=("Arial", 10),
                               wraplength=600)
        self.status.pack(**pad)

    def choose_folder(self):
        f = filedialog.askdirectory(initialdir=self.folder)
        if f:
            self.folder = f
            self.folder_label.config(text=f)

    def set_status(self, text):
        self.root.after(0, lambda: self.status.config(text=text))

    def set_progress(self, value):
        self.root.after(0, lambda: self.progress.config(value=value))

    def hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            done = d.get("downloaded_bytes", 0)
            if total:
                self.set_progress(done * 100 / total)
            speed = d.get("_speed_str", "").strip()
            self.set_status(f"جاري التنزيل... {speed}")
        elif d["status"] == "finished":
            self.set_progress(100)
            self.set_status("اكتمل التنزيل، جاري المعالجة...")

    def start(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("تنبيه", "الصق رابط الفيديو أولًا")
            return
        if self.downloading:
            return
        self.downloading = True
        self.btn.config(state="disabled")
        self.set_progress(0)
        threading.Thread(target=self.download, args=(url,),
                         daemon=True).start()

    def download(self, url):
        mode = self.mode.get()
        opts = {
            "outtmpl": os.path.join(self.folder, "%(title)s.%(ext)s"),
            "progress_hooks": [self.hook],
            "noplaylist": False,
            "quiet": True,
        }
        if mode == "صوت فقط (MP3)":
            opts["format"] = "bestaudio/best"
        elif mode == "فيديو 1080p":
            opts["format"] = "best[height<=1080]"
        elif mode == "فيديو 720p":
            opts["format"] = "best[height<=720]"
        elif mode == "فيديو 480p":
            opts["format"] = "best[height<=480]"
        else:
            opts["format"] = "best"

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            self.set_status("تم التنزيل بنجاح ✔")
        except Exception as e:
            self.set_status(f"حدث خطأ: {str(e)[:200]}")
        finally:
            self.downloading = False
            self.root.after(0, lambda: self.btn.config(state="normal"))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
