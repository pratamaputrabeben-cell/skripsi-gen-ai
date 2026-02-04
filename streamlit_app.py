import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime
import random
import time # Penambahan library untuk jeda otomatis

# --- 1. KONEKSI MULTI-KEY & AUTO-MODEL ---
ALL_KEYS = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])

def inisialisasi_ai():
    # Rotasi Key secara cerdas setiap kali dipanggil
    key_aktif = random.choice(ALL_KEYS)
    genai.configure(api_key=key_aktif)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for target in ['gemini-1.5-flash', 'gemini-1.5-pro']:
            for real_model in available_models:
                if target in real_model: return genai.GenerativeModel(real_model)
        return genai.GenerativeModel(available_models[0])
    except: return genai.GenerativeModel('gemini-1.5-flash')

# --- 2. LOGIKA LISENSI ---
def gen_lic(n):
    d = datetime.now().strftime("%d%m")
    nm = n.split(' ')[0].upper() if n else "USER"
    return f"PRO-{nm}-{d}-SKR"

if 'db' not in st.session_state: st.session_state['db'] = {}

# --- 3. UI SETUP ---
st.set_page_config(page_title="SkripsiGen Pro v8.30", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.success("✅ Anti-Limit: Auto-Retry Active")
    st.info("Sistem akan mencoba ulang otomatis jika jalur sibuk.")
    
    st.divider()
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Contoh: Beny")
    user_lic = st.text_input("🔑 Kode Lisensi:", type="password")
    
    st.divider()
    with st.expander("🛠️ MENU OWNER"):
        pw = st.text_input("Admin Pass:", type="password")
        if pw == "BEBEN-BOSS":
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate ✨"): st.code(gen_lic(pbl))

# --- 4. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.30")
st.caption(f"Status: Optimasi Jalur Aktif | Standar Akademik 2026")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Analisis Kinerja...")
    lokasi = st.text_input("📍 Lokasi:", placeholder="Contoh: PT. Maju")
with c2:
    kota = st.text_input("🏙️ Kota:", placeholder="Contoh: Jakarta")
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran"])

# --- FUNGSI GENERATE DENGAN AUTO-RETRY ---
def jalankan_proses(mode="Normal"):
    if topik and nama_user:
        placeholder = st.empty()
        # Percobaan maksimal 3 kali jika sibuk
        for i in range(3):
            try:
                with placeholder.container():
                    st.spinner(f"Sedang mengaudit data (Percobaan {i+1}/3)...")
                    # Inisialisasi ulang model tiap percobaan untuk ganti Key
                    model = inisialisasi_ai() 
                    
                    prompt = f"""
                    Susun draf {pil_bab} skripsi {metode} judul '{topik}' di {lokasi}, {kota}.
                    WAJIB: Referensi RIIL 2023-2026, APA 7th, Bedah Variabel, dan Deep Paraphrase.
                    Laporan Audit di akhir: Sebutkan Status Referensi dan Skor Orisinalitas (>95%).
                    """
                    res = model.generate_content(prompt)
                    st.session_state['db'][pil_bab] = res.text
                    st.rerun()
                    break # Keluar loop jika sukses
            except Exception as e:
                if "429" in str(e):
                    # Jika kena limit, tunggu 5 detik lalu coba lagi
                    st.warning(f"Jalur padat, sedang mencari celah... (Tunggu 5 detik)")
                    time.sleep(5)
                else:
                    st.error(f"Kendala: {e}")
                    break
    else: st.warning("Lengkapi Nama & Judul!")

if st.button("🚀 Susun Draf & Kalibrasi"):
    jalankan_proses()

# --- 5. BOX OUTPUT ---
if st.session_state['db']:
    st.divider()
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 1, 1])
            col1.markdown(f"### 📄 {b}")
            if col2.button(f"🔄 Re-Kalibrasi", key=f"re_{b}"):
                jalankan_proses(mode="Re-Calibrate")
            if col3.button("🗑️ Hapus", key=f"del_{b}"):
                del st.session_state['db'][b]; st.rerun()
            
            st.markdown(content[:400] + "...")
            with st.expander("Buka Draf & Hasil Audit"):
                st.markdown(content)
                if user_lic == gen_lic(nama_user):
                    doc = Document()
                    doc.add_heading(b, 0); doc.add_paragraph(content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download Word", data=bio.getvalue(), file_name=f"{b}.docx", key=f"d_{b}")
                else: st.warning("Masukkan lisensi untuk download.")
