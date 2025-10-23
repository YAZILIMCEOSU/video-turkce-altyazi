import streamlit as st
import os
import tempfile
import srt
import datetime
import whisper
from pytube import YouTube
from deep_translator import GoogleTranslator

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

# --- YouTube Video İndirme ---
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

# --- Dosya Yükleme ---
elif option == "📁 Bilgisayardan Yükle":
    uploaded_file = st.file_uploader("Bir video dosyası yükleyin (MP4, MKV, MOV)", type=["mp4", "mkv", "mov"])
    if uploaded_file:
        try:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name
            st.success("✅ Video yüklendi!")
        except Exception as e:
            st.error(f"❌ Video yüklenemedi: {e}")

# --- Altyazı Oluşturma ---
if video_path and st.button("🎧 Altyazıyı oluştur"):
    st.info("⏳ Ses dönüştürülüyor, lütfen bekleyin...")
    try:
        result = model.transcribe(video_path, task="translate")  # İngilizce'ye çevir
        english_text = result["text"]

        st.success("✅ Altyazı çıkarıldı. Türkçe'ye çevriliyor...")

        # 🔹 Deep Translator ile Türkçe çeviri
        translated_text = GoogleTranslator(source='auto', target='tr').translate(english_text)

        # 🔹 Altyazı objeleri oluştur
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

        # 🔹 SRT dosyasını kaydet
        srt_path = os.path.splitext(video_path)[0] + "_turkce.srt"
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        st.success("✅ Türkçe altyazı başarıyla oluşturuldu!")
        st.download_button("⬇️ Altyazı Dosyasını İndir (.srt)", srt_content, file_name="altyazi_tr.srt")

    except Exception as e:
        st.error(f"❌ Hata oluştu: {e}")

