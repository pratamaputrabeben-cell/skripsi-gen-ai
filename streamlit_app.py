import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime

# --- 1. KONEKSI API DENGAN DETEKSI OTOMATIS ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Fungsi mencari model yang PASTI BISA dipakai
    def inisialisasi_mesin():
        daftar_target = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.5-pro']
        tersedia = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Cari yang cocok dari daftar target
        for target in daftar_target:
            # Cek apakah target ada di daftar model yang tersedia (dengan atau tanpa prefix 'models/')
            for model_aktif in tersedia:
                if target in model_aktif:
                    return genai.GenerativeModel(model_aktif)
        
        # Jika gagal total, gunakan fallback paling standar
        return genai.GenerativeModel('gemini-pro')

    model = inisialisasi_mesin()
    nama_mesin = model.model_name
except Exception as e:
    st.error(f"Gagal koneksi ke server Google: {e}"); st.stop()

# --- 2. LOGIKA LISENSI ---
def gen_lic(n):
    d = datetime.now().strftime("%d%m")
    nm = n.split(' ')[0].upper() if n else "USER"
    return f"PRO-{nm}-{d}-SKR"

# --- 3. DATABASE SESI ---
if 'db' not in st.session_state: st.session_state['db'] = {}

# --- 4. UI SETUP ---
st.set_page_config(page_title="SkripsiGen Pro v8.19", layout="wide")

with st.sidebar:
    st.header("🔓 Aktivasi")
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Budi Santoso")
    user_lic = st.text_input("🔑 Kode Lisensi:", type="password")
    
    st.divider()
    st.write("🔍 **Cek Jurnal Riil**")
    cj = st.text_input("Salin Judul/DOI:", placeholder="Cek keaslian...")
    if cj:
        st.link_button("Cek di Google Scholar ↗️", f"https://scholar.google.com/scholar?q={cj.replace(' ', '+')}")

    st.divider()
    with st.expander("🛠️ MENU OWNER"):
        pw = st.text_input("Password Admin:", type="password")
        if pw == "BEBEN-BOSS":
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate ✨"):
                st.code(gen_lic(pbl))

# --- 5. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.19")
st.caption(f"Mesin Aktif: {nama_mesin} | Standar Akademik 2026")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Pengaruh X terhadap Y...")
    lokasi = st.text_input("📍 Lokasi:", placeholder="Contoh: PT. ABC")
with c2:
    kota = st.text_input("🏙️ Kota:", placeholder="Contoh: Jakarta")
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran"])

if st.button("🚀 Susun Draf Skripsi"):
    if topik and nama_user:
        with st.spinner("AI sedang menyusun draf..."):
            prompt = f"Buatkan draf {pil_bab} skripsi {metode} judul '{topik}' di {lokasi}. Bedah variabel, kutip ahli riil 2023-2026, dan format APA 7th."
            try:
                res = model.generate_content(prompt)
                st.session_state['db'][pil_bab] = res.text
                st.rerun()
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ Kuota penuh. Tunggu 60 detik.")
                else:
                    st.error(f"Kendala Teknis: {e}")
    else:
        st.warning("Isi Nama & Judul!")

# --- 6. DOKUMEN BOX ---
if st.session_state['db']:
    st.divider()
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            col_b1, col_b2 = st.columns([5, 1])
            with col_b1: st.markdown(f"### 📄 {b}")
            with col_b2:
                if st.button("🗑️ Hapus", key=f"del_{b}"):
                    del st.session_state['db'][b]; st.rerun()
            
            st.markdown(content[:300] + "...")
            with st.expander("Lihat & Download"):
                st.markdown(content)
                if user_lic == gen_lic(nama_user):
                    doc = Document()
                    doc.add_heading(b, 0)
                    doc.add_paragraph(content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download Word", data=bio.getvalue(), file_name=f"{b}.docx", key=f"d_{b}")
                else:
                    st.warning("⚠️ Masukkan lisensi di sidebar untuk download.")
