import streamlit as st
import requests
import google.generativeai as genai
from docx import Document
from io import BytesIO

# --- KONFIGURASI API ---
genai.configure(api_key="AIzaSyAFv7QLp9t7luNhvjXTV_RB4Zm7hwm5CN0")
model = genai.GenerativeModel('gemini-1.5-flash')

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
            # Cari jurnal
            papers = search_real_papers(topik)
            
            # Siapkan konteks referensi
            if papers:
                context = "Gunakan data riil dari jurnal berikut:\n"
                for p in papers:
                    context += f"Judul: {p['title']}\nAbstrak: {p['abstract']}\nURL: {p['url']}\n\n"
            else:
                context = "Referensi jurnal spesifik tidak ditemukan di database, gunakan pengetahuan akademik umum yang relevan dengan topik ini."

            # Minta AI buat draf
            prompt = f"Buatkan Bab 1 Skripsi formal dalam {bahasa} dengan judul '{topik}'. {context} Sertakan Latar Belakang, Rumusan Masalah, dan Daftar Pustaka."
            
            try:
                response = model.generate_content(prompt)
                hasil_teks = response.text
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Draf Bab 1")
                    st.write(hasil_teks)
                    file_word = create_docx(topik, hasil_teks)
                    st.download_button("📥 Download File Word (.docx)", data=file_word, file_name=f"Draf_Skripsi.docx")
                
                with col2:
                    st.subheader("Referensi Jurnal Riil")
                    if papers:
                        for p in papers:
                            st.info(f"**{p['title']}** ({p['year']})\n[Link Jurnal]({p['url']})")
                    else:
                        st.warning("⚠️ Catatan: Tidak ditemukan jurnal spesifik di database. Draf dibuat berdasarkan referensi akademik umum.")
            except Exception as e:
                st.error(f"Terjadi kesalahan pada AI: {e}")
    else:
        st.warning("Masukkan judul terlebih dahulu!")
