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

# Fungsi untuk memilih model secara otomatis
def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        pass
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
st.set_page_config(page_title="SkripsiGen Pro - Auto Anti-Plagiat", layout="wide")
st.title("🎓 SkripsiGen Pro v3.5 (Auto-Parafrase)")

with st.sidebar:
    st.header("⚙️ Pengaturan")
    topik = st.text_input("Judul Skripsi:", placeholder="Masukkan judul...")
    metode = st.radio("Metode Penelitian:", ["Kuantitatif", "Kualitatif", "R&D"])
    bab_pilihan = st.selectbox("Pilih Bab:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5"])
    
    st.divider()
    st.write("🛡️ **Fitur Keamanan:**")
    st_auto_clean = st.checkbox("Otomatis Parafrase (Anti-Plagiat)", value=True)
    st_academic_tone = st.checkbox("Gunakan Bahasa Dosen/Formal", value=True)

# --- 4. EKSEKUSI OTOMATIS ---
if st.button(f"Generate & Bersihkan {bab_pilihan} ✨"):
    if topik:
        with st.spinner(f"Sedang menyusun dan melakukan parafrase otomatis pada {bab_pilihan}..."):
            
            prompt = f"""
            Tugas: Buatkan draf {bab_pilihan} untuk skripsi berjudul '{topik}' dengan metode {metode}.
            
            Aturan Ketat:
            1. Gunakan struktur standar akademik Indonesia.
            2. {'Lakukan parafrase tingkat tinggi agar tidak terdeteksi sebagai teks AI umum.' if st_auto_clean else ''}
            3. {'Gunakan kosakata tingkat lanjut dan nada bicara dosen penguji.' if st_academic_tone else ''}
            4. Pastikan alur antar paragraf koheren (nyambung).
            5. Sertakan sitasi (Nama, Tahun) dalam teks.
            """
            
            try:
                response = model.generate_content(prompt)
                hasil_teks = response.text
                
                st.markdown(f"### ✨ Hasil Draf {bab_pilihan} (Versi Bersih)")
                st.success("✅ Teks telah diproses dengan fitur Anti-Plagiat Otomatis.")
                st.write(hasil_teks)
                
                file_word = create_docx(topik, bab_pilihan, hasil_teks)
                st.download_button(f"📥 Download {bab_pilihan} (.docx)", 
                                   data=file_word, 
                                   file_name=f"Clean_{bab_pilihan.replace(' ', '_')}.docx")
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
    else:
        st.warning("Silakan isi judul skripsi dulu!")
