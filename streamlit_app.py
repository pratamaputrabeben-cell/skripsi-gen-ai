import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime
import random
import time

# --- 1. KONEKSI API ---
ALL_KEYS = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])

def inisialisasi_ai():
    key_aktif = random.choice(ALL_KEYS)
    genai.configure(api_key=key_aktif)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for target in ['gemini-1.5-flash', 'gemini-1.5-pro']:
            for real_model in available_models:
                if target in real_model: return genai.GenerativeModel(real_model)
        return genai.GenerativeModel(available_models[0])
    except: return genai.GenerativeModel('gemini-1.5-flash')

if 'db' not in st.session_state: st.session_state['db'] = {}

# --- 2. UI SETUP ---
st.set_page_config(page_title="SkripsiGen Pro v8.34", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.success("✅ Lampiran & Instrumen Ready")
    st.info("Pilih 'Lampiran' untuk mendapatkan Surat Izin & Kuesioner Lapangan.")
    
    st.divider()
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Contoh: Beny")
    user_lic = st.text_input("🔑 Kode Lisensi:", type="password")
    
    # --- LOGIKA LISENSI ---
    def gen_lic(n):
        d = datetime.now().strftime("%d%m")
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{d}-SKR"

    st.divider()
    with st.expander("🛠️ MENU OWNER"):
        pw = st.text_input("Admin Pass:", type="password")
        if pw == "BEBEN-BOSS":
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate ✨"): st.code(gen_lic(pbl))

# --- 3. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.34")
st.caption(f"Status: Full Toolkit Active | Jalur: Multi-Key")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Analisis Pengetahuan...")
    lokasi = st.text_input("📍 Lokasi:", value="SMK PGRI 1 Kabupaten Lahat")
with c2:
    kota = st.text_input("🏙️ Kota:", value="Lahat")
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
# Penambahan opsi Lampiran secara spesifik
pil_bab = st.selectbox("📄 Pilih Bagian:", [
    "Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", 
    "Lampiran: Surat Izin & Instrumen Lapangan"
])

def jalankan_proses(target_bab=None, catatan_dosen=""):
    bab_yg_diproses = target_bab if target_bab else pil_bab
    if topik and nama_user:
        placeholder = st.empty()
        for i in range(3):
            try:
                with placeholder.container():
                    st.spinner(f"Menyusun {bab_yg_diproses}...")
                    model = inisialisasi_ai()
                    
                    # PROMPT KHUSUS LAMPIRAN VS BAB BIASA
                    if "Lampiran" in bab_yg_diproses:
                        prompt = f"""
                        Buatkan dokumen LAMPIRAN PENELITIAN untuk mahasiswa bernama {nama_user} dengan judul '{topik}' di {lokasi}.
                        Isi harus mencakup:
                        1. DRAFT SURAT PERMOHONAN IZIN OBSERVASI: Kepada Kepala Sekolah {lokasi}.
                        2. PEDOMAN WAWANCARA: Untuk Guru BK guna validasi data perilaku siswa.
                        3. KUESIONER PENELITIAN (SIAP PAKAI): Bagian Pengetahuan, Sikap, dan Tindakan (Skala Likert/Guttman).
                        4. Format profesional, rapi, dan siap cetak.
                        """
                    else:
                        inst_dosen = f"REVISI BERDASARKAN: {catatan_dosen}" if catatan_dosen else ""
                        prompt = f"Susun draf {bab_yg_diproses} skripsi {metode} judul '{topik}' di {lokasi}, {kota}. {inst_dosen}. Gunakan Referensi RIIL 2023-2026, APA 7th, dan Laporan Audit di akhir."
                    
                    res = model.generate_content(prompt)
                    st.session_state['db'][bab_yg_diproses] = res.text
                    st.rerun()
                    break
            except:
                time.sleep(5)
    else: st.warning("Isi Nama & Judul!")

if st.button("🚀 Susun Draf / Lampiran"):
    jalankan_proses()

# --- 4. BOX OUTPUT ---
if st.session_state['db']:
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            
            # Input untuk Ocehan Dosen jika bukan lampiran
            if "Lampiran" not in b:
                catatan = st.text_area(f"✍️ Catatan Dosen untuk {b}:", key=f"in_{b}")
                col1, col2 = st.columns([1, 4])
                if col1.button(f"🔄 Revisi {b}", key=f"btn_{b}"):
                    jalankan_proses(target_bab=b, catatan_dosen=catatan)
            
            st.markdown(content[:400] + "...")
            with st.expander("Buka Dokumen Lengkap"):
                st.markdown(content)
                if user_lic == gen_lic(nama_user):
                    doc = Document()
                    doc.add_heading(b, 0); doc.add_paragraph(content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download Word", data=bio.getvalue(), file_name=f"{b}.docx", key=f"d_{b}")
                else: st.warning("Gunakan lisensi untuk download.")
