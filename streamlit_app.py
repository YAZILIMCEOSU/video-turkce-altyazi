import os
import tempfile
import subprocess
import datetime
import time
import srt

import streamlit as st
import whisper
import yt_dlp
from deep_translator import GoogleTranslator
import imageio_ffmpeg

# 🔹 ffmpeg yolunu sisteme ekle
FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG_BIN)

# --- Başlık ---
st.title("🎬 Türkçe Altyazı Oluşturucu")
st.write("Video yükle veya YouTube linki gir → Başlat'a bas → Altyazıyı indir veya videoya göm")

# --- Temp klasörü ---
if not os.path.exists("temp"):
    os.makedirs("temp")

# --- Video kaynağı ---
option = st.radio("Video Kaynağı:", ["📤 Video Yükle", "🌐 YouTube Linki"])
video_path = None
yt_link = None

if option == "📤 Video Yükle":
    uploaded_file = st.file_uploader("Video seç (MP4, MOV, AVI, MKV)", type=["mp4", "mov", "avi", "mkv"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name
        st.success("✅ Video yüklendi.")

elif option == "🌐 YouTube Linki":
    yt_link = st.text_input("YouTube linki gir:")

# --- Başlat butonu ---
if st.button("▶️ Başlat"):
    try:
        if not video_path and not yt_link:
            st.error("🚨 Video yok veya YouTube linki girilmedi.")
        else:
            progress_text = st.empty()
            progress_bar = st.progress(0)

            # --- YouTube indirme ---
            if yt_link:
                progress_text.text("📥 YouTube indiriliyor...")
                video_path = "temp/video.mp4"
                ydl_opts = {
                    "format": "bestvideo+bestaudio/best",
                    "outtmpl": video_path,
                    "merge_output_format": "mp4",
                    "quiet": True,
                    "noplaylist": True,
                    "user_agent": "Mozilla/5.0",
                    "retries": 10,
                    "sleep_interval": 1,
                    "ffmpeg_location": os.path.dirname(FFMPEG_BIN)
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt_link])
                progress_bar.progress(10)
                st.success("✅ YouTube indirildi.")

            # --- Whisper modeli yükleme ---
            progress_text.text("🔄 Ses tanıma modeli yükleniyor...")
            model = whisper.load_model("base")
            progress_bar.progress(30)
            time.sleep(0.5)

            # --- Ses çözümleme ---
            progress_text.text("🗣️ Ses çözülüyor...")
            result = model.transcribe(video_path)
            original_text = result["text"]
            progress_bar.progress(60)
            time.sleep(0.5)

            # --- Türkçeye çeviri ---
            progress_text.text("🌍 Çeviri yapılıyor...")
            translated_text = GoogleTranslator(source="auto", target="tr").translate(original_text)
            progress_bar.progress(80)
            time.sleep(0.5)

            # --- Altyazı oluşturma ---
            progress_text.text("🧩 Altyazı hazırlanıyor...")
            subs = [
                srt.Subtitle(
                    index=i,
                    start=datetime.timedelta(seconds=i*5),
                    end=datetime.timedelta(seconds=(i+1)*5),
                    content=line.strip()
                )
                for i, line in enumerate(translated_text.split('.')) if line.strip()
            ]
            srt_content = srt.compose(subs)

            srt_path = "temp/altyazi.srt"
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)

            progress_bar.progress(90)

            # --- Videoya altyazı gömme ---
            progress_text.text("🎞️ Altyazı videoya gömülüyor...")
            output_path = "temp/video_altyazili.mp4"

            subprocess.run([
                FFMPEG_BIN, "-y", "-i", video_path, "-vf",
                f"subtitles={srt_path}:force_style='Fontsize=20,PrimaryColour=&H00FFFF&'",
                "-c:a", "copy", output_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

            progress_bar.progress(100)
            progress_text.text("✅ İşlem tamamlandı!")

            # --- İndirme butonları ---
            with open(srt_path, "r", encoding="utf-8") as f:
                st.download_button("⬇️ Altyazı dosyasını indir (SRT)", data=f.read(), file_name="altyazi.srt")

            with open(output_path, "rb") as f:
                st.download_button("🎬 Altyazılı videoyu indir (MP4)", data=f, file_name="video_altyazili.mp4")

            st.success("✅ Video altyazılı olarak hazır!")

    except Exception as e:
        st.error(f"🚨 Bir hata oluştu: {e}")

