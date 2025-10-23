import imageio_ffmpeg
import os

# ffmpeg path'i al
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["FFMPEG_BINARY"] = ffmpeg_path

import streamlit as st
import os
import tempfile
import whisper
import srt
import datetime
from deep_translator import GoogleTranslator
import yt_dlp
import imageio.v3 as iio  # ffmpeg için
import time  # progress bar için

# ------------------- Başlık -------------------
st.title("🎬 Türkçe Altyazı Oluşturucu")
st.write("Videoyu yükle veya YouTube linki gir → Başlat butonuna basarak altyazıyı oluştur.")

# ------------------- Temp dizin -------------------
if not os.path.exists("temp"):
    os.makedirs("temp")

# ------------------- Video Kaynak Seçimi -------------------
option = st.radio("Video Kaynağı Seç:", ["📤 Video Yükle (≤200MB)", "🌐 YouTube Linki"])
video_path = None
yt_link = None

# --- Video Yükleme ---
if option == "📤 Video Yükle (≤200MB)":
    uploaded_file = st.file_uploader("Bir video yükle (MP4, MOV, AVI, MKV)", type=["mp4", "mov", "avi", "mkv"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name
        st.success("✅ Video başarıyla yüklendi.")

# --- YouTube Linki ---
elif option == "🌐 YouTube Linki":
    yt_link = st.text_input("YouTube video linkini gir:")

# ------------------- Başlat Butonu -------------------
if st.button("▶️ Başlat"):
    try:
        # Progress Bar başlat
        progress_text = st.empty()
        progress_bar = st.progress(0)

        # 0-10%: YouTube indirme
        if yt_link:
            progress_text.text("📥 YouTube videosu indiriliyor...")
            video_path = "temp/video.mp4"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': video_path,
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_link])
            progress_bar.progress(10)
            st.success("✅ YouTube videosu indirildi.")

        if not video_path:
            st.error("🚨 Video yüklenmedi veya link boş.")
        else:
            # 10-50%: Whisper model yükleme
            progress_text.text("🔄 Ses tanıma modeli yükleniyor...")
            model = whisper.load_model("base")
            progress_bar.progress(30)
            time.sleep(0.5)  # görsel efekt için

            # 50-70%: Ses çözümleme
            progress_text.text("🗣️ Ses çözümleniyor...")
            result = model.transcribe(video_path, language="en")
            original_text = result["text"]
            progress_bar.progress(60)
            time.sleep(0.5)

            # 70-85%: Türkçe çeviri
            progress_text.text("🌍 Metin Türkçe'ye çevriliyor...")
            translated_text = GoogleTranslator(source="auto", target="tr").translate(original_text)
            progress_bar.progress(80)
            time.sleep(0.5)

            # 85-100%: Altyazı oluşturma
            progress_text.text("🧩 Altyazı oluşturuluyor...")
            subs = [
                srt.Subtitle(
                    index=i,
                    start=datetime.timedelta(seconds=i * 5),
                    end=datetime.timedelta(seconds=(i + 1) * 5),
                    content=line.strip()
                )
                for i, line in enumerate(translated_text.split('.'))
                if line.strip()
            ]
            srt_content = srt.compose(subs)
            srt_path = "temp/altyazi.srt"
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
            progress_bar.progress(100)

            st.success("✅ Türkçe altyazı başarıyla oluşturuldu!")
            st.download_button("⬇️ Altyazıyı indir (.srt)", data=srt_content, file_name="altyazi.srt")

    except Exception as e:
        st.error(f"🚨 Bir hata oluştu: {e}")
