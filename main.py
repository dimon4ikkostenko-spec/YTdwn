import customtkinter as ctk
import yt_dlp
import threading
import webbrowser
from PIL import Image
import os
import sys
import ctypes
import time

APP_NAME = "YTdwn"
VERSION = "1.3.0"
GITHUB_XAIDPI = "https://github.com/dimon4ikkostenko-spec/xaidpi"

C_BG = "#0f0f0f"
C_SIDEBAR = "#181818"
C_ACCENT = "#ff0000"
C_GREEN = "#2ba640"
C_YELLOW = "#f1c40f"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

FFMPEG_PATH = resource_path("ffmpeg.exe")

try:
    myappid = 'kostenkodev.ytdwn.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

class DownloadItem(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, fg_color="#222222", corner_radius=10, **kwargs)
        self.pack(fill="x", pady=5, padx=5)
        
        self.icon_lbl = ctk.CTkLabel(self, text="🎵", font=("Arial", 20))
        self.icon_lbl.pack(side="left", padx=10)
        
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(side="left", fill="both", expand=True)
        
        lbl_title = ctk.CTkLabel(self.info_frame, text=title[:50], font=("Arial", 12, "bold"), anchor="w")
        lbl_title.pack(fill="x", pady=(5,0))
        
        self.progress_bar = ctk.CTkProgressBar(self.info_frame, height=8, progress_color=C_ACCENT)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=5)
        
        self.status_lbl = ctk.CTkLabel(self, text="0%", font=("Arial", 12, "bold"), width=80)
        self.status_lbl.pack(side="right", padx=10)

    def update_progress(self, val, text):
        self.progress_bar.set(val)
        self.status_lbl.configure(text=text)

    def finish(self):
        self.progress_bar.set(1)
        self.status_lbl.configure(text="✔ Готово", text_color=C_GREEN)
        
    def fail(self):
        self.status_lbl.configure(text="❌ Ошибка", text_color="red")

class YTdwnApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {VERSION}")
        self.geometry("1100x700")
        self.configure(fg_color=C_BG)
        
        try: self.iconbitmap(resource_path("logo.ico"))
        except: pass

        self.withdraw()
        self.show_splash()

        self.download_path = os.path.join(os.getcwd(), "Downloads")
        if not os.path.exists(self.download_path): os.makedirs(self.download_path)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=240, fg_color=C_SIDEBAR, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        try:
            img_logo = ctk.CTkImage(Image.open(resource_path("logo.png")), size=(50, 50))
            self.lbl_logo = ctk.CTkLabel(self.sidebar, text=f"  {APP_NAME}", image=img_logo, 
                                         compound="left", font=("Impact", 32), text_color="white")
        except:
            self.lbl_logo = ctk.CTkLabel(self.sidebar, text=APP_NAME, font=("Impact", 32), text_color="white")
        self.lbl_logo.pack(pady=(40, 30), anchor="center")

        self.btn_link = self.create_sidebar_btn("🔗  По Ссылке", self.show_link_tab, True)
        self.btn_search = self.create_sidebar_btn("🔍  Поиск (Beta)", self.show_search_tab, False)
        self.btn_downloads = self.create_sidebar_btn("⬇  Загрузки", self.show_downloads_tab, False)
        
        self.btn_folder = ctk.CTkButton(self.sidebar, text="📂 Открыть папку", fg_color="#333333", 
                                        hover_color="#444444", command=self.open_folder)
        self.btn_folder.pack(side="bottom", fill="x", padx=20, pady=20)

        self.create_xaidpi_banner()

        self.main_frame = ctk.CTkFrame(self, fg_color=C_BG)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.frame_link = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_search = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_downloads = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent", label_text="История загрузок")

        self.setup_link_ui()
        self.setup_search_ui()
        self.show_link_tab()

    def create_sidebar_btn(self, text, cmd, active=False):
        color = "#2b2b2b" if active else "transparent"
        btn = ctk.CTkButton(self.sidebar, text=text, anchor="w", fg_color=color, hover_color="#333333",
                            height=50, font=("Arial", 14, "bold"), command=cmd)
        btn.pack(fill="x", padx=10, pady=5)
        return btn

    def create_xaidpi_banner(self):
        banner = ctk.CTkFrame(self.sidebar, fg_color="#220000", border_color=C_ACCENT, border_width=2)
        banner.pack(side="bottom", fill="x", padx=15, pady=(0, 20))
        
        ctk.CTkLabel(banner, text="🚀 НЕ ГРУЗИТ?", font=("Arial", 12, "bold"), text_color="white").pack(pady=(10,5))
        ctk.CTkLabel(banner, text="Если YouTube тормозит\nкачай XAIDPI", font=("Arial", 10), text_color="#aaaaaa").pack()
        
        btn = ctk.CTkButton(banner, text="Скачать FIX", fg_color=C_ACCENT, hover_color="#cc0000", height=25,
                            command=lambda: webbrowser.open(GITHUB_XAIDPI))
        btn.pack(pady=10, padx=10, fill="x")

    def show_splash(self):
        splash = ctk.CTkToplevel(self)
        splash.overrideredirect(True)
        w, h = 450, 300
        x = (self.winfo_screenwidth()//2) - (w//2)
        y = (self.winfo_screenheight()//2) - (h//2)
        splash.geometry(f"{w}x{h}+{x}+{y}")
        splash.configure(fg_color=C_BG)
        
        try:
            img = ctk.CTkImage(Image.open(resource_path("logo.png")), size=(120, 120))
            ctk.CTkLabel(splash, text="", image=img).pack(pady=(60,20))
        except:
            ctk.CTkLabel(splash, text=APP_NAME, font=("Impact", 40)).pack(pady=80)
            
        ctk.CTkLabel(splash, text="Запуск системы...", text_color="gray").pack()
        
        pb = ctk.CTkProgressBar(splash, width=200, height=2, progress_color=C_ACCENT)
        pb.pack(pady=20)
        pb.set(0)
        
        def animate():
            for i in range(101):
                pb.set(i/100)
                splash.update()
                time.sleep(0.015)
            splash.destroy()
            self.deiconify()
            
        threading.Thread(target=animate).start()

    def reset_buttons(self):
        self.btn_link.configure(fg_color="transparent")
        self.btn_search.configure(fg_color="transparent")
        self.btn_downloads.configure(fg_color="transparent")

    def show_link_tab(self):
        self.reset_buttons()
        self.btn_link.configure(fg_color="#2b2b2b")
        self.frame_search.pack_forget()
        self.frame_downloads.pack_forget()
        self.frame_link.pack(fill="both", expand=True)

    def show_search_tab(self):
        self.reset_buttons()
        self.btn_search.configure(fg_color="#2b2b2b")
        self.frame_link.pack_forget()
        self.frame_downloads.pack_forget()
        self.frame_search.pack(fill="both", expand=True)

    def show_downloads_tab(self):
        self.reset_buttons()
        self.btn_downloads.configure(fg_color="#2b2b2b")
        self.frame_link.pack_forget()
        self.frame_search.pack_forget()
        self.frame_downloads.pack(fill="both", expand=True)

    def setup_link_ui(self):
        center_frame = ctk.CTkFrame(self.frame_link, fg_color="transparent")
        center_frame.pack(expand=True, fill="x", padx=50)

        ctk.CTkLabel(center_frame, text="Вставьте ссылку на видео", font=("Arial", 24, "bold")).pack(pady=10)
        
        rec_badge = ctk.CTkLabel(center_frame, text=" ✅ РЕКОМЕНДУЕМЫЙ СПОСОБ (СТАБИЛЬНО) ", 
                                 fg_color="#1e3a20", text_color="#4cd137", corner_radius=5)
        rec_badge.pack(pady=(0, 20))

        self.link_entry = ctk.CTkEntry(center_frame, placeholder_text="https://www.youtube.com/watch?v=...", 
                                       height=50, font=("Arial", 16), width=500, border_color="#333333")
        self.link_entry.pack(pady=10)
        
        self.btn_get_link = ctk.CTkButton(center_frame, text="СКАЧАТЬ ВИДЕО", height=50, width=200,
                                          font=("Arial", 15, "bold"), fg_color=C_ACCENT, hover_color="#cc0000",
                                          command=self.process_link)
        self.btn_get_link.pack(pady=20)
        
        info_frame = ctk.CTkFrame(self.frame_link, fg_color="#181818", corner_radius=15)
        info_frame.pack(side="bottom", fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(info_frame, text="Как это работает?", font=("Arial", 14, "bold"), text_color="white").pack(pady=10)
        ctk.CTkLabel(info_frame, text="1. Скопируй ссылку на видео в браузере.\n2. Вставь в поле выше.\n3. Нажми кнопку. Программа сама выберет лучшее качество.", 
                     text_color="gray", justify="center").pack(pady=(0, 15))

    def process_link(self):
        url = self.link_entry.get()
        if not url: return
        
        self.btn_get_link.configure(state="disabled", text="Обработка...")
        threading.Thread(target=self.download_direct, args=(url,)).start()

    def download_direct(self, url):
        self.after(0, self.show_downloads_tab)
        item = DownloadItem(self.frame_downloads, title=f"Ссылка: {url}")
        
        def hook(d):
            if d['status'] == 'downloading':
                try:
                    p = d.get('_percent_str', '0%').replace('%','')
                    import re
                    p = float(re.sub(r'\x1b\[[0-9;]*m', '', p))
                    self.after(0, lambda: item.update_progress(p/100, f"{int(p)}%"))
                except: pass
            elif d['status'] == 'finished':
                self.after(0, item.finish)

        opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [hook],
            'quiet': True,
            'nocheckcertificate': True,
            'noplaylist': True,
            'ffmpeg_location': FFMPEG_PATH,
        }
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            self.after(0, lambda: self.btn_get_link.configure(state="normal", text="СКАЧАТЬ ВИДЕО"))
        except:
            self.after(0, lambda: self.btn_get_link.configure(state="normal", text="СКАЧАТЬ ВИДЕО"))
            self.after(0, item.fail)
            self.after(0, self.show_xaidpi_alert)

    def setup_search_ui(self):
        top_frame = ctk.CTkFrame(self.frame_search, fg_color="#2b2200", corner_radius=0)
        top_frame.pack(fill="x")
        
        ctk.CTkLabel(top_frame, text="⚠ ВНИМАНИЕ: Поиск работает в BETA-режиме", 
                     text_color="#f1c40f", font=("Arial", 12, "bold")).pack(pady=10)
        
        search_bar = ctk.CTkFrame(self.frame_search, fg_color="transparent")
        search_bar.pack(fill="x", padx=20, pady=10)
        
        self.search_entry = ctk.CTkEntry(search_bar, placeholder_text="Введите запрос...", height=40)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0,10))
        
        btn = ctk.CTkButton(search_bar, text="Найти", width=100, height=40, command=self.start_search)
        btn.pack(side="right")
        
        self.search_results = ctk.CTkScrollableFrame(self.frame_search, fg_color="transparent")
        self.search_results.pack(fill="both", expand=True)
        
        self.empty_search_lbl = ctk.CTkLabel(self.search_results, text="\n\nВведите запрос выше\nи нажмите Найти", 
                                             font=("Arial", 16), text_color="gray")
        self.empty_search_lbl.pack()

    def start_search(self):
        q = self.search_entry.get()
        if not q: return
        
        for w in self.search_results.winfo_children(): w.destroy()
        ctk.CTkLabel(self.search_results, text="Поиск...").pack(pady=20)
        threading.Thread(target=self.run_search, args=(q,)).start()

    def run_search(self, q):
        try:
            with yt_dlp.YoutubeDL({'quiet':True, 'default_search':'ytsearch5', 'nocheckcertificate':True, 'noplaylist':True}) as ydl:
                info = ydl.extract_info(q, download=False)
                
            if 'entries' in info:
                self.after(0, lambda: self.render_search_res(info['entries']))
            else:
                 self.after(0, lambda: self.render_search_res([]))
        except:
             self.after(0, self.show_xaidpi_alert)

    def render_search_res(self, entries):
        for w in self.search_results.winfo_children(): w.destroy()
        
        if not entries:
            self.show_xaidpi_alert()
            return

        for vid in entries:
            f = ctk.CTkFrame(self.search_results, fg_color="#222222")
            f.pack(fill="x", pady=5, padx=10)
            
            ctk.CTkLabel(f, text=vid.get('title', 'Video'), font=("Arial", 12, "bold"), anchor="w").pack(fill="x", padx=10, pady=5)
            ctk.CTkButton(f, text="Скачать", height=25, fg_color="#333333", 
                          command=lambda v=vid: self.process_link_from_search(v['webpage_url'])).pack(padx=10, pady=5, fill="x")

    def process_link_from_search(self, url):
        self.show_link_tab()
        self.link_entry.delete(0, 'end')
        self.link_entry.insert(0, url)
        self.process_link()

    def show_xaidpi_alert(self):
        win = ctk.CTkToplevel(self)
        win.title("Ошибка сети")
        win.geometry("400x250")
        win.attributes("-topmost", True)
        
        ctk.CTkLabel(win, text="⚠ НЕ ГРУЗИТ?", text_color=C_ACCENT, font=("Arial", 20, "bold")).pack(pady=(30, 10))
        ctk.CTkLabel(win, text="YouTube блокирует соединение.\nВоспользуйтесь XAIDPI.", text_color="white", font=("Arial", 14)).pack(pady=10)
        
        ctk.CTkButton(win, text="Скачать XAIDPI FIX", fg_color=C_ACCENT, hover_color="#cc0000", width=200, height=40,
                      command=lambda: webbrowser.open(GITHUB_XAIDPI)).pack(pady=20)
    
    def open_folder(self):
        os.startfile(self.download_path)

if __name__ == "__main__":
    app = YTdwnApp()
    app.mainloop()
