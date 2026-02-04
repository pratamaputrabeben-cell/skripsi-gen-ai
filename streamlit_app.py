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

# --- 3. DATABASE SESI (PERSISTENT STORAGE) ---
if 'db' not in st.session_state:
    st.session_state['db'] = {} # Format: {'Bab 1': 'teks...', 'Bab 2': 'teks...'}
if 'pustaka_koleksi' not in st.session_state:
    st.session_state['pustaka_koleksi'] = ""

# --- 4. TAMPILAN DASHBOARD ---
st.set_page_config(page_title="SkripsiGen Pro v8.0", layout="wide")

with st.sidebar:
    st.title("🛡️ Panel Aktivasi")
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Budi Santoso")
    user_license = st.text_input("🔑 Kode Lisensi:", type="password")
    
    st.divider()
    st.write("Belum punya kode?")
    st.link_button("📲 Beli Lisensi (WA)", "https://wa.me/6283173826717")
    
    st.divider()
    if st.button("🗑️ Hapus Semua Dokumen"):
        st.session_state['db'] = {}
        st.session_state['pustaka_koleksi'] = ""
        st.rerun()

st.title("🎓 SkripsiGen Pro v8.0")
st.caption("Manajemen Dokumen Skripsi Otomatis | Referensi 2023-2026")

# --- 5. INPUT DATA ---
c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Pengaruh X terhadap Y...")
    lokasi = st.text_input("📍 Lokasi Penelitian:", placeholder="SMA Negeri 1 Jakarta")
with c2:
    kota = st.text_input("🏙️ Kota & Provinsi:", placeholder="Jakarta, DKI Jakarta")
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()

# --- 6. GENERATOR ---
col_gen1, col_gen2 = st.columns([2, 1])
with col_gen1:
    bab_pilihan = st.selectbox("📄 Pilih Bagian untuk di-Generate:", 
                              ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran: Instrumen", "Lampiran: Surat Izin"])
with col_gen2:
    st.write("") # Spacer
    btn_gen = st.button("🚀 Generate Sekarang")

if btn_gen:
    if topik and nama_user:
        with st.spinner(f"Menyusun {bab_pilihan}..."):
            tahun_skrg = 2026
            rentang = f"{tahun_skrg-3}-{tahun_skrg}"
            
            # Logika Prompt Khusus
            if "Bab 2" in bab_pilihan:
                prompt = f"Bedah judul {topik} per variabel. Buat landasan teori mendalam, indikator, dan penelitian terdahulu tahun {rentang} untuk mahasiswa {nama_user}. Gunakan sitasi APA 7th dan Daftar Pustaka."
            else:
                prompt = f"Buat draf {bab_pilihan} skripsi {metode} judul {topik} lokasi {lokasi}. Referensi wajib {rentang}. Gunakan sitasi APA 7th dan Daftar Pustaka."
            
            try:
                res = model.generate_content(prompt).text
                st.session_state['db'][bab_pilihan] = res
                if "DAFTAR PUSTAKA" in res.upper():
                    st.session_state['pustaka_koleksi'] += "\n" + res.upper().split("DAFTAR PUSTAKA")[-1]
                st.rerun()
            except Exception as e: st.error(f"Gagal: {e}")
    else: st.warning("Isi Nama di sidebar dan Judul di atas!")

st.divider()

# --- 7. DISPLAY HASIL DALAM BOX ---
st.subheader("📁 Koleksi Dokumen Anda")
if not st.session_state['db']:
    st.info("Belum ada dokumen yang di-generate.")
else:
    # Menampilkan setiap dokumen dalam box (expander/container)
    for bab, isi in st.session_state['db'].items():
        with st.container(border=True):
            col_header1, col_header2 = st.columns([5, 1])
            with col_header1:
                st.markdown(f"### 📄 {bab}")
            with col_header2:
                # Tombol Hapus per dokumen
                if st.button(f"🗑️ Hapus", key=f"del_{bab}"):
                    del st.session_state['db'][bab]
                    st.rerun()
            
            # Preview isi draf
            st.markdown(isi[:500] + "..." if len(isi) > 500 else isi)
            
            with st.expander("Lihat Selengkapnya & Download"):
                st.markdown(isi)
                st.divider()
                
                # Logika Aktivasi per Box
                if user_license == generate_license_logic(nama_user):
                    st.success("✅ Lisensi Aktif")
                    doc = Document()
                    doc.add_heading(bab, 0)
                    doc.add_paragraph(isi)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button(f"📥 Download {bab} (.docx)", data=bio.getvalue(), file_name=f"{bab}.docx", key=f"dl_{bab}")
                else:
                    st.warning("⚠️ Masukkan lisensi di sidebar untuk download.")
