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
    st.error(f"API Error: {e}")
    st.stop()

# --- 2. LOGIKA LISENSI ---
def generate_license_logic(nama):
    tgl = datetime.now().strftime("%d%m")
    nm = nama.split(' ')[0].upper() if nama else "USER"
    return f"PRO-{nm}-{tgl}-SKR"

# --- 3. DATABASE SESI ---
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'pustaka' not in st.session_state: st.session_state['pustaka'] = ""

# --- 4. TAMPILAN DASHBOARD ---
st.set_page_config(page_title="SkripsiGen Pro v8.10", layout="wide")

# SIDEBAR (AKTIVASI & ADMIN)
with st.sidebar:
    st.header("🔓 Aktivasi & Verifikasi")
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Budi Santoso")
    user_license = st.text_input("🔑 Kode Lisensi:", type="password")
    
    st.divider()
    st.write("🔍 **Cek Keaslian Jurnal**")
    cek_j = st.text_input("Judul/DOI:", placeholder="Salin judul ke sini...")
    if cek_j:
        st.link_button("Cek di Google Scholar ↗️", f"https://scholar.google.com/scholar?q={cek_j.replace(' ', '+')}")

    # --- MENU OWNER (GENERATE KODE) ---
    st.divider()
    with st.expander("🛠️ MENU OWNER"):
        kunci = st.text_input("Password Admin:", type="password")
        if kunci == "BEBEN-BOSS":
            st.subheader("Buat Lisensi")
            pembeli = st.text_input("Nama Pembeli:")
            if st.button("Generate ✨"):
                st.code(generate_license_logic(pembeli))
                st.success(f"Kode untuk {pembeli}")

# --- 5. TAMPILAN UTAMA ---
st.title("🎓 SkripsiGen Pro v8.10")
st.caption("Standar Akademik 2026 | Referensi Riil 3 Tahun Terakhir")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Analisis Pengaruh...")
    lokasi = st.text_input("📍 Lokasi Penelitian:", placeholder="Contoh: PT. Maju Jaya")
with c2:
    kota = st.text_input("🏙️ Kota & Provinsi:", placeholder="Jakarta Selatan, DKI Jakarta")
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()

# GENERATOR
pilihan = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran: Instrumen"])

if st.button("🚀 Generate Draf"):
    if topik and nama_user:
        with st.spinner("Menyusun draf akademik..."):
            thn_now = 2026
            rnt = f"{thn_now-3}-{thn_
