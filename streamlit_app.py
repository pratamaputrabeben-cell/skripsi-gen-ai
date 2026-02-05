import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import re

# --- 1. CONFIG ENGINE ---
def inisialisasi_ai():
    try:
        keys = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])
        key_aktif = random.choice(keys)
        genai.configure(api_key=key_aktif)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Masalah API: {e}")
        return None

# Inisialisasi Database Sederhana
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

# --- 2. FUNGSI RAPIKAN WORD ---
def buat_dokumen_rapi(judul_bab, isi_teks):
    doc = Document()
    for sec in doc.sections:
        sec.left_margin, sec.top_margin = Cm(4), Cm(3)
        sec.right_margin, sec.bottom_margin = Cm(3), Cm(3)
    
    style = doc.styles['Normal']
    style.font.name, style.font.size = 'Times New Roman', Pt(12)
    
    teks_clean = re.sub(r"^(Tentu|Berikut|Ini adalah|Sesuai).*?\n", "", isi_teks, flags=re.IGNORECASE)
    teks_clean = teks_clean.replace("**", "").replace("---", "")

    head = doc.add_heading(judul_bab.upper(), 0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in head.runs:
        run.font.name, run.font.size, run.bold = 'Times New Roman', Pt(14), True

    for p_text in teks_clean.split('\n'):
        t = p_text.strip()
        if t:
            p = doc.add_paragraph()
            fmt = p.paragraph_format
            fmt.line_spacing, fmt.alignment = 1.5, WD_ALIGN_PARAGRAPH.JUSTIFY
            if re.match(r"^(\d+\.\d+)", t):
                run = p.add_run(t); run.bold = True
            else:
                p.add_run(t); fmt.first_line_indent = Inches(0.5)
    
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 3. UI SIDEBAR ---
st.set_page_config(page_title="SkripsiGen Pro v8.57", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    
    # Gunakan key agar value tidak hilang saat rerun
    st.session_state['user_data']['nama'] = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    
    def gen_lic(n):
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{datetime.now().strftime('%d%m')}-SKR"

    st.divider()
    st.markdown("### 🛠️ PANEL ADMIN")
    pw = st.text_input("Password Admin:", type="password")
    if pw == "RAHASIA-BEBEN-2026":
        st.info("Halo Bos Beben!")
        pbl = st.text_input("Nama Pembeli Baru:")
        if st.button("Generate License"):
            st.code(gen_lic(pbl))
    
    if st.button("🗑️ Reset Semua"):
        st.session_state['db'] = {}
        st.rerun()

# --- 4. TAMPILAN UTAMA (ANTI CRASH) ---
st.title("🎓 SkripsiGen Pro v8.57")
st.caption("Stable Engine | 4333 Formatting")

# Input diletakkan di container agar lebih stabil
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        st.session_state['user_data']['topik'] = st.text_input("📝 Judul Skripsi:", value=st.session_state['user_data']['topik'])
        st.session_state['user_data']['lokasi'] = st.text_input("📍 Lokasi:", value=st.session_state['user_data']['lokasi'])
    with c2:
        st.session_state['user_data']['kota'] = st.text_input("🏙️ Kota:", value=st.session_state['user_data']['kota'])
        metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran"])

if st.button("🚀 Susun Sekarang"):
    if st.session_state['user_data']['topik'] and st.session_state['user_data']['nama']:
        with st.spinner("Menyusun..."):
            model = inisialisasi_ai()
            if model:
                prompt = f"Susun {pil_bab} skripsi {metode} judul '{st.session_state['user_data']['topik']}' di {st.session_state['user_data']['lok
