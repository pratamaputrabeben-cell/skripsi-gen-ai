import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime
import random

# --- 1. KONFIGURASI API ---
ALL_KEYS = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])

def inisialisasi_ai():
    if not ALL_KEYS or ALL_KEYS[0] == "":
        st.error("API Key kosong!"); st.stop()
    key_aktif = random.choice(ALL_KEYS)
    genai.configure(api_key=key_aktif)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for target in ['gemini-1.5-flash', 'gemini-1.5-pro']:
            for real_model in available_models:
                if target in real_model: return genai.GenerativeModel(real_model)
        return genai.GenerativeModel(available_models[0])
    except: return genai.GenerativeModel('gemini-1.5-flash')

try:
    model = inisialisasi_ai()
    nama_mesin = model.model_name
except Exception as e:
    st.error(f"Error: {e}"); st.stop()

# --- 2. LOGIKA LISENSI ---
def gen_lic(n):
    d = datetime.now().strftime("%d%m")
    nm = n.split(' ')[0].upper() if n else "USER"
    return f"PRO-{nm}-{d}-SKR"

if 'db' not in st.session_state: st.session_state['db'] = {}

# --- 3. UI SETUP ---
st.set_page_config(page_title="SkripsiGen Pro v8.24", layout="wide")

with st.sidebar:
    st.header("🔓 Aktivasi & Audit")
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Contoh: Beny")
    user_lic = st.text_input("🔑 Kode Lisensi:", type="password")
    
    st.divider()
    st.subheader("🛠️ Alat Audit Mandiri")
    st.info("Gunakan alat di bawah untuk verifikasi draf AI secara mendalam.")
    st.link_button("🌐 Cek Database Jurnal (Crossref)", "https://search.crossref.org/")
    st.link_button("🤖 Cek Deteksi AI (ZeroGPT)", "https://www.zerogpt.com/")
    
    st.divider()
    with st.expander("🛠️ MENU OWNER"):
        pw = st.text_input("Admin Pass:", type="password")
        if pw == "BEBEN-BOSS":
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate ✨"): st.code(gen_lic(pbl))

# --- 4. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.24")
st.caption(f"Status: Online | Jalur: {nama_mesin}")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Pengaruh Lingkungan Kerja...")
    lokasi = st.text_input("📍 Lokasi:", placeholder="Contoh: PT. Maju")
with c2:
    kota = st.text_input("🏙️ Kota:", placeholder="Contoh: Jakarta")
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran"])

if st.button("🚀 Susun Draf & Jalankan Audit"):
    if topik and nama_user:
        with st.spinner("Menyusun draf akademik..."):
            prompt = f"Buat draf {pil_bab} skripsi {metode} judul '{topik}' di {lokasi}, {kota}. Wajib gunakan teori ahli riil, kutipan APA 7th, dan referensi 2023-2026."
            try:
                res = model.generate_content(prompt)
                st.session_state['db'][pil_bab] = res.text
                st.rerun()
            except Exception as e:
                st.warning("⚠️ Jalur penuh, klik sekali lagi!")
    else: st.warning("Lengkapi Nama & Judul!")

# --- 5. BOX OUTPUT DENGAN PANEL VERIFIKASI ---
if st.session_state['db']:
    st.divider()
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            
            # --- PANEL AUDIT KHUSUS ---
            v1, v2, v3, v4 = st.columns(4)
            with v1:
                st.link_button("🔍 Cek Jurnal (Scholar)", f"https://scholar.google.com/scholar?q={topik.replace(' ', '+')}")
            with v2:
                # Untuk cek apakah jurnal/DOI yang dikasih AI itu beneran terdaftar di dunia
                st.link_button("📑 Verifikasi DOI", "https://search.crossref.org/")
            with v3:
                # Untuk cek plagiasi umum
                st.link_button("🛡️ Cek Plagiasi", "https://www.duplichecker.com/id")
            with v4:
                if st.button("🗑️ Hapus", key=f"del_{b}"):
                    del st.session_state['db'][b]; st.rerun()
            
            st.markdown(content[:400] + "...")
            with st.expander("Buka Draf Lengkap"):
                st.markdown(content)
                if user_lic == gen_lic(nama_user):
                    doc = Document()
                    doc.add_heading(b, 0); doc.add_paragraph(content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download Word", data=bio.getvalue(), file_name=f"{b}.docx", key=f"d_{b}")
                else: st.warning("Masukkan lisensi untuk download.")
