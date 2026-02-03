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

# --- 2. FUNGSI DOWNLOAD ---
def create_docx(judul, bab, konten):
    doc = Document()
    doc.add_heading(f"{bab}", 0)
    doc.add_heading(f"Judul: {judul}", level=1)
    doc.add_paragraph(konten)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 3. TAMPILAN WEBSITE ---
st.set_page_config(page_title="SkripsiGen Pro - Auto Reference", layout="wide")
st.title("🎓 SkripsiGen Pro v3.8")

with st.sidebar:
    st.header("⚙️ Pengaturan")
    topik = st.text_input("Judul Skripsi:", placeholder="Contoh: Strategi Pemasaran UMKM...")
    metode = st.radio("Metode Penelitian:", ["Kuantitatif", "Kualitatif", "R&D"])
    bab_pilihan = st.selectbox("Pilih Bab:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5"])
    
    st.divider()
    st.write("📚 **Format Sitasi:** APA Style 7th Ed.")
    st_auto_ref = st.checkbox("Sertakan Daftar Pustaka", value=True)

# --- 4. EKSEKUSI ---
if st.button(f"Generate {bab_pilihan} & Referensi ✨"):
    if topik:
        with st.spinner(f"Menyusun {bab_pilihan} dan memvalidasi daftar pustaka..."):
            
            prompt = f"""
            Tugas: Buatkan draf {bab_pilihan} untuk skripsi berjudul '{topik}' dengan metode {metode}.
            
            Aturan Akademik:
            1. Gunakan bahasa Indonesia formal (EYD).
            2. Berikan narasi yang dalam dan ilmiah.
            3. Sertakan kutipan (Sitasi) dalam teks (Contoh: Sugiyono, 2019).
            4. {'WAJIB: Buatkan DAFTAR PUSTAKA di akhir teks yang berisi semua referensi yang disitasi di atas dengan format APA Style 7th Edition.' if st_auto_ref else ''}
            5. Pastikan referensi relevan dengan topik dan metode {metode}.
            """
            
            try:
                response = model.generate_content(prompt)
                hasil_teks = response.text
                
                st.markdown(f"### ✨ Hasil Draf {bab_pilihan}")
                st.write(hasil_teks)
                
                file_word = create_docx(topik, bab_pilihan, hasil_teks)
                st.download_button(f"📥 Download {bab_pilihan} + Daftar Pustaka", 
                                   data=file_word, 
                                   file_name=f"{bab_pilihan.replace(' ', '_')}_Lengkap.docx")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
    else:
        st.warning("Isi judul skripsi dulu!")
