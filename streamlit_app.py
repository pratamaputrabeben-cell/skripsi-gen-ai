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

model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. TAMPILAN WEBSITE ---
st.set_page_config(page_title="SkripsiGen Pro - Anti Plagiat", layout="wide")
st.title("🎓 SkripsiGen Pro v3.0")

tab1, tab2 = st.tabs(["📝 Penyusun Bab", "🔍 Cek & Parafrase Plagiasi"])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.header("⚙️ Pengaturan")
        topik = st.text_input("Judul Skripsi:", placeholder="Contoh: Analisis Gaya Kepemimpinan...")
        metode = st.radio("Metode:", ["Kuantitatif", "Kualitatif", "R&D"])
        bab = st.selectbox("Pilih Bab:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5"])
        
    with col2:
        if st.button(f"Generate {bab} ✨"):
            if topik:
                with st.spinner("Menyusun draf..."):
                    prompt = f"Buatkan draf {bab} skripsi berjudul '{topik}' dengan metode {metode}. Gunakan bahasa formal akademik Indonesia."
                    response = model.generate_content(prompt)
                    st.markdown(f"### Hasil {bab}")
                    st.write(response.text)
            else:
                st.warning("Isi judul dulu!")

with tab2:
    st.header("🔍 Simulasi Cek Plagiasi & Parafrase")
    st.info("Paste paragraf Anda di bawah untuk dicek keunikannya dan diperbaiki secara otomatis.")
    
    teks_input = st.text_area("Input Teks Skripsi:", height=200, placeholder="Tempel paragraf yang ingin dicek di sini...")
    
    if st.button("Analisis & Perbaiki Teks 🚀"):
        if teks_input:
            with st.spinner("Menganalisis potensi plagiasi..."):
                # Prompt untuk simulasi cek plagiasi dan parafrase
                prompt_cek = f"""
                Analisis teks berikut untuk potensi plagiasi akademik:
                '{teks_input}'
                
                Berikan output dalam format:
                1. Estimasi skor keunikan (0-100%).
                2. Bagian mana yang terkesan 'pasaran' atau terlalu umum.
                3. Berikan VERSI PARAFRASE yang lebih akademik dan unik agar lolos Turnitin.
                """
                response = model.generate_content(prompt_cek)
                
                st.subheader("Hasil Analisis & Parafrase")
                st.write(response.text)
        else:
            st.warning("Masukkan teks yang ingin diperiksa!")

# --- FUNGSI DOWNLOAD DOCX ---
def create_docx(judul, konten):
    doc = Document()
    doc.add_heading(judul, 0)
    doc.add_paragraph(konten)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()
