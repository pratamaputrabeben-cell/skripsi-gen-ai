import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import re

# --- 1. SEO BYPASS (WAJIB PERTAMA) ---
# Trik Meta Tag agar Google Search Console bisa baca kodenya
st.markdown('<meta name="google-site-verification" content="L6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI" />', unsafe_allow_html=True)

if st.query_params.get("google") == "1":
    st.write("google-site-verification: googleL6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI.html")
    st.stop()

# --- 2. CONFIG HALAMAN ---
st.set_page_config(page_title="SkripsiGen Pro v8.67", page_icon="🎓", layout="wide")

# --- 3. DATABASE & SESSION ---
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {
        "topik": "", 
        "lokasi": "SMK Negeri 2 Kabupaten Lahat", 
        "kota": "Lahat", 
        "nama": ""
    }

# --- 4. ENGINE SETUP ---
def inisialisasi_ai():
    try:
        keys = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])
        genai.configure(api_key=random.choice(keys))
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        st.error("⚠️ Cek API Key di Secrets Dashboard Streamlit!")
        st.stop()

# --- 5. TAMPILAN SIDEBAR ---
with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.info("SEO Tag & Auto-Format: ACTIVE")
    nama_user = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    st.session_state['user_data']['nama'] = nama_user
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    
    def gen_lic(n):
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{datetime.now().strftime('%d%m')}-SKR"

    if st.button("🗑️ Reset Sesi"):
        st.session_state['db'] = {}
        st.rerun()

# --- 6. TAMPILAN UTAMA & INPUT LOKASI ---
st.title("🎓 SkripsiGen Pro v8.67")
st.caption("Standard: Academic Formatting 4-3-3-3 | Verified by Google")

c1, c2 = st.columns(2)
with c1:
    st.session_state['user_data']['topik'] = st.text_input("📝 Judul Skripsi:", value=st.session_state['user_data']['topik'])
    # KEMBALI: Input Lokasi & Instansi
    st.session_state['user_data']['lokasi'] = st.text_input("📍 Lokasi (Contoh: SMK Negeri 2):", value=st.session_state['user_data']['lokasi'])
with c2:
    # KEMBALI: Input Kota/Provinsi
    st.session_state['user_data']['kota'] = st.text_input("🏙️ Kota/Provinsi:", value=st.session_state['user_data']['kota'])
    metode = st.selectbox("🔬 Metode Penelitian:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran"])

if st.button("🚀 Susun & Kalibrasi Sekarang"):
    if st.session_state['user_data']['topik'] and nama_user:
        with st.spinner("AI sedang merangkai draf..."):
            model = inisialisasi_ai()
            prompt = f"""Susun {pil_bab} skripsi {metode} dengan judul '{st.session_state['user_data']['topik']}' 
            berlokasi di {st.session_state['user_data']['lokasi']}, {st.session_state['user_data']['kota']}. 
            Gunakan referensi riil tahun 2023-2026 dan anti-plagiarisme."""
            res = model.generate_content(prompt)
            st.session_state['db'][pil_bab] = res.text
            st.rerun()
    else: st.warning("Nama & Judul wajib diisi!")

# Output & Download
if st.session_state['db']:
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            is_trial, is_pro = b in ["Bab 1", "Bab 2"], user_lic == gen_lic(nama_user)
            with st.expander("Buka Draf"):
                st.markdown(content)
                if is_trial or is_pro:
                    st.success("Format 4-3-3-3 Siap!")
                else:
                    st.error("🔑 Terkunci (Mode PRO)")
                    st.link_button("💬 Hubungi Admin
