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
    return f"PRO-{nama_clean}-{hari_ini}-SKR"

# --- 3. INISIALISASI PENYIMPANAN PROGRESS ---
if 'database_skripsi' not in st.session_state:
    st.session_state['database_skripsi'] = {} # Menyimpan hasil tiap bab: {'Bab 1': 'teks...', 'Bab 2': 'teks...'}

# --- 4. TAMPILAN ---
st.set_page_config(page_title="SkripsiGen Pro - Progress Saved", layout="wide")

with st.expander("🛠️ Admin Panel (Owner Only)"):
    kunci_admin = st.text_input("Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        st.subheader("Generator Kode Lisensi")
        nama_pembeli = st.text_input("Nama Pembeli:")
        if st.button("Generate Kode"):
            st.code(generate_license_logic(nama_pembeli))

st.title("🎓 SkripsiGen Pro v6.3")

# --- FORM IDENTITAS ---
col_id1, col_id2 = st.columns(2)
with col_id1:
    nama_user = st.text_input("👤 Nama Lengkap Anda:", placeholder="Budi Santoso", key="main_nama")
with col_id2:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Analisis Strategi...", key="main_judul")

st.divider()

# --- TAB SISTEM ---
tab_buat, tab_revisi = st.tabs(["📝 Buat/Lihat Draf", "🔄 Fitur Revisi Dosen"])

with tab_buat:
    col_set1, col_set2 = st.columns(2)
    with col_set1:
        metode = st.selectbox("🔬 Pilih Metode:", ["Kuantitatif", "Kualitatif", "R&D"])
    with col_set2:
        bab_pilihan = st.selectbox("📄 Pilih Bab untuk Dikerjakan/Dilihat:", 
                                  ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", 
                                   "Lampiran: Instrumen", "Lampiran: Surat Izin"])

    # Cek apakah bab ini sudah pernah di-generate sebelumnya
    sudah_ada = bab_pilihan in st.session_state['database_skripsi']

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🚀 Generate Baru"):
            if topik and nama_user:
                with st.spinner(f"Menyusun {bab_pilihan}..."):
                    prompt = f"Judul: {topik}\nNama: {nama_user}\nTugas: Buatkan draf {bab_pilihan} {metode} formal."
                    try:
                        response = model.generate_content(prompt)
                        st.session_state['database_skripsi'][bab_pilihan] = response.text
                        st.rerun() # Refresh agar tampilan update
                    except Exception as e:
                        st.error(f"Error: {e}")
            else: st.warning("Isi Nama & Judul!")
    
    with col_btn2:
        if sudah_ada:
            st.success(f"✅ Data {bab_pilihan} tersedia di memori. Silakan scroll ke bawah untuk melihat/download.")

with tab_revisi:
    st.info("Fitur revisi akan memperbarui draf yang sudah ada di memori.")
    catatan = st.text_area("✍️ Masukkan Catatan Dosen untuk Bab yang dipilih:")
    if st.button("Proses Revisi 🚀"):
        if catatan and topik:
            with st.spinner("Mengolah revisi..."):
                prompt_rev = f"Revisi {bab_pilihan} judul {topik} berdasarkan: {catatan}. Tulis ulang."
                response = model.generate_content(prompt_rev)
                st.session_state['database_skripsi'][bab_pilihan] = response.text
                st.rerun()

# --- AREA HASIL & DOWNLOAD (PERSISTENT) ---
if bab_pilihan in st.session_state['database_skripsi']:
    teks_hasil = st.session_state['database_skripsi'][bab_pilihan]
    st.divider()
    st.subheader(f"📄 Hasil Pengerjaan: {bab_pilihan}")
    st.write(teks_hasil)
    
    # Bagian Aktivasi
    st.info("🔓 **Aktivasi Download**")
    col_dl1, col_dl2 = st.columns([2, 1])
    with col_dl1:
        user_license = st.text_input(f"Masukkan Kode Lisensi ({nama_user}):", type="password")
    with col_dl2:
        st.write("") 
        st.link_button("📲 Beli Kode via WA", f"https://wa.me/6283173826717")

    if user_license == generate_license_logic(nama_user):
        st.success("✅ Lisensi Aktif!")
        doc = Document()
        doc.add_heading(bab_pilihan, 0)
        doc.add_paragraph(teks_hasil)
        bio = BytesIO()
        doc.save(bio)
