import streamlit as st
import requests
import google.generativeai as genai
from docx import Document
from io import BytesIO

# --- KONFIGURASI API AMAN ---
# Sistem akan otomatis mengambil kunci dari menu Secrets tadi
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("Waduh! API Key belum dipasang di menu Secrets Streamlit.")
    st.stop()

# Fungsi mencari model aktif
def get_active_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        pass
    return 'gemini-1.5-flash'

model = genai.GenerativeModel(get_active_model())

# --- FUNGSI PENDUKUNG ---
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

# --- TAMPILAN WEBSITE ---
st.set_page_config(page_title="Penyusun Skripsi Otomatis", layout="wide")
st.title("🎓 SkripsiGen Pro")

topik = st.text_input("Masukkan Topik/Judul Skripsi:", placeholder="Contoh: Dampak AI pada UMKM")
bahasa = st.selectbox("Pilih Bahasa:", ["Indonesia", "English"])

if st.button("Generate Draf Bab 1 ✨"):
    if topik:
        with st.spinner("Sedang menyusun draf..."):
            papers = search_real_papers(topik)
            context = ""
            if papers:
                for p in papers:
                    context += f"Judul: {p['title']}\nAbstrak: {p['abstract']}\nURL: {p['url']}\n\n"
            
            prompt = f"Buatkan Bab 1 Skripsi formal dalam {bahasa} dengan judul '{topik}'. Gunakan data riil jika ada:\n{context}. Sertakan Latar Belakang dan Daftar Pustaka."
            
            try:
                response = model.generate_content(prompt)
                hasil_teks = response.text
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Draf Bab 1")
                    st.write(hasil_teks)
                    file_word = create_docx(topik, hasil_teks)
                    st.download_button("📥 Download File Word", data=file_word, file_name=f"Draf_Skripsi.docx")
                with col2:
                    st.subheader("Referensi Jurnal Riil")
                    if papers:
                        for p in papers:
                            st.info(f"**{p['title']}** ({p['year']})\n[Link Jurnal]({p['url']})")
                    else:
                        st.warning("Jurnal tidak ditemukan, menggunakan pengetahuan AI.")
            except Exception as e:
                st.error(f"Kesalahan: {e}")
