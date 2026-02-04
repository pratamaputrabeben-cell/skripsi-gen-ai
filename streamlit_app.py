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

# --- 4. TAMPILAN ---
st.set_page_config(page_title="SkripsiGen Pro v7.5 - Ultimate", layout="wide")

with st.expander("🛠️ Admin Panel (Owner Only)"):
    kunci_admin = st.text_input("Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        st.subheader("Generator Kode Lisensi")
        pembeli = st.text_input("Nama Pembeli:")
        if st.button("Generate Kode"):
            st.code(generate_license_logic(pembeli))

st.title("🎓 SkripsiGen Pro v7.5")
st.info("Asisten Skripsi Standar Akademik - Lengkap dengan Sitasi & Daftar Pustaka Kumulatif.")

# --- 5. FORM IDENTITAS & LOKASI ---
c1, c2 = st.columns(2)
with c1:
    nama_user = st.text_input("👤 Nama Lengkap Anda:", placeholder="Budi Santoso")
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Pengaruh Disiplin terhadap Kinerja...")
with c2:
    lokasi_penelitian = st.text_input("📍 Lokasi Penelitian:", placeholder="SMA Negeri 1 / PT. Maju Jaya")
    kab_prov = st.text_input("🏙️ Kota & Provinsi:", placeholder="Contoh: Jakarta Selatan, DKI Jakarta")

st.divider()

# --- 6. KONTROL PENELITIAN ---
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    metode = st.selectbox("🔬 Metode Penelitian:", ["Kuantitatif", "Kualitatif", "R&D"])
with col_opt2:
    bab_pilihan = st.selectbox("📄 Pilih Bab/Dokumen:", 
                              ["Bab 1: Pendahuluan", 
                               "Bab 2: Tinjauan Pustaka", 
                               "Bab 3: Metodologi Penelitian", 
                               "Bab 4: Hasil dan Pembahasan", 
                               "Bab 5: Penutup", 
                               "Lampiran: Instrumen Penelitian", 
                               "Lampiran: Surat Izin Penelitian"])

tab_buat, tab_revisi = st.tabs(["📝 Buat/Lihat Draf", "🔄 Revisi Dosen"])

# --- 7. FUNGSI PROMPT ULTIMATE ---
def dapatkan_prompt_ultimate(tipe, t, n, m, lok, kota, p_lama, c=""):
    instruksi_pustaka = f"WAJIB masukkan referensi lama ini ke Daftar Pustaka: {p_lama}" if p_lama else ""
    
    if "Bab 1" in tipe:
        instruksi_khusus = f"Susun Latar Belakang Piramida Terbalik: Data Nasional/Provinsi, data Kota {kota}, hingga fenomena nyata di {lok}."
    elif "Bab 2" in tipe:
        instruksi_khusus = f"Bedah judul '{t}' menjadi variabel-variabel. Buat landasan teori untuk MASING-MASING variabel (Definisi ahli, indikator, faktor). Tambahkan penelitian terdahulu dan kerangka berpikir."
    elif "Surat Izin" in tipe:
        return f"Buatkan surat izin penelitian formal nama {n} lokasi {lok} judul {t}."
    elif "Instrumen" in tipe:
        return f"Buatkan instrumen {m} (kuesioner/pedoman) untuk judul {t} di {lok}."
    else:
        instruksi_khusus = f"Kerjakan {tipe} {m} di lokasi {lok}."

    if c:
        return f"REVISI {tipe} judul {t} berdasarkan catatan dosen: '{c}'. {instruksi_khusus}. {instruksi_pustaka}. Gunakan sitasi APA 7th."
    else:
        return f"Buat draf {tipe} skripsi {m} judul {t}. {instruksi_khusus}. {instruksi_pustaka}. WAJIB gunakan kutipan ahli dan akhiri dengan DAFTAR PUSTAKA APA Style 7th Edition."

# --- 8. PROSES GENERATE ---
with tab_buat:
    if st.button("🚀 Generate / Update Draf"):
        if topik and nama_user and lokasi_penelitian:
            with st.spinner(f"Sedang menyusun {bab_pilihan}..."):
                try:
                    prompt = dapatkan_prompt_ultimate(bab_pilihan, topik, nama_user, metode, lokasi_penelitian, kab_prov, st.session_state['pustaka_koleksi'])
                    res = model.generate_content(prompt)
                    st.session_state['db'][bab_pilihan] = res.text
                    # Simpan pustaka secara kumulatif
                    if "DAFTAR PUSTAKA" in res.text.upper():
                        st.session_state['pustaka_koleksi'] += "\n" + res.text.upper().split("DAFTAR PUSTAKA")[-1]
                    st.rerun()
                except Exception as e: st.error(f"Gagal: {e}")
        else: st.warning("Lengkapi Nama, Judul, dan Lokasi dulu ya!")

with tab_revisi:
    catatan_dosen = st.text_area("✍️ Masukkan Catatan/Revisi dari Dosen:")
    if st.button("Proses Revisi 🚀"):
        if catatan_dosen and topik:
            with st.spinner("Merevisi draf sesuai standar akademik..."):
                try:
                    prompt_rev = dapatkan_prompt_ultimate(bab_pilihan, topik, nama_user, metode, lokasi_penelitian, kab_prov, st.session_state['pustaka_koleksi'], catatan_dosen)
                    res = model.generate_content(prompt_rev)
                    st.session_state['db'][bab_pilihan] = res.text
                    st.rerun()
                except Exception as e: st.error(f"Gagal: {e}")

# --- 9. AREA HASIL & LISENSI (MODEL 6.4) ---
if bab_pilihan in st.session_state['db']:
    teks_hasil = st.session_state['db'][bab_pilihan]
    st.divider()
    st.subheader(f"📄 Hasil Pengerjaan: {bab_pilihan}")
    st.markdown(teks_hasil)
