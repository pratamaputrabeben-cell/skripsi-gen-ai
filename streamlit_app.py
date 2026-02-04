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
    st.error(f"Koneksi Gagal: {e}")
    st.stop()

# --- 2. LOGIKA LISENSI ---
def generate_license_logic(nama):
    hari_ini = datetime.now().strftime("%d%m")
    nama_clean = nama.split(' ')[0].upper() if nama else "USER"
    return f"PRO-{nama_clean}-{hari_ini}-SKR"

# --- 3. TAMPILAN UTAMA ---
st.set_page_config(page_title="SkripsiGen Pro - Revision Mode", layout="wide")

with st.expander("🛠️ Admin Panel (Owner Only)"):
    kunci_admin = st.text_input("Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        st.subheader("Generator Kode Lisensi")
        nama_pembeli = st.text_input("Nama Pembeli:")
        if st.button("Generate Kode"):
            st.code(generate_license_logic(nama_pembeli))

st.title("🎓 SkripsiGen Pro v6.0")

# --- TAB SISTEM ---
tab_buat, tab_revisi = st.tabs(["📝 Buat Baru", "🔄 Fitur Revisi Dosen"])

with tab_buat:
    col1, col2 = st.columns(2)
    with col1:
        nama_user = st.text_input("👤 Nama Lengkap:", key="nama_buat")
        topik = st.text_input("📝 Judul Skripsi:", key="judul_buat")
    with col2:
        metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"], key="metode_buat")
        bab_pilihan = st.selectbox("📄 Pilih Bab:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran: Instrumen", "Lampiran: Surat Izin"], key="bab_buat")

    if st.button("Generate Draf ✨"):
        # (Logika generate sama seperti sebelumnya...)
        st.info("Gunakan tab 'Fitur Revisi' jika Anda sudah punya draf dan ingin memperbaikinya.")

with tab_revisi:
    st.subheader("🛠️ Perbaikan Berdasarkan Masukan Dosen")
    st.warning("Fitur ini akan menyesuaikan bab yang dipilih hingga bab-bab selanjutnya agar tetap konsisten.")
    
    col_rev1, col_rev2 = st.columns(2)
    with col_rev1:
        nama_rev = st.text_input("👤 Nama Lengkap:", key="nama_rev")
        topik_lama = st.text_input("📝 Judul/Topik Saat Ini:", key="judul_rev")
        mulai_bab = st.selectbox("🎯 Mulai Revisi dari Bab:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4"], index=0)
    
    with col_rev2:
        catatan_dosen = st.text_area("✍️ Masukkan Catatan/Revisi dari Dosen:", 
                                    placeholder="Contoh: Ganti variabel X menjadi Y, atau tambahkan teori tentang Z di Bab 2...")

    if st.button("Proses Revisi Berantai 🚀"):
        if catatan_dosen and topik_lama and nama_rev:
            with st.spinner("Sedang merombak draf agar konsisten sesuai revisi..."):
                prompt_revisi = f"""
                Anda adalah Dosen Pembimbing Senior. Mahasiswa saya bernama {nama_rev} sedang merevisi skripsi berjudul '{topik_lama}'.
                
                CATATAN REVISI DOSEN:
                '{catatan_dosen}'
                
                TUGAS ANDA:
                1. Tulis ulang {mulai_bab} sesuai dengan catatan revisi tersebut.
                2. Jelaskan secara singkat perubahan apa saja yang harus dilakukan pada bab-bab SETELAHNYA agar tetap konsisten dengan revisi di {mulai_bab} ini.
                3. Pastikan bahasa sangat formal dan sitasi tetap ada.
                """
                try:
                    response = model.generate_content(prompt_revisi)
                    hasil_revisi = response.text
                    
                    st.success(f"✅ Revisi {mulai_bab} Berhasil Dibuat!")
                    st.markdown("### 📄 Hasil Revisi & Panduan Konsistensi")
                    st.write(hasil_revisi)
                    
                    # Cek Lisensi untuk Download
                    # (Gunakan sistem lisensi yang sama agar tetap cuan)
                    st.info("Gunakan kode lisensi di sidebar untuk download hasil revisi ini.")
                except Exception as e:
                    st.error(f"Gagal: {e}")
        else:
            st.warning("Mohon isi nama, judul, dan catatan revisi dosen!")

# --- SIDEBAR TETAP UNTUK LISENSI ---
with st.sidebar:
    st.header("🔓 Aktivasi & Lisensi")
    st.write("Hubungi admin untuk mendapatkan kode lisensi.")
    st.link_button("📲 Hubungi Admin", f"https://wa.me/6283173826717")
    user_license = st.text_input("Masukkan Kode Lisensi:", type="password", key="lic_key")
