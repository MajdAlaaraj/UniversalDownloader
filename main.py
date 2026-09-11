import os
import sys
import re
import threading
import subprocess
from io import BytesIO
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import requests
import yt_dlp

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = get_base_path()
    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CustomLogger:
    def __init__(self, app_instance):
        self.app = app_instance
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

class AboutDeveloperWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("عن المطور - Eng. Majd Alaaraj")
        self.geometry("420x560")
        self.resizable(False, False)
        self.grab_set()

        card_frame = ctk.CTkFrame(self, corner_radius=15, border_width=1)
        card_frame.pack(padx=20, pady=20, fill="both", expand=True)

        img_path = resource_path("developer.png")
        if os.path.exists(img_path):
            dev_pil_img = Image.open(img_path)
            dev_ctk_img = ctk.CTkImage(light_image=dev_pil_img, dark_image=dev_pil_img, size=(140, 140))
            img_label = ctk.CTkLabel(card_frame, text="", image=dev_ctk_img)
            img_label.pack(pady=(20, 10))

        name_label = ctk.CTkLabel(
            card_frame, 
            text="المهندس: مجد ياسر الأعرج\n(Eng. Majd Alaaraj)", 
            font=("Segoe UI", 16, "bold"),
            text_color="#38bdf8",
            justify="center"
        )
        name_label.pack(pady=5)

        spec_label = ctk.CTkLabel(card_frame, text="مهندس حواسيب وخبير ذكاء اصطناعي", font=("Segoe UI", 13, "bold"))
        spec_label.pack(pady=3)

        loc_label = ctk.CTkLabel(card_frame, text="📍 سورية — اللاذقية", font=("Segoe UI", 12), text_color="#9ca3af")
        loc_label.pack(pady=3)

        phone_label = ctk.CTkLabel(card_frame, text="📞 +963988008243", font=("Segoe UI", 13, "bold"), text_color="#34d399")
        phone_label.pack(pady=(10, 15))

        close_btn = ctk.CTkButton(card_frame, text="إغلاق", width=120, command=self.destroy)
        close_btn.pack(pady=(0, 15))


class VideoDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Universal Video Downloader Pro - Eng. Majd Alaaraj")
        self.geometry("780x890")
        self.resizable(False, False)

        icon_file = resource_path("app_icon.ico")
        if os.path.exists(icon_file):
            self.iconbitmap(icon_file)

        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.cookies_path = None
        self.cancel_requested = False
        self.last_clipboard_url = ""

        # --- الشريط العلوي ---
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=25, pady=(12, 5))

        self.about_btn = ctk.CTkButton(top_frame, text="المطور عن  👨‍💻", width=95, command=lambda: AboutDeveloperWindow(self), fg_color="#0284c7", hover_color="#0369a1")
        self.about_btn.pack(side="left")

        self.update_btn = ctk.CTkButton(top_frame, text="المحرك تحديث🔄", width=105, command=self.start_update_ytdlp, fg_color="#7c3aed", hover_color="#6d28d9")
        self.update_btn.pack(side="left", padx=8)

        self.theme_switch = ctk.CTkSwitch(top_frame, text="الوضع الليلي", command=self.toggle_theme)
        self.theme_switch.pack(side="left", padx=10)
        self.theme_switch.select()

        self.header_label = ctk.CTkLabel(top_frame, text="مُحمّل الوسائط الذكي المتقدم", font=("Segoe UI", 16, "bold"))
        self.header_label.pack(side="right")

        # --- حاوية إدخال الرابط ---
        url_container = ctk.CTkFrame(self, fg_color="transparent")
        url_container.pack(fill="x", padx=25, pady=(5, 0))

        url_top_bar = ctk.CTkFrame(url_container, fg_color="transparent")
        url_top_bar.pack(fill="x")

        self.auto_paste_switch = ctk.CTkSwitch(url_top_bar, text="مراقبة الحافظة التلقائية (Auto-Detect)")
        self.auto_paste_switch.pack(side="left")

        self.url_label = ctk.CTkLabel(url_top_bar, text="رابط الفيديو أو القائمة:", font=("Segoe UI", 12, "bold"))
        self.url_label.pack(side="right")

        url_input_frame = ctk.CTkFrame(url_container, fg_color="transparent")
        url_input_frame.pack(fill="x", pady=5)

        self.fetch_btn = ctk.CTkButton(url_input_frame, text="فحص 🔍", width=75, command=self.start_fetch_metadata, fg_color="#4f46e5", hover_color="#4338ca")
        self.fetch_btn.pack(side="left", padx=(0, 4))

        self.paste_btn = ctk.CTkButton(url_input_frame, text="لصق 📋", width=70, command=self.paste_from_clipboard, fg_color="#0d9488", hover_color="#0f766e")
        self.paste_btn.pack(side="left", padx=(0, 6))

        self.url_entry = ctk.CTkEntry(url_input_frame, placeholder_text="....هنا الفديو رابط ضع")
        self.url_entry.pack(side="right", fill="x", expand=True)

        self.setup_entry_context_menu()

        # --- بطاقة معاينة الفيديو ---
        self.preview_frame = ctk.CTkFrame(self, corner_radius=10)
        self.preview_frame.pack(fill="x", padx=25, pady=8)

        self.thumb_label = ctk.CTkLabel(self.preview_frame, text="المعاينة", width=150, height=85, fg_color="#27272a", corner_radius=6)
        self.thumb_label.pack(side="left", padx=10, pady=10)

        meta_info_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        meta_info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.title_label = ctk.CTkLabel(meta_info_frame, text="العنوان: الصق رابطاً واضغط فحص", font=("Segoe UI", 12, "bold"), anchor="w", wraplength=480, justify="left")
        self.title_label.pack(fill="x")

        self.duration_label = ctk.CTkLabel(meta_info_frame, text="المدة: --:-- | القناة: --", font=("Segoe UI", 11), text_color="#9ca3af", anchor="w")
        self.duration_label.pack(fill="x", pady=(4, 0))

        # --- خيارات المسار والكوكيز ---
        paths_frame = ctk.CTkFrame(self, fg_color="transparent")
        paths_frame.pack(fill="x", padx=25, pady=2)

        self.browse_btn = ctk.CTkButton(paths_frame, text="المجلد تغيير" \
        , width=90, command=self.select_folder)
        self.browse_btn.pack(side="left")

        self.cookies_btn = ctk.CTkButton(paths_frame, text="ملف Cookies 🔑", width=105, command=self.select_cookies, fg_color="#334155", hover_color="#1e293b")
        self.cookies_btn.pack(side="left", padx=8)

        self.path_label = ctk.CTkLabel(paths_frame, text=f"مسار الحفظ: {self.download_path}", font=("Segoe UI", 10), wraplength=450, anchor="e")
        self.path_label.pack(side="right")

        # --- خيارات الجودة والصيغة ---
        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.pack(fill="x", padx=25, pady=6)

        format_box = ctk.CTkFrame(options_frame, fg_color="transparent")
        format_box.pack(side="left", padx=(0, 15))

        self.format_label = ctk.CTkLabel(format_box, text="صيغة الإخراج:", font=("Segoe UI", 11, "bold"))
        self.format_label.pack(anchor="w")

        self.format_menu = ctk.CTkOptionMenu(
            format_box,
            values=["MP4 (فيديو)", "MKV (فيديو)", "WEBM (فيديو)", "MP3 (صوت فقط)", "WAV (صوت فقط)"],
            width=170,
            command=self.on_format_change
        )
        self.format_menu.set("MP4 (فيديو)")
        self.format_menu.pack(pady=2)

        res_box = ctk.CTkFrame(options_frame, fg_color="transparent")
        res_box.pack(side="left", fill="x", expand=True)

        self.res_label = ctk.CTkLabel(res_box, text="الدقة المطلوبة (360p - 1080p):", font=("Segoe UI", 11, "bold"))
        self.res_label.pack(anchor="w")

        self.res_menu = ctk.CTkOptionMenu(
            res_box, 
            values=["1080p", "720p", "480p", "360p"], 
            width=250
        )
        self.res_menu.set("1080p")
        self.res_menu.pack(pady=2)

        # --- قسم قص الفيديو واقتطاع أجزاء محددة ---
        trim_card = ctk.CTkFrame(self, corner_radius=8)
        trim_card.pack(fill="x", padx=25, pady=6)

        self.trim_checkbox = ctk.CTkCheckBox(trim_card, text="الفديو من محدد جزء قص", command=self.toggle_trim_inputs)
        self.trim_checkbox.pack(side="left", padx=12, pady=8)

        self.end_time_entry = ctk.CTkEntry(trim_card, width=75, placeholder_text="02:30", state="disabled")
        self.end_time_entry.pack(side="right", padx=(5, 12), pady=8)
        self.end_time_label = ctk.CTkLabel(trim_card, text="إلى:", font=("Segoe UI", 11))
        self.end_time_label.pack(side="right")

        self.start_time_entry = ctk.CTkEntry(trim_card, width=75, placeholder_text="00:30", state="disabled")
        self.start_time_entry.pack(side="right", padx=(5, 15), pady=8)
        self.start_time_label = ctk.CTkLabel(trim_card, text="من:", font=("Segoe UI", 11))
        self.start_time_label.pack(side="right")

        # خيار الترجمة
        self.subtitles_checkbox = ctk.CTkCheckBox(self, text="وجدت إن المحددة الترجمة تنزيل")
        self.subtitles_checkbox.pack(anchor="e", padx=30, pady=(2, 8))

        # --- أزرار التحكم ---
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(pady=10)

        self.download_btn = ctk.CTkButton(control_frame, text="بدء التحميل ⬇", command=self.start_download_thread, fg_color="#16a34a", hover_color="#15803d", font=("Segoe UI", 14, "bold"), height=40, width=180)
        self.download_btn.pack(side="left", padx=8)

        self.cancel_btn = ctk.CTkButton(control_frame, text="إلغاء ✖", command=self.request_cancel, fg_color="#dc2626", hover_color="#b91c1c", font=("Segoe UI", 14, "bold"), height=40, width=110, state="disabled")
        self.cancel_btn.pack(side="left", padx=8)

        self.open_dir_btn = ctk.CTkButton(control_frame, text="فتح المجلد 📂", command=self.open_download_directory, fg_color="#475569", hover_color="#334155", font=("Segoe UI", 12), height=40, width=120)
        self.open_dir_btn.pack(side="left", padx=8)

        # --- التقدم والحالة ---
        self.progress_bar = ctk.CTkProgressBar(self, width=720)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=4)

        self.status_label = ctk.CTkLabel(self, text="جاهز للعمل", font=("Segoe UI", 12), text_color="#9ca3af")
        self.status_label.pack(pady=2)

        self.speed_label = ctk.CTkLabel(self, text="السرعة: 0 KB/s | الحجم المحمّل: 0 MB | الوقت المتبقي: --:--", font=("Segoe UI", 11), text_color="#64748b")
        self.speed_label.pack(pady=2)

        # تشغيل مراقبة الحافظة
        self.check_clipboard_loop()

    def toggle_trim_inputs(self):
        state = "normal" if self.trim_checkbox.get() == 1 else "disabled"
        self.start_time_entry.configure(state=state)
        self.end_time_entry.configure(state=state)

    def on_format_change(self, choice):
        if "صوت فقط" in choice:
            self.res_menu.configure(state="disabled")
            self.res_label.configure(text_color="gray")
        else:
            self.res_menu.configure(state="normal")
            self.res_label.configure(text_color=["black", "white"])

    def setup_entry_context_menu(self):
        entry_widget = self.url_entry._entry
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="قص (Cut)", command=lambda: entry_widget.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="نسخ (Copy)", command=lambda: entry_widget.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="لصق (Paste)", command=self.paste_from_clipboard)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="تحديد الكل (Select All)", command=lambda: entry_widget.select_range(0, 'end'))

        entry_widget.bind("<Button-3>", lambda e: self.context_menu.tk_popup(e.x_root, e.y_root))
        entry_widget.bind("<Control-v>", lambda e: self.paste_from_clipboard())
        entry_widget.bind("<Control-V>", lambda e: self.paste_from_clipboard())
        entry_widget.bind("<Control-c>", lambda e: entry_widget.event_generate("<<Copy>>"))
        entry_widget.bind("<Control-a>", lambda e: (entry_widget.select_range(0, 'end'), "break"))

    def paste_from_clipboard(self):
        try:
            text = self.clipboard_get().strip()
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, text)
        except Exception:
            pass

    def check_clipboard_loop(self):
        if self.auto_paste_switch.get() == 1:
            try:
                clip = self.clipboard_get().strip()
                if (clip.startswith("http://") or clip.startswith("https://")) and clip != self.last_clipboard_url:
                    self.last_clipboard_url = clip
                    self.url_entry.delete(0, "end")
                    self.url_entry.insert(0, clip)
                    self.start_fetch_metadata()
            except Exception:
                pass
        self.after(1000, self.check_clipboard_loop)

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
            self.theme_switch.configure(text="الوضع الليلي")
        else:
            ctk.set_appearance_mode("Light")
            self.theme_switch.configure(text="الوضع النهاري")

    def select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.path_label.configure(text=f"مسار الحفظ: {self.download_path}")

    def select_cookies(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.cookies_path = file_path
            self.cookies_btn.configure(text="كوكيز مفعّل ✔", fg_color="#059669")
            messagebox.showinfo("تم التفعيل", "تم تحميل ملف تعريف الارتباط بنجاح.")

    def open_download_directory(self):
        if os.path.exists(self.download_path):
            if sys.platform == "win32":
                os.startfile(self.download_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.download_path])
            else:
                subprocess.Popen(["xdg-open", self.download_path])

    def request_cancel(self):
        self.cancel_requested = True
        self.status_label.configure(text="جاري إيقاف العملية...")

    def update_ytdlp_worker(self):
        self.status_label.configure(text="جاري تحديث محرك yt-dlp...")
        try:
            res = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], capture_output=True, text=True)
            if res.returncode == 0:
                self.after(0, lambda: self.status_label.configure(text="تم تحديث المحرك بنجاح."))
                messagebox.showinfo("تحديث", "تم تحديث محرك التحميل لأحدث إصدار متوافق.")
            else:
                raise Exception(res.stderr)
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text="تعذر تحديث المحرك."))
            messagebox.showerror("خطأ", f"حدث خطأ أثناء التحديث:\n{str(e)}")
        finally:
            self.after(0, lambda: self.update_btn.configure(state="normal"))

    def start_update_ytdlp(self):
        self.update_btn.configure(state="disabled")
        threading.Thread(target=self.update_ytdlp_worker, daemon=True).start()

    def update_preview_ui(self, title, duration_str, uploader, ctk_img, dynamic_options):
        self.title_label.configure(text=f"العنوان: {title}")
        self.duration_label.configure(text=f"المدة: {duration_str} | القناة: {uploader}")
        if ctk_img:
            self.thumb_label.configure(image=ctk_img, text="")
        else:
            self.thumb_label.configure(image=None, text="لا تتوفر معاينة")
            
        self.res_menu.configure(values=dynamic_options)
        self.res_menu.set(dynamic_options[0])
        self.status_label.configure(text="تم فحص الرابط وجلب البيانات بنجاح.")

    def fetch_metadata(self):
        raw_url = self.url_entry.get().strip()
        if not raw_url:
            messagebox.showwarning("تنبيه", "يرجى وضع رابط صالح أولاً.")
            self.fetch_btn.configure(state="normal")
            return

        # عزل الرابط وتجاوز القوائم لتسريع المعاينة
        url = raw_url.split('&list=')[0].split('?list=')[0] if "watch" in raw_url or "youtu.be" in raw_url else raw_url

        self.status_label.configure(text="جاري فحص الرابط وجلب البيانات...")
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'noplaylist': True,
            'extract_flat': False,
            'socket_timeout': 15
        }
        if self.cookies_path:
            ydl_opts['cookiefile'] = self.cookies_path

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            if 'entries' in info and info['entries']:
                info = info['entries'][0]

            title = info.get('title', 'غير معروف')
            duration = info.get('duration', 0)
            mins, secs = divmod(int(duration or 0), 60)
            duration_str = f"{mins:02d}:{secs:02d}"
            uploader = info.get('uploader') or info.get('channel') or 'مجهول'
            thumb_url = info.get('thumbnail')

            ctk_img = None
            if thumb_url:
                try:
                    res = requests.get(thumb_url, timeout=7, headers={"User-Agent": "Mozilla/5.0"})
                    if res.status_code == 200:
                        pil_img = Image.open(BytesIO(res.content))
                        pil_img = pil_img.resize((150, 85), Image.Resampling.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(150, 85))
                except Exception:
                    ctk_img = None

            formats = info.get('formats', [])
            heights = set()
            for f in formats:
                h = f.get('height')
                if h and isinstance(h, int) and 360 <= h <= 1080:
                    heights.add(h)

            dynamic_options = []
            if heights:
                for h in sorted(list(heights), reverse=True):
                    dynamic_options.append(f"{h}p")
            else:
                dynamic_options = ["1080p", "720p", "480p", "360p"]

            self.after(0, self.update_preview_ui, title, duration_str, uploader, ctk_img, dynamic_options)

        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text="فشل جلب المعاينة (يمكن المتابعة بالتحميل مباشرة)."))
        finally:
            self.after(0, lambda: self.fetch_btn.configure(state="normal"))

    def start_fetch_metadata(self):
        self.fetch_btn.configure(state="disabled")
        threading.Thread(target=self.fetch_metadata, daemon=True).start()

    def parse_time_seconds(self, t_str):
        parts = t_str.strip().split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return int(parts[0])

    def progress_hook(self, d):
        if self.cancel_requested:
            raise Exception("CANCEL_BY_USER")

        if d.get('status') == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)

            if total > 0:
                percent = downloaded / total
                self.progress_bar.set(percent)
                self.status_label.configure(text=f"جاري التحميل... {int(percent * 100)}%")
            else:
                self.status_label.configure(text="جاري التحميل...")

            speed = d.get('speed')
            if speed:
                speed_str = f"{speed / 1024:.1f} KB/s" if speed < 1048576 else f"{speed / 1048576:.2f} MB/s"
            else:
                speed_str = "0 KB/s"

            downloaded_mb = downloaded / (1024 * 1024)

            eta = d.get('eta')
            if eta is not None:
                try:
                    eta_val = int(eta)
                    eta_str = f"{eta_val // 60:02d}:{eta_val % 60:02d}"
                except Exception:
                    eta_str = "--:--"
            else:
                eta_str = "--:--"

            self.speed_label.configure(text=f"السرعة: {speed_str} | الحجم: {downloaded_mb:.1f} MB | المتبقي: {eta_str}")

        elif d.get('status') == 'finished':
            self.progress_bar.set(1.0)
            self.status_label.configure(text="اكتمل التنزيل، جاري المعالجة والدمج عبر FFmpeg...")
            self.speed_label.configure(text="السرعة: مكتمل | جاري الحفظ النهائي...")

    def download_worker(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("تنبيه", "يرجى وضع رابط صالح.")
            self.reset_ui_after_task()
            return

        self.cancel_requested = False
        format_choice = self.format_menu.get()
        res_choice = self.res_menu.get()

        app_dir = get_base_path()
        local_ffmpeg = os.path.join(app_dir, "ffmpeg.exe")
        meipass_ffmpeg = os.path.join(getattr(sys, '_MEIPASS', ''), "ffmpeg.exe")

        ffmpeg_target_dir = None
        if os.path.exists(local_ffmpeg):
            ffmpeg_target_dir = app_dir
        elif os.path.exists(meipass_ffmpeg):
            ffmpeg_target_dir = getattr(sys, '_MEIPASS')

        ydl_opts = {
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'logger': CustomLogger(self),
            'quiet': True,
            'no_warnings': True,
        }

        if ffmpeg_target_dir:
            ydl_opts['ffmpeg_location'] = ffmpeg_target_dir

        if self.cookies_path:
            ydl_opts['cookiefile'] = self.cookies_path

        if "صوت فقط" in format_choice:
            codec = "mp3" if "MP3" in format_choice else "wav"
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
                'preferredquality': '320',
            }]
        else:
            height = ''.join(filter(str.isdigit, res_choice))
            h_int = max(360, min(1080, int(height))) if height else 1080
            container = "mp4"
            if "MKV" in format_choice: container = "mkv"
            elif "WEBM" in format_choice: container = "webm"

            ydl_opts['format'] = f"bestvideo[height<={h_int}]+bestaudio/best[height<={h_int}]/best"
            ydl_opts['merge_output_format'] = container

        if self.trim_checkbox.get() == 1:
            try:
                start_sec = self.parse_time_seconds(self.start_time_entry.get() or "0")
                end_sec = self.parse_time_seconds(self.end_time_entry.get() or "0")
                if end_sec > start_sec:
                    ydl_opts['download_ranges'] = yt_dlp.utils.download_range_func(None, [(start_sec, end_sec)])
                    ydl_opts['force_keyframes_at_cuts'] = True
            except Exception:
                messagebox.showwarning("تنبيه", "تنسيق وقت القص غير صحيح، تم تنزيل الفيديو كاملاً.")

        if self.subtitles_checkbox.get() == 1:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = ['ar', 'en']

        try:
            self.status_label.configure(text="جاري بدء الاتصال والتحميل...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.status_label.configure(text="تم إكمال التحميل والمعالجة بنجاح!")
            messagebox.showinfo("نجاح", "تم حفظ وتجهيز الملف بالكامل.")
        except Exception as e:
            if "CANCEL_BY_USER" in str(e):
                self.status_label.configure(text="تم إلغاء العملية.")
                messagebox.showwarning("إلغاء", "تم إيقاف عملية التحميل.")
            else:
                self.status_label.configure(text="حدث خطأ أثناء التنزيل.")
                messagebox.showerror("خطأ", f"تعذر إكمال العملية:\n{str(e)}")
        finally:
            self.reset_ui_after_task()

    def reset_ui_after_task(self):
        self.download_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.speed_label.configure(text="السرعة: 0 KB/s | الحجم المحمّل: 0 MB | الوقت المتبقي: --:--")

    def start_download_thread(self):
        self.download_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        threading.Thread(target=self.download_worker, daemon=True).start()

if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()