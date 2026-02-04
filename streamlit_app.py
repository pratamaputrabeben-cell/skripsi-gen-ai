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

# --- 3. DATABASE SESI ---
if 'db' not in st.session_state:
    st.session_state['db'] = {}
if 'pustaka_koleksi' not in st.session_state:
    st.session_state['pustaka_koleksi'] = ""

# --- 4. TAMPILAN ---
st.set_page_config(page_title="SkripsiGen Pro - Data Fenomena", layout="wide")

with st.expander("🛠️ Admin Panel (Owner Only)"):
    kunci_admin = st.text_input("Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        pembeli = st.text_input("Nama Pembeli:")
        if st.button("Generate Kode"):
            st.code(generate_license_logic(pembeli))

st.title("🎓 SkripsiGen Pro v7.0")

# FORM IDENTITAS & LOKASI
col_id1, col_id2 = st.columns(2)
with col_id1:
    nama_user = st.text_input("👤 Nama Lengkap Anda:", placeholder="Budi Santoso")
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Analisis Pengaruh...")
with col_id2:
    lokasi_penelitian = st.text_input("📍 Lokasi Spesifik Penelitian:", placeholder="Contoh: SMA Negeri 1 Jakarta / PT. Maju Jaya")
    kab_prov = st.text_input("🏙️ Kota & Provinsi:", placeholder="Contoh: Jakarta Selatan, DKI Jakarta")

st.divider()

# KONTROL PENELITIAN
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    metode = st.selectbox("🔬 Metode Penelitian:", ["Kuantitatif", "Kualitatif", "R&D"])
with col_opt2:
    bab_pilihan = st.selectbox("📄 Pilih Bab/Dokumen:", 
                              ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", 
                               "Lampiran: Instrumen", "Lampiran: Surat Izin"])

tab_buat, tab_revisi = st.tabs(["📝 Buat/Lihat Draf", "🔄 Revisi Dosen"])

# FUNGSI PROMPT DENGAN LOGIKA DATA FENOMENA
def dapatkan_prompt_fenomena(tipe, t, n, m, lok, kota, p_lama, c=""):
    instruksi_pustaka = f"Sertakan daftar pustaka lama ini: {p_lama}" if p_lama else ""
    
    if "Bab 1" in tipe:
        instruksi_khusus = f"""
        Dalam Latar Belakang, susun data fenomena secara mengerucut (Piramida Terbalik):
        1. Mulai dari data/masalah di tingkat Provinsi/Nasional terkait {t}.
        2. Masuk ke data di tingkat Kabupaten/Kota ({kota}).
        3. Masuk ke fenomena nyata di lokasi penelitian ({lok}).
        4. Berikan argumen mengapa penelitian ini mendesak dilakukan di lokasi tersebut.
        """
    else:
        instruksi_khusus = f"Kerjakan {tipe} dengan fokus pada lokasi {lok}."

    if c:
        return f"Revisi {tipe} skripsi {m} judul {t} di {lok} berdasarkan: {c}. {instruksi_pustaka}. Gunakan kutipan APA 7th."
    else:
        return f"Buatkan draf {tipe} skripsi {m} judul {t}. {instruksi_khusus}. {instruksi_pustaka}. WAJIB gunakan kutipan dan Daftar Pustaka APA 7th."

with tab_buat:
    if st.button("🚀 Generate / Update Draf"):
        if topik and nama_user and lokasi_penelitian:
            with st.spinner(f"Menyusun {bab_pilihan} (Menganalisis data fenomena)..."):
                try:
                    p = dapatkan_prompt_fenomena(bab_pilihan, topik, nama_user, metode, lokasi_penelitian, kab_prov, st.session_state['pustaka_koleksi'])
                    res = model.generate_content(p)
                    st.session_state['db'][bab_pilihan] = res.text
                    if "DAFTAR PUSTAKA" in res.text.upper():
                        st.session_state['pustaka_koleksi'] = res.text.upper().split("DAFTAR PUSTAKA")[-1]
                    st.rerun()
                except Exception as e: st.error(f"Gagal: {e}")
        else: st.warning("Pastikan Nama, Judul, dan Lokasi Penelitian sudah diisi!")

with tab_revisi:
    catatan = st.text_area("✍️ Catatan Revisi Dosen:")
    if st.button("Proses Revisi 🚀"):
        if catatan and topik:
            with st.spinner("Merevisi draf..."):
                try:
                    p = dapatkan_prompt_fenomena(bab_pilihan, topik, nama_user, metode, lokasi_penelitian, kab_prov, st.session_state['pustaka_koleksi'], catatan)
                    res = model.generate_content(p)
                    st.session_state['db'][bab_pilihan] = res.text
                    st.rerun()
                except Exception as e: st.error(f"Gagal: {e}")

# --- AREA HASIL & LISENSI ---
if bab_pilihan in st.session_state['db']:
    teks = st.session_state['db'][bab_pilihan]
    st.divider()
    st.subheader(f"📄 Hasil: {bab_pilihan}")
    st.markdown(teks)
    
    st.info("🔓 **Aktivasi Download Dokumen**")
    col_lic1, col_lic2 = st.columns([2, 1])
    with col_lic1:
        user_license = st.text_input("Masukkan Kode Lisensi Anda:", type="password", key=f"lic_{bab_pilihan}")
    with col_lic2:
        st.write("") 
        st.link_button("📲 Beli Kode via WA", f"https://wa.me/6283173826717")

    if user_license == generate_license_logic(nama_user):
        st.success("✅ Lisensi Aktif!")
        doc = Document()
        doc.add_heading(f"{bab_pilihan} - {topik}", 0)
        doc.add_paragraph(teks)
        bio = BytesIO()
        doc.save(bio)
        st.download_button(f"📥 Download {bab_pilihan} (.docx)", data=bio.getvalue(), file_name=f"{bab_pilihan}.docx")
    elif user_license != "":
        st.error("❌ Kode Lisensi tidak cocok.")
