import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import re

# --- 1. CONFIG HALAMAN (STABIL) ---
st.set_page_config(page_title="SkripsiGen Pro v8.77", page_icon="🎓", layout="wide")

# --- 2. DATABASE & SESSION STATE ---
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {
        "topik": "", 
        "lokasi": "SMK Negeri 2 Kabupaten Lahat", 
        "kota": "Lahat", 
        "nama": ""
    }

# --- 3. ENGINE SETUP (MULTI-KEY & FLASH MODE) ---
def inisialisasi_ai():
    try:
        # Mengambil daftar kunci dari Secrets Streamlit
        keys = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])
        key_aktif = random.choice(keys)
        genai.configure(api_key=key_aktif)
        
        # Menggunakan Gemini 1.5 Flash agar kuota awet dan tidak cepat habis
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"⚠️ Masalah API Key: {e}")
        st.stop()

# --- 4. FORMATTING ENGINE (4333 & Times New Roman) ---
def buat_dokumen_rapi(judul_bab, isi_teks):
    doc = Document()
    for sec in doc.sections:
        sec.left_margin, sec.right_margin = Cm(4), Cm(3)
        sec.top_margin, sec.bottom_margin = Cm(3), Cm(3)
    
    style = doc.styles['Normal']
    style.font.name, style.font.size = 'Times New Roman', Pt(12)
    
    # Header Bab
    head = doc.add_heading(judul_bab.upper(), 0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in head.runs:
        run.font.name, run.font.size, run.bold, run.font.color.rgb = 'Times New Roman', Pt(14), True, None
    
    # Isi Paragraf
    for p_text in isi_teks.split('\n'):
        t = p_text.strip()
        if t:
            p = doc.add_paragraph()
            fmt = p.paragraph_format
            fmt.line_spacing, fmt.alignment = 1.5, WD_ALIGN_PARAGRAPH.JUSTIFY
            p.add_run(t)
    return doc

# --- 5. TAMPILAN SIDEBAR ---
with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    nama_user = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    st.session_state['user_data']['nama'] = nama_user
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    
    def gen_lic(n):
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{datetime.now().strftime('%d%m')}-SKR"

    st.divider()
    
    # OWNER PANEL (Password: RAHASIA-BEBEN-2026)
    with st.expander("🛠️ OWNER PANEL"):
        pw = st.text_input("Admin Password:", type="password")
        if pw == "RAHASIA-BEBEN-2026": 
            st.success("Halo Bos Beben!")
            pbl = st.text_input("Nama Pembeli:")
            if st.button("
