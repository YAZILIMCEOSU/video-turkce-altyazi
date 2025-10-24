import os
import imageio_ffmpeg

FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG_BIN)

import streamlit as st
import tempfile
import os
import whisper
import srt
import datetime
from deep_translator import GoogleTranslator
import yt_dlp
import imageio_ffmpeg
import subprocess
import time

# 🔹 ffmpeg binary kesin çözüm
FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()  # kullanıcıya gösterme

# Başlık
st.title("🎬 Türkçe Altyazı Oluşturucu")
st.write("Video yükle veya YouTube linki gir → Başlat'a bas → Altyazıyı indir")

# Temp klasörü
if not os.path.exists("temp"):
    os.makedirs("temp")

# Video kaynağı
option = st.radio("Video Kaynağı:", ["📤 Video Yükle", "🌐 YouTube Linki"])
video_path = None
yt_link = None

if option == "📤 Video Yükle":
    uploaded_file = st.file_uploader("Video seç (MP4, MOV, AVI, MKV)", type=["mp4","mov","avi","mkv"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name
        st.success("✅ Video yüklendi.")

elif option == "🌐 YouTube Linki":
    yt_link = st.text_input("YouTube linki gir:")

# Başlat butonu
if st.button("▶️ Başlat"):
    try:
        if not video_path and not yt_link:
            st.error("🚨 Video yok veya YouTube linki girilmedi.")
        else:
            progress_text = st.empty()
            progress_bar = st.progress(0)

            # YouTube indirme
            if yt_link:
                progress_text.text("📥 YouTube indiriliyor...")
                video_path = "temp/video.mp4"
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': video_path,
                    'quiet': True,
                    'noplaylist': True,
                    'user_agent': 'Mozilla/5.0',
                    'retries': 10,
                    'sleep_interval': 1,
                    'ffmpeg_location': FFMPEG_BIN  # ffmpeg yolunu kesin veriyoruz
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt_link])
                progress_bar.progress(10)
                st.success("✅ YouTube indirildi.")

            # Whisper modeli yükleme
            progress_text.text("🔄 Ses tanıma modeli yükleniyor...")
            model = whisper.load_model("base")
            progress_bar.progress(30)
            time.sleep(0.5)

            # Ses çözümleme
            progress_text.text("🗣️ Ses çözülüyor...")
            result = model.transcribe(video_path)
            original_text = result["text"]
            progress_bar.progress(60)
            time.sleep(0.5)

            # Türkçeye çeviri
            progress_text.text("🌍 Çeviri yapılıyor...")
            translated_text = GoogleTranslator(source="auto", target="tr").translate(original_text)
            progress_bar.progress(80)
            time.sleep(0.5)

            # Altyazı oluşturma
            progress_text.text("🧩 Altyazı hazırlanıyor...")
            subs = [
                srt.Subtitle(
                    index=i,
                    start=datetime.timedelta(seconds=i*5),
                    end=datetime.timedelta(seconds=(i+1)*5),
                    content=line.strip()
                )
                for i,line in enumerate(translated_text.split('.')) if line.strip()
            ]
            srt_content = srt.compose(subs)

            srt_path = "temp/altyazi.srt"
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
            progress_bar.progress(100)

            st.success("✅ Altyazı hazır!")
            st.download_button("⬇️ Altyazıyı indir", data=srt_content, file_name="altyazi.srt")

    except Exception as e:
        st.error(f"🚨 Bir hata oluştu: {e}")
