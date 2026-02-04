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

# --- 3. DATABASE SESI (TERMASUK STORAGE PUSTAKA) ---
if 'db' not in st.session_state:
    st.session_state['db'] = {}
if 'pustaka_koleksi' not in st.session_state:
    st.session_state['pustaka_koleksi'] = ""

# --- 4. TAMPILAN ---
st.set_page_config(page_title="SkripsiGen Pro - Cumulative Ref", layout="wide")

with st.expander("🛠️ Admin Panel (Owner Only)"):
    kunci_admin = st.text_input("Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        pembeli = st.text_input("Nama Pembeli:")
        if st.button("Generate Kode"):
            st.code(generate_license_logic(pembeli))

st.title("🎓 SkripsiGen Pro v6.9")

# FORM IDENTITAS
c1, c2 = st.columns(2)
with c1:
    nama_user = st.text_input("👤 Nama Lengkap Anda:", placeholder="Budi Santoso")
with c2:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Analisis Strategi...")

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

# FUNGSI PROMPT DENGAN MEMORI PUSTAKA
def dapatkan_prompt_kumulatif(tipe, t, n, m, p_lama, c=""):
    instruksi_pustaka = f"WAJIB: Masukkan referensi lama berikut ke dalam Daftar Pustaka: {p_lama}" if p_lama else ""
    
    if "Surat Izin" in tipe:
        return f"Buatkan draf surat izin penelitian formal nama {n} judul {t}."
    elif "Instrumen" in tipe:
        return f"Buatkan instrumen penelitian {m} untuk judul {t}."
    elif c:
        return f"Revisi {tipe} skripsi {m} judul {t} berdasarkan: {c}. {instruksi_pustaka}. Gunakan kutipan dan Daftar Pustaka APA 7th Edition."
    else:
        return f"Buatkan draf {tipe} skripsi {m} judul {t}. {instruksi_pustaka}. WAJIB gunakan kutipan di teks dan sertakan Daftar Pustaka (Gabungan referensi lama dan baru) di akhir."

with tab_buat:
    if st.button("🚀 Generate / Update Draf"):
        if topik and nama_user:
            with st.spinner(f"Menyusun {bab_pilihan} (Sinkronisasi Pustaka)..."):
                try:
                    p = dapatkan_prompt_kumulatif(bab_pilihan, topik, nama_user, metode, st.session_state['pustaka_koleksi'])
                    res = model.generate_content(p)
                    st.session_state['db'][bab_pilihan] = res.text
                    
                    # Ambil bagian Daftar Pustaka dari hasil untuk disimpan ke memori
                    if "DAFTAR PUSTAKA" in res.text.upper():
                        parts = res.text.upper().split("DAFTAR PUSTAKA")
                        st.session_state['pustaka_koleksi'] = parts[-1]
                    
                    st.rerun()
                except Exception as e: st.error(f"Gagal: {e}")
        else: st.warning("Isi Nama & Judul!")

with tab_revisi:
    catatan = st.text_area("✍️ Catatan Revisi Dosen:")
    if st.button("Proses Revisi 🚀"):
        if catatan and topik:
            with st.spinner("Merevisi & Sinkron Pustaka..."):
                try:
                    p = dapatkan_prompt_kumulatif(bab_pilihan, topik, nama_user, metode, st.session_state['pustaka_koleksi'], catatan)
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
