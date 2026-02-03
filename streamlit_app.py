import streamlit as st
import requests
import google.generativeai as genai
from docx import Document
from io import BytesIO

# --- 1. KONEKSI KE API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("API Key belum terpasang di Secrets.")
    st.stop()

def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except: pass
    return "models/gemini-pro"

model = genai.GenerativeModel(get_working_model())

# --- 2. FUNGSI PENDUKUNG ---
def create_docx(judul, bab, konten):
    doc = Document()
    doc.add_heading(f"{bab}: {judul}", 0)
    doc.add_paragraph(konten)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 3. TAMPILAN WEBSITE ---
st.set_page_config(page_title="SkripsiGen Pro - Full Version", layout="wide")
st.title("🎓 SkripsiGen Pro v2.0")
st.subheader("Penyusun Draf Skripsi Lengkap (Bab 1 - 5)")

with st.sidebar:
    st.header("Konfigurasi")
    topik = st.text_input("Judul Skripsi:", placeholder="Masukkan judul lengkap...")
    bab_pilihan = st.selectbox("Pilih Bab yang Ingin Dibuat:", 
                              ["Bab 1: Pendahuluan", 
                               "Bab 2: Tinjauan Pustaka", 
                               "Bab 3: Metodologi Penelitian", 
                               "Bab 4: Hasil dan Pembahasan", 
                               "Bab 5: Penutup"])
    bahasa = st.selectbox("Bahasa:", ["Indonesia", "English"])

# --- 4. LOGIKA PROMPT BERDASARKAN BAB ---
instruksi_bab = {
    "Bab 1: Pendahuluan": "Buatkan Latar Belakang, Rumusan Masalah, Tujuan, dan Manfaat Penelitian.",
    "Bab 2: Tinjauan Pustaka": "Buatkan landasan teori yang kuat, penelitian terdahulu, dan kerangka berpikir.",
    "Bab 3: Metodologi Penelitian": "Buatkan desain penelitian, populasi/sampel, teknik pengumpulan data, dan analisis data.",
    "Bab 4: Hasil dan Pembahasan": "Buatkan draf hasil penelitian (gunakan data dummy/contoh) dan analisis mendalam.",
    "Bab 5: Penutup": "Buatkan Kesimpulan yang menjawab rumusan masalah dan Saran untuk penelitian selanjutnya."
}

if st.button(f"Generate {bab_pilihan} ✨"):
    if topik:
        with st.spinner(f"Sedang menyusun {bab_pilihan}..."):
            prompt = f"""
            Anda adalah asisten dosen ahli. Buatkan draf {bab_pilihan} untuk skripsi berjudul '{topik}'.
            Gunakan bahasa Indonesia yang sangat formal dan akademik.
            Instruksi khusus: {instruksi_bab[bab_pilihan]}
            Sertakan sitasi standar APA jika memungkinkan.
            """
            try:
                response = model.generate_content(prompt)
                hasil_teks = response.text
                
                st.markdown(f"### Hasil {bab_pilihan}")
                st.write(hasil_teks)
                
                file_word = create_docx(topik, bab_pilihan, hasil_teks)
                st.download_button(f"📥 Download {bab_pilihan} (Word)", 
                                   data=file_word, 
                                   file_name=f"{bab_pilihan.replace(':', '')}.docx")
            except Exception as e:
                st.error(f"Gagal: {e}")
    else:
        st.warning("Silakan isi judul skripsi di menu samping (sidebar)!")
