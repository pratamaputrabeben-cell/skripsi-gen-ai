import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime
import random
import time

# --- 1. KONEKSI MULTI-KEY ---
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

# --- 2. DATABASE SESI ---
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'loading' not in st.session_state: st.session_state['loading'] = False

# --- 3. LOGIKA LISENSI ---
def gen_lic(n):
    d = datetime.now().strftime("%d%m")
    nm = n.split(' ')[0].upper() if n else "USER"
    return f"PRO-{nm}-{d}-SKR"

# --- 4. UI SETUP ---
st.set_page_config(page_title="SkripsiGen Pro v8.39", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.success("✅ Engine: Loop-Free Stabilizer")
    st.info("Gunakan Lampiran untuk Surat Izin & Kuesioner Lengkap.")
    
    st.divider()
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Contoh: Beny")
    user_lic = st.text_input("🔑 Kode Lisensi:", type="password")
    
    st.divider()
    with st.expander("🛠️ MENU OWNER"):
        pw = st.text_input("Admin Pass:", type="password")
        if pw == "BEBEN-BOSS":
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate ✨"): st.code(gen_lic(pbl))

# --- 5. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.39")
st.caption("Status: Optimized Stability | Jalur: Multi-Key")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Analisis Kinerja...")
    lokasi = st.text_input("📍 Lokasi:", value="SMK PGRI 1 Kabupaten Lahat")
with c2:
    kota = st.text_input("🏙️ Kota:", value="Lahat")
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", [
    "Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", 
    "Lampiran: Surat Izin, Kuesioner & Kisi-kisi"
])

# --- FUNGSI GENERATE (TANPA RECURSION ERROR) ---
def jalankan_proses(target_bab=None, catatan_dosen=""):
    bab_aktif = target_bab if target_bab else pil_bab
    
    if topik and nama_user:
        with st.spinner(f"Sedang memproses {bab_aktif}..."):
            for i in range(3):
                try:
                    model = inisialisasi_ai()
                    if "Lampiran" in bab_aktif:
                        prompt = f"Buat Lampiran Skripsi {nama_user} judul '{topik}' di {lokasi}, {kota}. Wajib: Surat Izin, Kuesioner Pra-Riset, Kuesioner PST Utama, Kisi-kisi, dan Informed Consent."
                    else:
                        rev_msg = f"REVISI DOSEN: {catatan_dosen}" if catatan_dosen else ""
                        prompt = f"Susun draf {bab_aktif} skripsi {metode} judul '{topik}' di {lokasi}. {rev_msg}. Ref RIIL 2023-2026, APA 7th, Deep Paraphrase."
                    
                    res = model.generate_content(prompt)
                    # SIMPAN DATA
                    st.session_state['db'][bab_aktif] = res.text
                    # SELESAI & TAMPILKAN
                    st.success(f"{bab_aktif} Berhasil Disusun!")
                    return # Keluar dari fungsi tanpa rerun berlebihan
                except Exception as e:
                    if "429" in str(e):
                        time.sleep(5)
                    else:
                        st.error(f"Error: {e}"); break
    else: st.warning("Isi Nama & Judul!")

if st.button("🚀 Susun Bagian Terpilih"):
    jalankan_proses()

# --- 6. BOX OUTPUT ---
if st.session_state['db']:
    st.divider()
    # Menampilkan bab yang sudah ada di database
    for b in sorted(st.session_state['db'].keys()):
        content = st.session_state['db'][b]
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            
            if "Lampiran" not in b:
                catatan = st.text_area(f"✍️ Revisi Dosen untuk {b}:", key=f"rev_input_{b}")
                if st.button(f"🔄 Jalankan Revisi {b}", key=f"rev_btn_{b}"):
                    jalankan_proses(target_bab=b, catatan_dosen=catatan)
            
            # Tampilkan 500 karakter awal saja biar nggak berat
            st.markdown(content[:500] + "...")
            with st.expander("Buka Dokumen & Laporan Audit"):
                st.markdown(content)
                if user_lic == gen_lic(nama_user):
                    doc = Document()
                    doc.add_heading(b, 0); doc.add_paragraph(content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download Word", data=bio.getvalue(), file_name=f"{b}.docx", key=f"dl_{b}")
                else: st.warning("Gunakan lisensi untuk download.")
