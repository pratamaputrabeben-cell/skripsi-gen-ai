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
    return "models/gemini-1.5-flash"

model = genai.GenerativeModel(get_working_model())

# --- 2. FUNGSI PENDUKUNG ---
def create_docx(judul, bab, konten):
    doc = Document()
    doc.add_heading(f"{bab}", 0)
    doc.add_heading(f"Judul: {judul}", level=1)
    doc.add_paragraph(konten)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 3. TAMPILAN WEBSITE ---
st.set_page_config(page_title="SkripsiGen Pro - Full Research", layout="wide")
st.title("🎓 SkripsiGen Pro v2.5")

with st.sidebar:
    st.header("⚙️ Pengaturan Skripsi")
    topik = st.text_input("Judul Skripsi:", placeholder="Contoh: Analisis Kinerja Karyawan...")
    metode_pilihan = st.radio("Metode Penelitian Utama:", 
                             ["Kuantitatif (Data Angka/Statistik)", 
                              "Kualitatif (Wawancara/Studi Kasus)", 
                              "R&D (Pengembangan Produk/Sistem)"])
    bab_pilihan = st.selectbox("Pilih Bab:", 
                              ["Bab 1: Pendahuluan", 
                               "Bab 2: Tinjauan Pustaka", 
                               "Bab 3: Metodologi Penelitian", 
                               "Bab 4: Hasil dan Pembahasan", 
                               "Bab 5: Penutup"])
    bahasa = st.selectbox("Bahasa:", ["Indonesia", "English"])

# --- 4. LOGIKA INSTRUKSI BERDASARKAN METODE ---
# Bab 3 disesuaikan dengan metode yang dipilih pengguna
if "Kuantitatif" in metode_pilihan:
    metode_detail = "Gunakan pendekatan kuantitatif, populasi dan sampel, teknik sampling, instrumen angket/kuesioner, dan uji validitas/reliabilitas serta analisis statistik."
elif "Kualitatif" in metode_pilihan:
    metode_detail = "Gunakan pendekatan kualitatif deskriptif, teknik observasi, wawancara mendalam, dokumentasi, dan triangulasi data."
else:
    metode_detail = "Gunakan model pengembangan (seperti ADDIE atau Waterfall), tahapan perancangan, uji coba produk, dan validasi ahli."

instruksi_bab = {
    "Bab 1: Pendahuluan": "Buatkan Latar Belakang, Rumusan Masalah, Tujuan, dan Manfaat.",
    "Bab 2: Tinjauan Pustaka": "Buatkan landasan teori, penelitian terdahulu, dan kerangka pemikiran sesuai topik.",
    "Bab 3: Metodologi Penelitian": metode_detail,
    "Bab 4: Hasil dan Pembahasan": f"Buatkan draf hasil penelitian sesuai metode {metode_pilihan}. Sajikan analisis data dan pembahasan mendalam.",
    "Bab 5: Penutup": "Buatkan Kesimpulan dan Saran yang aplikatif."
}

# --- 5. EKSEKUSI ---
if st.button(f"Generate {bab_pilihan} ✨"):
    if topik:
        with st.spinner(f"Menyusun {bab_pilihan} dengan metode {metode_pilihan}..."):
            prompt = f"""
            Anda adalah pakar metodologi penelitian. Buatkan draf {bab_pilihan} untuk skripsi: '{topik}'.
            Gunakan format standar skripsi di Indonesia. 
            Metode yang harus digunakan: {metode_pilihan}.
            Instruksi spesifik isi: {instruksi_bab[bab_pilihan]}
            Pastikan Bab 4 dan 5 konsisten dengan metode {metode_pilihan} yang dipilih.
            Gunakan bahasa Indonesia yang baku, formal, dan objektif.
            """
            try:
                response = model.generate_content(prompt)
                hasil_teks = response.text
                
                st.markdown(f"### 📄 Hasil {bab_pilihan}")
                st.info(f"Metode: {metode_pilihan}")
                st.write(hasil_teks)
                
                file_word = create_docx(topik, bab_pilihan, hasil_teks)
                st.download_button(f"📥 Download {bab_pilihan}", 
                                   data=file_word, 
                                   file_name=f"{bab_pilihan.replace(' ', '_')}.docx")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
    else:
        st.warning("Isi judul skripsi dulu di menu samping!")
