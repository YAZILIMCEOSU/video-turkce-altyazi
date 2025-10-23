import streamlit as st
import os
import tempfile
import whisper
import srt
import datetime
from deep_translator import GoogleTranslator
import yt_dlp
import imageio.v3 as iio  # ffmpeg için

# ------------------- Başlık -------------------
st.title("🎬 Türkçe Altyazı Oluşturucu")
st.write("Videoyu yükle veya YouTube linki gir → otomatik Türkçe altyazı oluşturulsun.")

# ------------------- Temp dizin -------------------
if not os.path.exists("temp"):
    os.makedirs("temp")

# ------------------- Video Kaynak Seçimi -------------------
option = st.radio("Video Kaynağı Seç:", ["📤 Video Yükle (≤200MB)", "🌐 YouTube Linki"])
video_path = None

# --- Video Yükleme ---
if option == "📤 Video Yükle (≤200MB)":
    uploaded_file = st.file_uploader("Bir video yükle (MP4, MOV, AVI, MKV)", type=["mp4", "mov", "avi", "mkv"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name
            st.success("✅ Video başarıyla yüklendi.")

# --- YouTube Video İndirme ---
elif option == "🌐 YouTube Linki":
    yt_link = st.text_input("YouTube video linkini gir:")
    if yt_link:
        try:
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
            st.success("✅ YouTube videosu indirildi.")
        except Exception as e:
            st.error(f"🚨 YouTube indirme hatası: {e}")

# ------------------- Altyazı Oluşturma -------------------
if video_path and st.button("🎧 Altyazıyı Oluştur"):
    try:
        st.info("🔄 Ses tanıma modeli yükleniyor...")
        model = whisper.load_model("base")

        st.info("🗣️ Ses çözümleniyor, lütfen bekleyin...")
        result = model.transcribe(video_path, language="en")
        original_text = result["text"]

        st.info("🌍 Metin Türkçe'ye çevriliyor...")
        translated_text = GoogleTranslator(source="auto", target="tr").translate(original_text)

        st.info("🧩 Altyazı oluşturuluyor...")
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

        st.success("✅ Türkçe altyazı başarıyla oluşturuldu!")
        st.download_button("⬇️ Altyazıyı indir (.srt)", data=srt_content, file_name="altyazi.srt")

    except Exception as e:
        st.error(f"🚨 Bir hata oluştu: {e}")
