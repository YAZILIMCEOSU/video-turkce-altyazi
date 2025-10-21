import streamlit as st
import os
from pytube import YouTube
import whisper
from googletrans import Translator

st.set_page_config(page_title="🎬 Türkçe Altyazı Uygulaması")

st.title("🎧 Otomatik Türkçe Altyazı Çevirici")

st.write("Bu uygulama videonun sesini otomatik olarak çözümler, Türkçe'ye çevirir ve altyazı dosyası oluşturur.")

# Seçim
option = st.radio("Video kaynağını seç:", ["🎥 Bilgisayardan Yükle", "🔗 YouTube Linki"])

video_path = None

# 1️⃣ Dosya yükleme
if option == "🎥 Bilgisayardan Yükle":
    video = st.file_uploader("Video yükle (MP4, MKV, AVI)", type=["mp4", "mkv", "avi"])
    if video:
        with open("uploaded_video.mp4", "wb") as f:
            f.write(video.read())
        video_path = "uploaded_video.mp4"
        st.success("✅ Video başarıyla yüklendi.")

# 2️⃣ YouTube linki
elif option == "🔗 YouTube Linki":
    url = st.text_input("YouTube linkini gir:")
    if st.button("Videoyu indir"):
        if url:
            yt = YouTube(url)
            yt.streams.filter(only_audio=True).first().download(filename="youtube_video.mp4")
            video_path = "youtube_video.mp4"
            st.success("🎬 Video indirildi.")
        else:
            st.warning("Lütfen geçerli bir YouTube linki gir.")

# 3️⃣ Altyazı oluşturma
if video_path and st.button("Altyazıyı oluştur"):
    st.info("İşleniyor... Bu işlem birkaç dakika sürebilir ⏳")

    # Ses tanıma
    model = whisper.load_model("small")
    result = model.transcribe(video_path)

    # Türkçe çeviri
    translator = Translator()
    tr_text = translator.translate(result["text"], dest="tr").text

    # SRT oluşturma
    srt_path = "altyazi_tr.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(tr_text)

    st.success("✅ Türkçe altyazı başarıyla oluşturuldu!")
    with open(srt_path, "r", encoding="utf-8") as f:
        st.download_button("📄 Altyazıyı indir", f, file_name="altyazi_tr.srt")

