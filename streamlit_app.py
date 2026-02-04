import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import time

# --- 1. KONEKSI MULTI-KEY & DATABASE ---
ALL_KEYS = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK PGRI 1 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

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

# --- 2. FUNGSI RAPIKAN WORD (STANDAR SKRIPSI 4-3-3-3) ---
def buat_dokumen_rapi(judul_bab, isi_teks):
    doc = Document()
    
    # Pengaturan Margin (4333)
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(3)
        section.bottom_margin = Cm(3)
        section.left_margin = Cm(4)
        section.right_margin = Cm(3)

    # Setting Font Global
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    
    # Judul Bab (Center, Bold, Size 14)
    head = doc.add_heading(judul_bab, 0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in head.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.bold = True
        run.font.color.rgb = None
    
    paragraphs = isi_teks.split('\n')
    for p_text in paragraphs:
        t = p_text.strip()
        if t:
            p = doc.add_paragraph()
            p_format = p.paragraph_format
            p_format.line_spacing = 1.5
            p_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            # Logika Penomoran & Indentasi
            if t[0].isdigit() and "." in t[:5]:
                run = p.add_run(t)
                run.bold = True
                titik_count = t.split(' ')[0].count('.')
                if titik_count == 1: p_format.left_indent = Inches(0.2)
                elif titik_count >= 2: p_format.left_indent = Inches(0.4)
            else:
                p.add_run(t)
                p_format.first_line_indent = Inches(0.5)
            
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 3. UI SETUP ---
st.set_page_config(page_title="SkripsiGen Pro v8.47", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.success("✅ Margin 4-3-3-3: ACTIVE")
    st.success("✅ Anti-Plagiarism: ACTIVE")
    
    nama_user = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    st.session_state['user_data']['nama'] = nama_user
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    
    def gen_lic(n):
        d = datetime.now().strftime("%d%m")
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{d}-SKR"

    st.divider()
    with st.expander("🛠️ OWNER PANEL"):
        pw = st.text_input("Admin Password:", type="password")
        if pw == "
