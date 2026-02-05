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

if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

# --- 2. FUNGSI WORD (4333) ---
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
st.set_page_config(page_title="SkripsiGen Pro v8.59", layout="wide")
with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.session_state['user_data']['nama'] = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    def gen_lic(n):
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{datetime.now().strftime('%d%m')}-SKR"
    st.divider()
    st.markdown("### 🛠️ PANEL ADMIN")
    pw = st.text_input("Password Admin:", type="password")
    if pw == "RAHASIA-BEBEN-2026":
        pbl = st.text_input("Nama Pembeli Baru:")
        if st.button("Generate License"): st.code(gen_lic(pbl))
