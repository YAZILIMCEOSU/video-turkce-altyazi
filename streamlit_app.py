import streamlit as st
import os
import tempfile
import srt
import datetime
import moviepy.editor as mp
from pytube import YouTube
import whisper
from deep_translator import GoogleTranslator  # 🔹 googletrans yerine

st.title("🎥 Türkçe Altyazı Çevirici Uygulaması")

st.markdown("""
Bu uygulama, yüklediğiniz veya YouTube bağlantısı verdiğiniz videolardan **Türkçe altyazı** üretir.  
Desteklenen diller: İngilizce, Almanca, Fransızca ve diğer diller.
""")

# 🔹 Whisper modelini yükle
@st.cache_resource
def load_model():
    return whisper.load_model("small")

model = load_model()

# 🔹 Video seçimi
option = st.radio("Video türünü seçin:", ["🎥 YouTube Linki", "📁 Bilgisayardan Yükle"])

video_path = None

if option == "🎥 YouTube Linki":
    yt_link = st.text_input("YouTube bağlantısını buraya yapıştırın:")
    if yt_link:
        try:
            yt = YouTube(yt_link)
            stream = yt.streams.filter(only_audio=True).first()
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            stream.download(filename=tmp_file.name)
            video_path = tmp_file.name
