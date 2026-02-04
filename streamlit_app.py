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
    # Lisensi unik berdasarkan Nama + Tanggal (Berubah tiap hari)
    hari_ini = datetime.now().strftime("%d%m")
    nama_clean = nama.split(' ')[0].upper() if nama else "USER"
    return f"PRO-{nama_clean}-{hari_ini}-SKR"

# --- 3. DATABASE SESI (MEMORY) ---
if 'db' not in st.session_state:
    st.session_state['db'] = {}
if 'pustaka_koleksi' not in st.session_state:
    st.session_state['pustaka_koleksi'] = ""

# --- 4. TAMPILAN DASHBOARD ---
st.set_page_config(page_title="SkripsiGen Pro v7.7 - Ultimate Edition", layout="wide")

# ADMIN PANEL TERSEMBUNYI
with st.expander("🛠️ Admin Panel (Owner Only)"):
    kunci_admin = st.text_input("Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        pembeli = st.text_input("Nama Pembeli:")
        if st.button("Generate Kode Lisensi"):
            st.code(generate_license_logic(pembeli))

st.title("🎓 SkripsiGen Pro v7.7")
st.caption("Asisten Skripsi Berbasis AI dengan Standar Akademik Tinggi & Referensi Terbaru.")

# --- 5. INPUT IDENTITAS PENELITIAN ---
col_id1, col_id2 = st.columns(2)
with col_id1:
    nama_user = st.text_input("👤 Nama Lengkap Mahasiswa:", placeholder="Contoh: Budi Santoso")
    topik = st.text_input("📝 Judul Lengkap Skripsi:", placeholder="Contoh: Pengaruh Disiplin terhadap Kinerja...")
with col_id2:
    lokasi_penelitian = st.text_input("📍 Lokasi Spesifik (Instansi/Sekolah):", placeholder="Contoh: SMA Negeri 1 Jakarta")
    kab_prov = st.text_input("🏙️ Kota & Provinsi:", placeholder="Contoh: Jakarta Selatan, DKI Jakarta")

st.divider()

# --- 6. PENGATURAN SKRIPSI ---
c_opt1, c_opt2, c_opt3 = st.columns([1, 1, 1])
with c_opt1:
    metode = st.selectbox("🔬 Metode Penelitian:", ["Kuantitatif", "Kualitatif", "R&D"])
with c_opt2:
    bab_pilihan = st.selectbox("📄 Pilih Bagian pengerjaan:", 
                              ["Bab 1: Pendahuluan", 
                               "Bab 2: Tinjauan Pustaka", 
                               "Bab 3: Metodologi Penelitian", 
                               "Bab 4: Hasil dan Pembahasan", 
                               "Bab 5: Penutup", 
                               "Lampiran: Instrumen Penelitian", 
                               "Lampiran: Surat Izin Penelitian"])
with c_opt3:
    st.write("📅 **Filter Referensi:**")
    st.success("Aktif: Maksimal 3 Tahun Terakhir")

tab_buat, tab_revisi = st.tabs(["📝 Buat Draf Baru", "🔄 Revisi Catatan Dosen"])

# --- 7. MESIN PROMPT (LOGIKA UTAMA) ---
def dapatkan_prompt_final(tipe, t, n, m, lok, kota, p_lama, c=""):
    tahun_skrg = 2026
    rentang = f"{tahun_skrg-3} hingga {tahun_skrg}" # 2023-2026
    instruksi_pustaka = f"Tambahkan referensi dari bab sebelumnya: {p_lama}" if p_lama else ""
    
    # Logika instruksi per Bab
    if "Bab 1" in tipe:
        instruksi = f"Buat Latar Belakang Piramida Terbalik. Mulai data makro Nasional/Provinsi, data Kota {kota}, hingga fenomena nyata di {lok}. Wajib sertakan data statistik tahun {rentang}."
    elif "Bab 2" in tipe:
        instruksi = f"""BEDAH JUDUL '{t}' PER VARIABEL:
        1. Buat sub-bab landasan teori untuk SETIAP kata kunci/variabel utama dalam judul secara mendalam.
        2. Sertakan definisi ahli, indikator, dan faktor yang mempengaruhi untuk tiap variabel.
        3. Semua sitasi/kutipan WAJIB dari tahun {rentang}.
        4. Tambahkan penelitian terdahulu yang relevan tahun {rentang}.
        5. Buat Kerangka Berpikir & Hipotesis (jika Kuantitatif)."""
    elif "Instrumen" in tipe:
        instruksi = f"Buatkan draf instrumen penelitian (Kuesioner/Pedoman Wawancara) berdasarkan variabel dalam judul {t} untuk lokasi {lok}."
    elif "Surat Izin" in tipe:
        instruksi = f"Buatkan surat permohonan izin penelitian formal untuk {n} kepada pimpinan {lok}."
    else:
        instruksi = f"Susun {tipe} dengan standar akademik tinggi, lokasi di {lok}, dan referensi {rentang}."

    prompt_base = f"Bertindaklah sebagai Dosen Pembimbing Skripsi. Buatkan draf {tipe} untuk {n} dengan judul '{t}'. {instruksi}. {instruksi_pustaka}. Gunakan gaya bahasa formal, sitasi APA 7th Edition, dan akhiri dengan DAFTAR PUSTAKA (Wajib tahun {rentang})."
    
    if c:
        return f"REVISI {tipe} berdasarkan catatan dosen: '{c}'. Perbaiki draf berikut dengan tetap mengikuti aturan referensi {rentang}."
    return prompt_base

# --- 8. TOMBOL AKSI ---
with tab_buat:
    if st.button("🚀 Mulai Generate Draf"):
        if topik and nama_user and lokasi_penelitian:
            with st.spinner(f"Menyusun {bab_pilihan}..."):
                try:
                    p = dapatkan_prompt_final(bab_pilihan, topik, nama_user, metode, lokasi_penelitian, kab_prov, st.session_state['pustaka_koleksi'])
                    res = model.generate_content(p)
                    st.session_state['db'][bab_pilihan] = res.text
                    # Simpan pustaka secara kumulatif
                    if "DAFTAR PUSTAKA" in res.text.upper():
                        st.session_state['pustaka_koleksi'] += "\n" + res.text.upper().split("DAFTAR PUSTAKA")[-1]
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")
        else: st.warning("Mohon isi Nama, Judul, dan Lokasi terlebih dahulu!")

with tab_revisi:
    catatan = st.text_area("✍️ Masukkan Catatan Revisi dari
