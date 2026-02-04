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
st.set_page_config(page_title="SkripsiGen Pro v7.8", layout="wide")

with st.expander("🛠️ Admin Panel"):
    kunci_admin = st.text_input("Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        pembeli = st.text_input("Nama Pembeli:")
        if st.button("Generate Kode"):
            st.code(generate_license_logic(pembeli))

st.title("🎓 SkripsiGen Pro v7.8")
st.caption("Standar Akademik Tinggi | Referensi 2023-2026")

# --- 5. INPUT DATA ---
c1, c2 = st.columns(2)
with c1:
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Budi Santoso")
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Pengaruh X terhadap Y...")
with c2:
    lokasi = st.text_input("📍 Lokasi Penelitian:", placeholder="SMA Negeri 1 Jakarta")
    kota = st.text_input("🏙️ Kota & Provinsi:", placeholder="Jakarta, DKI Jakarta")

st.divider()

# --- 6. PENGATURAN ---
o1, o2 = st.columns(2)
with o1:
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])
with o2:
    bab_pilihan = st.selectbox("📄 Pilih Bab:", 
                              ["Bab 1: Pendahuluan", "Bab 2: Tinjauan Pustaka", "Bab 3: Metodologi Penelitian", 
                               "Bab 4: Hasil dan Pembahasan", "Bab 5: Penutup", "Lampiran: Instrumen", "Lampiran: Surat Izin"])

tab1, tab2 = st.tabs(["📝 Buat Baru", "🔄 Revisi Dosen"])

# --- 7. FUNGSI PROMPT ---
def buat_prompt(tipe, t, n, m, l, k, p_lama, rev=""):
    thn = 2026
    rentang = f"{thn-3} s/d {thn}"
    pustaka_msg = f"Gunakan referensi lama ini jika relevan: {p_lama}" if p_lama else ""
    
    if "Bab 1" in tipe:
        desc = f"Latar belakang piramida terbalik dari Nasional ke {k} lalu ke {l}. Gunakan data statistik {rentang}."
    elif "Bab 2" in tipe:
        desc = f"Bedah judul {t} per variabel. Teori mendalam per kata kunci, indikator, dan penelitian terdahulu {rentang}."
    elif "Surat" in tipe:
        return f"Buat surat izin penelitian formal untuk {n} judul {t} lokasi {l}."
    else:
        desc = f"Susun {tipe} dengan referensi {rentang} di lokasi {l}."

    base = f"Buatkan draf {tipe} skripsi {m} judul {t} untuk mahasiswa {n}. {desc}. {pustaka_msg}. Wajib sitasi APA 7th dan Daftar Pustaka {rentang}."
    
    if rev:
        return f"REVISI {tipe} berdasarkan catatan: {rev}. Judul: {t}. Referensi wajib {rentang}."
    return base

# --- 8. TOMBOL AKSI ---
with tab1:
    if st.button("🚀 Mulai Generate Sekarang"):
        if topik and nama_user:
            with st.spinner("Sedang menyusun draf akademik..."):
                try:
                    p = buat_prompt(bab_pilihan, topik, nama_user, metode, lokasi, kota, st.session_state['pustaka_koleksi'])
                    res = model.generate_content(p).text
                    st.session_state['db'][bab_pilihan] = res
                    if "DAFTAR PUSTAKA" in res.upper():
                        st.session_state['pustaka_koleksi'] += "\n" + res.upper().split("DAFTAR PUSTAKA")[-1]
                    st.rerun()
                except Exception as e: st.error(f"Gagal: {e}")
        else: st.warning("Nama dan Judul wajib diisi!")

with tab2:
    catatan_rev = st.text_area("✍️ Masukkan Catatan Revisi Dosen:")
    if st.button("Proses Perbaikan 🚀"):
        if catatan_rev and topik:
            with st.spinner("Memperbaiki draf..."):
                try:
                    p_rev = buat_prompt(bab_pilihan, topik, nama_user, metode, lokasi, kota, st.session_state['pustaka_koleksi'], rev=catatan_rev)
                    res_rev = model.generate_content(p_rev).text
                    st.session_state['db'][bab_pilihan] = res_rev
                    st.rerun()
                except Exception as e: st.error(f"Gagal: {e}")

# --- 9. HASIL & LISENSI ---
if bab_pilihan in st.session_state['db']:
    konten = st.session_state['db'][bab_pilihan]
    st.divider()
    st.subheader(f"📄 Hasil {bab_pilihan}")
    st.markdown(konten)
    
    st.info("🔓 **Aktivasi Download Dokumen**")
    l1, l2 = st.columns([2, 1])
    with l1:
        lisensi_input = st.text_input("Masukkan Kode Lisensi:", type="password", key=f"key_{bab_pilihan}")
    with l2:
        st.write("")
        st.link_button("📲 Beli Kode via WA", f"https://wa.me/6283173826717")

    if lisensi_input == generate_license_logic(nama_user):
        st.success("✅ Lisensi Aktif!")
        doc = Document()
        doc.add_heading(bab_pilihan, 0)
        doc.add_paragraph(konten)
        bio = BytesIO()
        doc.save(bio)
        st.download_button("📥 Download Word (.docx)", data=bio.getvalue(), file_name=f"{bab_pilihan}.docx")
    elif lisensi_input != "":
        st.error("❌ Kode Salah!")
