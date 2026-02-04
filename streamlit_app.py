import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime

# --- 1. KONFIGURASI API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    def get_active_model_name():
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods: return m.name
        except: pass
        return "models/gemini-pro"
    model = genai.GenerativeModel(get_active_model_name())
except Exception as e:
    st.error(f"Koneksi API Gagal: {e}")
    st.stop()

# --- 2. LOGIKA LISENSI ---
def generate_license_logic(nama):
    hari_ini = datetime.now().strftime("%d%m")
    nama_clean = nama.split(' ')[0].upper() if nama else "USER"
    return f"PRO-{nama_clean}-{hari_ini}-SKR"

# --- 3. DATABASE SESI ---
if 'db' not in st.session_state:
    st.session_state['db'] = {}
if 'pustaka_koleksi' not in st.session_state:
    st.session_state['pustaka_koleksi'] = ""

# --- 4. TAMPILAN DASHBOARD ---
st.set_page_config(page_title="SkripsiGen Pro v8.9", layout="wide")

# --- SIDEBAR (AKTIVASI & ADMIN) ---
with st.sidebar:
    st.header("🔓 Aktivasi & Verifikasi")
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Budi Santoso")
    user_license = st.text_input("🔑 Kode Lisensi:", type="password")
    
    st.divider()
    st.write("🔍 **Cek Keaslian Jurnal**")
    cek_judul = st.text_input("Judul/DOI:", placeholder="Salin judul ke sini...")
    if cek_judul:
        q = cek_judul.replace(' ', '+')
        st.link_button("Cek di Google Scholar ↗️", f"https://scholar.google.com/scholar?q={q}")

    st.divider()
    if st.button("🗑️ Reset Semua Data"):
        st.session_state['db'] = {}
        st.session_state['pustaka_koleksi'] = ""
        st.rerun()

    # --- TEMPAT GENERATE LISENSI (DI SINI BOS!) ---
    st.divider()
    with st.expander("🛠️ MENU OWNER (GENERATE KODE)"):
        kunci_admin = st.text_input("Password Admin:", type="password")
        if kunci_admin == "BEBEN-BOSS":
            st.subheader("Buat Lisensi Baru")
            nama_pembeli = st.text_input("Nama Pembeli:")
            if st.button("Generate Sekarang ✨"):
                kode_baru = generate_license_logic(nama_pembeli)
                st.code(kode_baru)
                st.success(f"Salin kode di atas untuk {nama_pembeli}")
        else:
            st.info("Masukkan password 'BEBEN-BOSS' untuk buka generator.")

# --- 5. TAMPILAN UTAMA ---
st.title("🎓 SkripsiGen Pro v8.9")
st.caption("Sistem Pengerjaan Skripsi Otomatis - Standar Akademik 2026")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Analisis Pengaruh...")
    lokasi = st.text_input("📍 Lokasi Penelitian:", placeholder="Contoh: PT. Maju Jaya")
with c2:
    kota = st.text_input("🏙️ Kota & Provinsi:", placeholder="Contoh: Jakarta Selatan, DKI Jakarta")
    metode = st.selectbox("🔬 Metode Penelitian:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()

# GENERATOR
bab_pilihan = st.selectbox("📄 Pilih Bagian pengerjaan:", 
                          ["Bab 1: Pendahuluan", "Bab 2: Tinjauan Pustaka", "Bab 3: Metodologi Penelitian", 
                           "Bab 4: Hasil dan Pembahasan", "Bab 5: Penutup", "Lampiran: Instrumen"])

if st.button("🚀 Generate Draf Akademik"):
    if topik and nama_user:
        with st.spinner("Menghubungkan ke database referensi..."):
            thn =
