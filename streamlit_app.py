import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime

# --- 1. KONEKSI API ---
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
    st.error(f"Koneksi Gagal: {e}")
    st.stop()

# --- 2. LOGIKA LISENSI ---
def generate_license_logic(nama):
    hari_ini = datetime.now().strftime("%d%m")
    nama_clean = nama.split(' ')[0].upper() if nama else "USER"
    # Rumus: PRO-[NAMA]-TGLBLN-SKR
    return f"PRO-{nama_clean}-{hari_ini}-SKR"

# --- 3. INISIALISASI DATABASE ---
if 'db' not in st.session_state:
    st.session_state['db'] = {}

# --- 4. TAMPILAN ---
st.set_page_config(page_title="SkripsiGen Pro - Fixed License", layout="wide")

with st.expander("🛠️ Admin Panel (Owner Only)"):
    kunci_admin = st.text_input("Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        st.subheader("Generator Kode Lisensi")
        pembeli = st.text_input("Nama Pembeli:")
        if st.button("Generate Kode"):
            st.code(generate_license_logic(pembeli))

st.title("🎓 SkripsiGen Pro v6.4")

# IDENTITAS
c1, c2 = st.columns(2)
with c1:
    nama_user = st.text_input("👤 Nama Lengkap Anda:", placeholder="Budi Santoso")
with c2:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Analisis Strategi...")

st.divider()

# KONTROL UTAMA
col_ctrl1, col_ctrl2 = st.columns(2)
with col_ctrl1:
    metode = st.selectbox("🔬 Metode Penelitian:", ["Kuantitatif", "Kualitatif", "R&D"])
with col_ctrl2:
    bab_pilihan = st.selectbox("📄 Pilih Bab untuk Dikerjakan/Dilihat:", 
                              ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", 
                               "Lampiran: Instrumen", "Lampiran: Surat Izin"])

# TOMBOL AKSI
tab_b, tab_r = st.tabs(["📝 Buat/Lihat Draf", "🔄 Revisi Dosen"])

with tab_b:
    if st.button("🚀 Generate / Update Draf"):
        if topik and nama_user:
            with st.spinner(f"Menyusun {bab_pilihan}..."):
                prompt = f"Judul: {topik}\nNama: {nama_user}\nMetode: {metode}\nTugas: Buatkan draf {bab_pilihan} formal."
                try:
                    res = model.generate_content(prompt)
                    st.session_state['db'][bab_pilihan] = res.text
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")
        else: st.warning("Isi Nama & Judul!")

with tab_r:
    catatan = st.text_area("✍️ Catatan Revisi untuk Bab ini:")
    if st.button("Proses Revisi 🚀"):
        if catatan and topik:
            with st.spinner("Merevisi..."):
                prompt_rev = f"Revisi {bab_pilihan} judul {topik} berdasarkan: {catatan}. Tulis ulang."
                try:
                    res = model.generate_content(prompt_rev)
                    st.session_state['db'][bab_pilihan] = res.text
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")

# --- AREA HASIL & LISENSI (DIPERBAIKI) ---
if bab_pilihan in st.session_state['db']:
    teks = st.session_state['db'][bab_pilihan]
    st.divider()
    st.subheader(f"📄 Hasil: {bab_pilihan}")
    st.write(teks)
    
    # BAGIAN LISENSI - Dibuat statis agar tidak hilang
    st.info("🔓 **Aktivasi Download Dokumen**")
    col_lic1, col_lic2 = st.columns([2, 1])
    with col_lic1:
        # Key unik 'lic_input' agar tidak bentrok
        user_license = st.text_input("Masukkan Kode Lisensi Anda:", type="password", key=f"lic_{bab_pilihan}")
    with col_lic2:
        st.write("") # Spacer
        st.link_button("📲 Beli Kode via WhatsApp", f"https://wa.me/6283173826717")

    # LOGIKA DOWNLOAD
    if user_license == generate_license_logic(nama_user):
        st.success("✅ Lisensi Aktif!")
        doc = Document()
        doc.add_heading(f"{bab_pilihan} - {topik}", 0)
        doc.add_paragraph(teks)
        bio = BytesIO()
        doc.save(bio)
        st.download_button(f"📥 Download {bab_pilihan} (.docx)", data=bio.getvalue(), file_name=f"{bab_pilihan}_{nama_user}.docx")
    elif user_license != "":
        st.error("❌ Kode Lisensi tidak valid untuk nama tersebut.")
else:
    st.info("Silakan klik tombol 'Generate' di atas untuk memulai.")
