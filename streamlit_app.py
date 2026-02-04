import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import re

# --- 1. SEO BYPASS (UNTUK GOOGLE SEARCH CONSOLE) ---
# Diletakkan paling awal agar bot Google langsung mendeteksi kepemilikan
st.markdown('<meta name="google-site-verification" content="L6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI" />', unsafe_allow_html=True)

if st.query_params.get("google") == "1":
    st.write("google-site-verification: googleL6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI.html")
    st.stop()

# --- 2. CONFIG HALAMAN ---
st.set_page_config(page_title="SkripsiGen Pro v8.70", page_icon="🎓", layout="wide")

# --- 3. DATABASE & SESSION STATE ---
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {
        "topik": "", 
        "lokasi": "SMK Negeri 2 Kabupaten Lahat", 
        "kota": "Lahat", 
        "nama": ""
    }

# --- 4. ENGINE SETUP (API KEY) ---
def inisialisasi_ai():
    try:
        # Mengambil kunci dari Secrets Streamlit
        keys = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])
        genai.configure(api_key=random.choice(keys))
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        st.error("⚠️ API Key belum disetting di Secrets Dashboard Streamlit!")
        st.stop()

# --- 5. TAMPILAN SIDEBAR & ADMIN PANEL ---
with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.info("Status: SEO Verified & Academic Mode")
    
    nama_user = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    st.session_state['user_data']['nama'] = nama_user
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    
    # Fungsi Generate Lisensi Otomatis
    def gen_lic(n):
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{datetime.now().strftime('%d%m')}-SKR"

    st.divider()
    
    # OWNER PANEL: Tempat Bos Beben cetak duit (Lisensi)
    with st.expander("🛠️ OWNER PANEL (Admin Only)"):
        pw = st.text_input("Password Admin:", type="password")
        if pw == "RAHASIA-BEBEN-2026": 
            st.success("Halo Bos Beben! Siap jualan?")
            pbl = st.text_input("Nama Pembeli Baru:")
            if st.button("Generate License Code ✨"):
                st.code(gen_lic(pbl))
        elif pw:
            st.error("Akses Ditolak!")

    if st.button("🗑️ Reset Sesi Aplikasi"):
        st.session_state['db'] = {}
        st.rerun()

# --- 6. TAMPILAN UTAMA (INPUT DATA) ---
st.title("🎓 SkripsiGen Pro v8.70")
st.caption("Standard: Academic Formatting 4-3-3-3 | Anti-Plagiarism | SEO Ready")

c1, c2 = st.columns(2)
with c1:
    st.session_state['user_data']['topik'] = st.text_input("📝 Judul Skripsi:", value=st.session_state['user_data']['topik'])
    st.session_state['user_data']['lokasi'] = st.text_input("📍 Instansi/Lokasi Penelitian:", value=st.session_state['user_data']['lokasi'])
with c2:
    st.session_state['user_data']['kota'] = st.text_input("🏙️ Kota/Provinsi:", value=st.session_state['user_data']['kota'])
    metode = st.selectbox("🔬 Metode Penelitian:", ["Kuantitatif", "Kualitatif", "R&D", "Studi Kasus"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian Yang Ingin Disusun:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Daftar Pustaka"])

if st.button("🚀 Susun & Kalibrasi Sekarang"):
    if st.session_state['user_data']['topik'] and nama_user:
        with st.spinner("AI sedang menyusun draf akademik..."):
            model = inisialisasi_ai()
            prompt = f"""
            Bertindaklah sebagai Konsultan Skripsi Profesional. 
            Susun {pil_bab} skripsi dengan metode {metode}.
            Judul: '{st.session_state['user_data']['topik']}'
            Lokasi: {st.session_state['user_data']['lokasi']}, {st.session_state['user_data']['kota']}
            Nama Peneliti: {nama_user}
            
            Gunakan Bahasa Indonesia formal (PUEBI), referensi riil tahun 2023-2026, 
            dan pastikan struktur paragraf sesuai standar akademik (Margin 4-4-3-3).
            """
            res = model.generate_content(prompt)
            st.session_state['db'][pil_bab] = res.text
            st.rerun()
    else:
        st.warning("Mohon isi Nama Mahasiswa dan Judul Skripsi terlebih dahulu!")

# --- 7. TAMPILAN HASIL (OUTPUT) ---
if st.session_state['db']:
    st.divider()
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            st.markdown(f"### 📄 Hasil Penyusunan: {b}")
            
            # Cek Lisensi
            is_pro = user_lic == gen_lic(nama_user)
            is_trial = b in ["Bab 1", "Bab 2"]
            
            with st.expander(f"Klik untuk Melihat Draf {b}"):
                st.markdown(content)
                
                if is_trial or is_pro:
                    st.success("✅ Mode Akses: Terbuka. Silakan salin ke MS Word.")
                else:
                    st.error("🔑 Bagian ini Terkunci (Khusus Pengguna PRO)")
                    wa_link = f"https://wa.me/6281273347072?text=Halo%20Admin%2C%20saya%20{nama_user}%20ingin%20beli%20lisensi%20PRO%20untuk%20judul%20{st.session_state['user
