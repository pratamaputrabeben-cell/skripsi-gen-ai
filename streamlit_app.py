import streamlit as st
import requests
import google.generativeai as genai
from docx import Document
from io import BytesIO

# --- 1. KONEKSI KE API (AMBIL DARI SECRETS) ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("Waduh! API Key belum dipasang di Secrets Streamlit. Cek menu Settings > Secrets.")
    st.stop()

# --- 2. FUNGSI MENCARI MODEL YANG AKTIF (ANTI-404) ---
def get_working_model():
    try:
        # Mencari model apa saja yang diizinkan untuk API Key Anda
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        pass
    return "models/gemini-pro" # Pilihan terakhir jika gagal scan

# --- 3. FUNGSI PENDUKUNG ---
def search_real_papers(query):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=3&fields=title,authors,year,abstract,url"
    try:
        response = requests.get(url, timeout=5)
        return response.json().get('data', [])
    except:
        return []

def create_docx(judul, konten):
    doc = Document()
    doc.add_heading(judul, 0)
    doc.add_paragraph(konten)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 4. TAMPILAN WEBSITE ---
st.set_page_config(page_title="Penyusun Skripsi Otomatis", layout="wide")
st.title("🎓 SkripsiGen Pro")

topik = st.text_input("Masukkan Topik/Judul Skripsi:", placeholder="Contoh: Pengaruh Media Sosial pada Remaja")
bahasa = st.selectbox("Pilih Bahasa:", ["Indonesia", "English"])

if st.button("Generate Draf Bab 1 ✨"):
    if topik:
        with st.spinner("Sedang mencari model dan menyusun draf..."):
            # Cari model otomatis
            model_name = get_working_model()
            model = genai.GenerativeModel(model_name)
            
            # Cari referensi
            papers = search_real_papers(topik)
            context = ""
            if papers:
                for p in papers:
                    context += f"Judul: {p['title']}\nAbstrak: {p['abstract']}\n\n"
            
            prompt = f"Buatkan Bab 1 Skripsi formal dalam {bahasa} dengan judul '{topik}'. Gunakan data ini jika ada:\n{context}. Sertakan Latar Belakang, Rumusan Masalah, dan Daftar Pustaka."
            
            try:
                response = model.generate_content(prompt)
                hasil_teks = response.text
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"📝 Draf Bab 1")
                    st.write(hasil_teks)
                    file_word = create_docx(topik, hasil_teks)
                    st.download_button("📥 Download File Word", data=file_word, file_name=f"Draf_Skripsi.docx")
                with col2:
                    st.subheader("📚 Referensi Jurnal")
                    if papers:
                        for p in papers:
                            st.info(f"**{p['title']}**\n[Link Jurnal]({p['url']})")
                    else:
                        st.warning("Jurnal spesifik tidak ditemukan, menggunakan basis data AI.")
            except Exception as e:
                st.error(f"Gagal generate: {e}")
    else:
        st.warning("Silakan masukkan judul terlebih dahulu!")
