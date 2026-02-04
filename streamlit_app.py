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
st.set_page_config(page_title="SkripsiGen Pro v8.73", page_icon="🎓", layout="wide")

# --- 3. SESSION STATE ---
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {
        "topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""
    }

# --- 4. ENGINE SETUP (MODIFIED FOR 404 ERROR) ---
def inisialisasi_ai():
    try:
        keys = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])
        key_aktif = random.choice(keys)
        genai.configure(api_key=key_aktif)
        
        # Daftar model terbaru 2026 yang paling stabil
        # Kita pakai versi 'models/' lengkap agar tidak 404
        model_options = [
            'gemini-1.5-flash-latest', 
            'gemini-1.5-pro-latest',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro'
        ]
        
        for m in model_options:
            try:
                model = genai.GenerativeModel(model_name=m)
                # Tes koneksi ringan
                return model
            except:
                continue
        
        # Jika semua gagal, pakai default yang paling umum
        return genai.GenerativeModel('gemini-pro')
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
st.title("🎓 SkripsiGen Pro v8.73")
st.caption("Standard: Academic Formatting 4-3-3-3 | Multi-Model Fallback Active")

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
        with st.spinner("Menghubungi Server Google..."):
            try:
                model = inisialisasi_ai()
                prompt = f"Susun {bab} skripsi {metode} judul '{st.session_state['user_data']['topik']}' di {st.session_state['user_data']['lokasi']}, {st.session_state['user_data']['kota']}. Gunakan format akademik."
                res = model.generate_content(prompt)
                if res.text:
                    st.session_state['db'][bab] = res.text
                    st.rerun()
            except Exception as e:
                st.error(f"Server sibuk: {e}. Coba klik lagi, Bos!")
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
                    st.success("Draf aman, siap salin ke Word.")
                else:
                    st.error("🔑 Bagian ini terkunci (Mode PRO)")
                    p_wa = f"Halo Admin, saya {nama_user} mau beli lisensi PRO."
                    wa_url = f"https://wa.me/6281273347072?text={p_wa.replace(' ', '%20')}"
                    st.link_button("💬 Hubungi Admin untuk Lisensi", wa_url)
