import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import re

# --- 1. SEO BYPASS ---
st.markdown('<meta name="google-site-verification" content="L6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI" />', unsafe_allow_html=True)

if st.query_params.get("google") == "1":
    st.write("google-site-verification: googleL6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI.html")
    st.stop()

# --- 2. CONFIG HALAMAN ---
st.set_page_config(page_title="SkripsiGen Pro v8.74", page_icon="🎓", layout="wide")

# --- 3. SESSION STATE ---
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {
        "topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""
    }

# --- 4. ENGINE SETUP (SMART DISCOVERY - ANTI 404) ---
def inisialisasi_ai():
    try:
        keys = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])
        key_aktif = random.choice(keys)
        genai.configure(api_key=key_aktif)
        
        # Minta daftar model yang benar-benar ada di akun Bos Beben
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Urutan prioritas model terbaik
        targets = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        for target in targets:
            for real_model in available_models:
                if target in real_model:
                    return genai.GenerativeModel(real_model)
        
        # Kalau tidak ketemu yang favorit, pakai apa saja yang ada
        return genai.GenerativeModel(available_models[0])
    except Exception as e:
        st.error(f"Koneksi API Gagal: {e}")
        st.stop()

# --- 5. SIDEBAR & ADMIN ---
with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    nama_user = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    st.session_state['user_data']['nama'] = nama_user
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    
    def gen_lic(n):
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{datetime.now().strftime('%d%m')}-SKR"

    st.divider()
    with st.expander("🛠️ OWNER PANEL"):
        pw = st.text_input("Password Admin:", type="password")
        if pw == "RAHASIA-BEBEN-2026": 
            st.success("Halo Bos Beben!")
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Buat Kode Lisensi ✨"): st.code(gen_lic(pbl))
    
    if st.button("🗑️ Reset Sesi"):
        st.session_state['db'] = {}
        st.rerun()

# --- 6. TAMPILAN UTAMA ---
st.title("🎓 SkripsiGen Pro v8.74")
st.caption("Auto-Discovery Model Active | Anti-404 System")

c1, c2 = st.columns(2)
with c1:
    st.session_state['user_data']['topik'] = st.text_input("📝 Judul Skripsi:", value=st.session_state['user_data']['topik'])
    st.session_state['user_data']['lokasi'] = st.text_input("📍 Instansi:", value=st.session_state['user_data']['lokasi'])
with c2:
    st.session_state['user_data']['kota'] = st.text_input("🏙️ Kota/Provinsi:", value=st.session_state['user_data']['kota'])
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5"])

if st.button("🚀 Susun Sekarang"):
    if st.session_state['user_data']['topik'] and nama_user:
        with st.spinner("Mencari Model AI yang aktif..."):
            try:
                model = inisialisasi_ai()
                prompt = f"Susun {bab} skripsi {metode} judul '{st.session_state['user_data']['topik']}' di {st.session_state['user_data']['lokasi']}, {st.session_state['user_data']['kota']}. Pakai format akademik."
                res = model.generate_content(prompt)
                st.session_state['db'][bab] = res.text
                st.rerun()
            except Exception as e:
                st.error(f"Google Error: {e}")
    else: st.warning("Isi Nama & Judul!")

# --- 7. OUTPUT BOX ---
if st.session_state['db']:
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            is_pro = user_lic == gen_lic(nama_user)
            with st.expander("Buka Draf"):
                st.markdown(content)
                if b in ["Bab 1", "Bab 2"] or is_pro:
                    st.success("Draf aman, siap salin.")
                else:
                    st.error("🔑 Bagian ini terkunci (Mode PRO)")
                    p_wa = f"Halo Admin, saya {nama_user} mau beli lisensi PRO."
                    wa_url = f"https://wa.me/6281273347072?text={p_wa.replace(' ', '%20')}"
                    st.link_button("💬 Hubungi Admin untuk Lisensi", wa_url)
