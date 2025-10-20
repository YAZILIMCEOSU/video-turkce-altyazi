import streamlit as st
import whisper
from googletrans import Translator
from pytube import YouTube

st.title("🎬 Otomatik Türkçe Altyazı Çevirici")

option = st.radio("Video kaynağını seç:", ["Dosya Yükle", "YouTube Linki"])

if option == "Dosya Yükle":
    video = st.file_uploader("Video yükle", type=["mp4","mkv","avi"])
    if video:
        with open("video.mp4", "wb") as f:
            f.write(video.read())
        video_path = "video.mp4"
elif option == "YouTube Linki":
    url = st.text_input("YouTube linkini gir:")
    if st.button("Videoyu indir"):
        yt = YouTube(url)
        yt.streams.filter(only_audio=True).first().download(filename="video.mp4")
        video_path = "video.mp4"
        st.success("Video indirildi!")

if st.button("Altyazıyı oluştur"):
    st.info("İşleniyor...")
    model = whisper.load_model("small")
    result = model.transcribe("video.mp4")
    translator = Translator()
    tr_text = translator.translate(result["text"], dest='tr').text

    with open("translated.srt", "w", encoding="utf-8") as f:
        f.write(tr_text)
    st.success("✅ Türkçe altyazı hazır!")
    st.download_button("Altyazıyı indir", tr_text, file_name="altyazi.srt")
