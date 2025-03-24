import customtkinter as ctk
from tkinter import filedialog
from pytubefix import YouTube
from PIL import Image, ImageTk
import threading
import queue
import os
import subprocess
import random


# Colors
RED = "#ff0000"
BLUE = "#0022ff"
BLACK = "#1E1E1E"

# Essential variables
quality = None

# Path save slot
path = None
if os.path.exists("config.txt"):
    with open("config.txt", "r") as f:
        path = f.read()
else:
    with open("config.txt", "w") as f:
        path = os.path.join(os.path.expanduser("~"), "Youtube Video Downloader", "Downloaded")
        f.write(path)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Youtube Videos Downloader")
        self.geometry("800x500")
        self.resizable(False, False)
        self.output_dir = path
        os.makedirs(self.output_dir, exist_ok=True)

        # Set the theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Load the image
        self.logo_image = Image.open("logo.png")
        self.logo_image = self.logo_image.resize((50, 50), Image.BICUBIC)
        self.logo_photo = ctk.CTkImage(self.logo_image, size=(48, 48))

        # Load the icon for window interface
        self.wm_iconbitmap()
        self.icon_image = ImageTk.PhotoImage(file="logo.ico")
        self.iconphoto(False, self.icon_image)

        # Create a frame to hold the widgets
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.place(relx=0, rely=0, relwidth=1, relheight=0.15)
        self.logo_text_frame = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        self.logo_text_frame.pack(fill="both", padx=10, pady=5)
        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.place(relx=0, rely=0.2, relwidth=1, relheight=0.85)
        self.quality_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.quality_frame.place(relx=0.09, rely=0.37, relwidth=1, relheight=0.3)
        self.downloads_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.downloads_frame.place(relx=0.315, rely=0.55, relwidth=1, relheight=0.2)
        self.output_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.output_frame.place(relx=0, rely=0.75, relwidth=1, relheight=0.1)

        # Logo section
        self.logo_label = ctk.CTkLabel(self.logo_text_frame, image=self.logo_photo, text="")
        self.logo_label.pack(side="left", padx=10)

        # Title and subtitle section
        self.text_frame = ctk.CTkFrame(self.logo_text_frame, fg_color="transparent")
        self.text_frame.pack(side="left", fill="x", expand=True)

        self.title_label = ctk.CTkLabel(self.text_frame, text="Youtube video downloader", font=("Inter", 20), anchor="w")
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(self.text_frame, text="Download your favorite youtube video with ease", font=("Inter", 12), anchor="w")
        self.subtitle_label.pack(anchor="w")

        # Entry URL section
        self.label = ctk.CTkLabel(self.frame, text="🔗 Please paste the video URL inside this entry below:", font=("Inter", 14))
        self.label.pack(pady=5)
        self.entry = ctk.CTkEntry(self.frame, width=300)
        self.entry.pack(pady=5)

        # Output directory button
        self.output_dir_button = ctk.CTkButton(self.frame, text="📁 Select Output Location", command=self.select_output_dir)
        self.output_dir_button.pack(pady=10)
        self.open_folder_button = ctk.CTkButton(self.frame, text="🔎 Open Output Folder", command=lambda: os.startfile(self.output_dir))
        self.open_folder_button.pack(pady=10)

        # Quality selection section
        self.quality_label = ctk.CTkLabel(self.frame, text="Select the quality you want to download the video in:", font=("Inter", 14))
        self.quality_label.pack(padx=5)
        self.quality = ctk.StringVar(value="720p")  # Set default quality to 720p
        self.quality_radio1 = ctk.CTkRadioButton(self.quality_frame, text="AUTO", value="auto", variable=self.quality)
        self.quality_radio2 = ctk.CTkRadioButton(self.quality_frame, text="1080p", value="1080p", variable=self.quality)
        self.quality_radio3 = ctk.CTkRadioButton(self.quality_frame, text="720p", value="720p", variable=self.quality)
        self.quality_radio4 = ctk.CTkRadioButton(self.quality_frame, text="480p", value="480p", variable=self.quality)
        self.quality_radio5 = ctk.CTkRadioButton(self.quality_frame, text="360p", value="360p", variable=self.quality)
        self.quality_radio6 = ctk.CTkRadioButton(self.quality_frame, text="240p", value="240p", variable=self.quality)
        self.quality_radio7 = ctk.CTkRadioButton(self.quality_frame, text="144p", value="144p", variable=self.quality)

        self.quality_radio1.pack(side="left")
        self.quality_radio2.pack(side="left")
        self.quality_radio3.pack(side="left")
        self.quality_radio4.pack(side="left")
        self.quality_radio5.pack(side="left")
        self.quality_radio6.pack(side="left")
        self.quality_radio7.pack(side="left")

        # Download button
        self.video_button = ctk.CTkButton(self.downloads_frame, text="📼 Download as video", command=lambda: self.start_download(self.quality.get(), self.entry))
        self.video_button.pack(side="left", padx=5)
        self.audio_button = ctk.CTkButton(self.downloads_frame, text="🔉Download as audio", command=lambda: self.start_download(self.quality.get(), self.entry, True))
        self.audio_button.pack(side="left", padx=5)

        # Video output section
        self.output_label = ctk.CTkLabel(self.output_frame, text=f"Output Location: {self.output_dir}", font=("Inter", 12))
        self.output_label.place(relx=0.5, rely=0.5, anchor="center")

        # Create a queue to communicate with the GUI thread
        self.queue = queue.Queue()
        self.check_queue()

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        if self.output_dir:
            self.output_label.configure(text=f"Output Location: {self.output_dir}")
            with open("config.txt", "w") as f:
                f.write(self.output_dir)

    def check_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()
                self.output_label.configure(text=message)
        except queue.Empty:
            pass
        self.after(100, self.check_queue)

    def start_download(self, quality: str, entry: ctk.CTkEntry, is_audio: bool = False):
        threading.Thread(target=self.download, args=(quality, entry, is_audio, self.output_dir)).start()

    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = (bytes_downloaded / total_size) * 100
        self.queue.put(f"Downloading {stream.title}: {percentage_of_completion:.2f}%")

    def download(self, quality: str, entry: ctk.CTkEntry, is_audio: bool = False, output_dir: str = ""):
        self.url = entry.get()
        self.yt = YouTube(self.url, on_progress_callback=self.on_progress)
        self.queue.put(f"Downloading {self.yt.title}...")
        self.audio_button.configure(state="disabled")
        self.video_button.configure(state="disabled")

        if is_audio:
            def audio_download():
                self.stream = self.yt.streams.filter(only_audio=True).first()
                self.stream.download(output_path=output_dir)
                self.queue.put(f"Downloaded {self.yt.title} as audio (.m4a).")
            threading.Thread(target=audio_download).start()
            self.audio_button.configure(state="normal")
            self.video_button.configure(state="normal")
        else:
            if quality == "1080p":
                video_stream = self.yt.streams.filter(res="1080p", file_extension="mp4").first()
            elif quality == "720p":
                video_stream = self.yt.streams.filter(res="720p", file_extension="mp4").first()
            elif quality == "480p":
                video_stream = self.yt.streams.filter(res="480p", file_extension="mp4").first()
            elif quality == "360p":
                video_stream = self.yt.streams.filter(res="360p", file_extension="mp4").first()
            elif quality == "240p":
                video_stream = self.yt.streams.filter(res="240p", file_extension="mp4").first()
            elif quality == "144p":
                video_stream = self.yt.streams.filter(res="144p", file_extension="mp4").first()
            elif quality == "auto":
                video_stream = self.yt.streams.get_highest_resolution()
            else:
                self.queue.put("❌ Error: Invalid quality.")
                return

            audio_stream = self.yt.streams.filter(only_audio=True).first()

            temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "YoutubeVideosDownloader")
            os.makedirs(temp_dir, exist_ok=True)

            try:
                video_stream.download(output_path=temp_dir, filename="temp_video.mp4")
            except Exception as e:
                self.queue.put(f"❌ Error: Video cannot be downloaded because of unsupported quality, please try another quality")
                self.audio_button.configure(state="normal")
                self.video_button.configure(state="normal")
                return
            
            try:
                audio_stream.download(output_path=temp_dir, filename="temp_audio.m4a")
            except Exception as e:
                self.queue.put(f"❌ Error: Audio cannot be downloaded because of unsupported quality.")
                self.audio_button.configure(state="normal")
                self.video_button.configure(state="normal")
                return

            output_file = os.path.join(output_dir, f"{self.yt.title}.mp4")

            # Merge video and audio using ffmpeg
            self.queue.put(f"🏃‍♂️ Merging video and audio for {self.yt.title}...")
            command = f'ffmpeg -i "{os.path.join(temp_dir, "temp_video.mp4")}" -i "{os.path.join(temp_dir, "temp_audio.m4a")}" -c:v copy -c:a aac "{output_file}"'
            try:
                subprocess.run(command, shell=True, check=True, cwd=os.getcwd())
            except Exception as e:
                self.queue.put(f"⚠️ Merging file error!, trying to download the file as downloaded.mp4")
                random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
                output_file_with_random_suffix = os.path.join(output_dir, f"downloaded_{random_suffix}.mp4")
                subprocess.run(f'ffmpeg -i "{os.path.join(temp_dir, "temp_video.mp4")}" -i "{os.path.join(temp_dir, "temp_audio.m4a")}" -c:v copy -c:a aac "{output_file_with_random_suffix}"', shell=True, cwd=os.getcwd())
                print("Error:", e)

            # Remove the separate video and audio files
            os.remove(os.path.join(temp_dir, "temp_video.mp4"))
            os.remove(os.path.join(temp_dir, "temp_audio.m4a"))

            self.queue.put(f"✅ Downloaded {self.yt.title} in {quality} quality.")

            # Enable buttons
            self.audio_button.configure(state="normal")
            self.video_button.configure(state="normal")


if __name__ == "__main__":
    app = App()
    app.mainloop()