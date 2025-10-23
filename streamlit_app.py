import streamlit as st
import os
import tempfile
import srt
import moviepy.editor as mp
from pytube import YouTube
import whisper
from deep_translator import GoogleTranslator  # 🔹 Yeni eklendi, googletrans yerine

st.title("🎬 Türkçe Altyazı Çevirici Uygulaması")

st.markdown("""
Bu uygulama, yüklediğiniz veya YouTube bağlantısı verdiğiniz videolardan **Türkçe altyazı** üretir.  
Desteklenen diller: İngilizce, Almanca, Fransızca ve diğer diller.
""")

# Whisper modelini yükle
@st.cache_resource
def load_model():
    return whisper.load_model("small")

model = load_model()

# Video seçimi
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
            st.success("✅ YouTube videosu indirildi!")
        except Exception as e:
            st.error(f"❌ Video indirilemedi: {e}")

elif option == "📁 Bilgisayardan Yükle":
    uploaded_file = st.file_uploader("Bir video dosyası yükleyin (MP4)", type=["mp4", "mkv", "mov"])
    if uploaded_file:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp_file.write(uploaded_file.read())
        video_path = tmp_file.name
        st.success("✅ Video yüklendi!")

# Altyazı oluşturma
if video_path and st.button("🎧 Altyazıyı oluştur"):
    st.info("⏳ Ses dönüştürülüyor, lütfen bekleyin...")
    try:
        result = model.transcribe(video_path, task="translate")  # İngilizceye çevir
        english_text = result["text"]

        st.success("✅ Altyazı çıkarıldı. Türkçe'ye çevriliyor...")

        # 🔹 Deep Translator kullanımı (Googletrans yerine)
        translated_text = GoogleTranslator(source='auto', target='tr').translate(english_text)

        # Altyazı dosyasını oluştur
        subs = [srt.Subtitle(index=i, start=srt.timedelta(seconds=i * 5),

