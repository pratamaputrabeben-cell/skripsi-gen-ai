import streamlit as st
import streamlit.components.v1 as components  # Penting untuk verifikasi Google
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import time
import re

# =========================================================
# 1. VERIFIKASI GOOGLE SEARCH CONSOLE (AGAR BISA DICARI)
# =========================================================
# Memasukkan kode unik agar Google bisa mendeteksi website ini
components.html(
    """
    <meta name="google-site-verification" content="L6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI" />
    """,
    height=0,
)

# =========================================================
# 2. KONFIGURASI ENGINE & DATA SESSION
# =========================================================
ALL_KEYS = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])

if 'db' not in st.session_state: 
    st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

def inisialisasi_ai():
    key_aktif = random.choice(ALL_KEYS)
    genai.configure(api_key=key_aktif)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for target in ['gemini-1.5-flash', 'gemini-1.5-pro']:
            for real_model in available_models:
                if target in real_model: return genai.GenerativeModel(real_model)
        return genai.GenerativeModel(available_models[0])
    except: 
        return genai.GenerativeModel('gemini-1.5-flash')

# --- FUNGSI MEMBERSIHKAN & MENGURUTKAN TEKS ---
def bersihkan_dan_urutkan(teks):
    teks = re.sub(r"^(Tentu|Berikut|Ini adalah|Sesuai).*?\n", "", teks, flags=re.IGNORECASE)
    teks = teks.replace("&nbsp;", " ").replace("**", "").replace("---", "")
    
    if "DAFTAR PUSTAKA" in teks.upper():
        parts = re.split(r"DAFTAR PUSTAKA", teks, flags=re.IGNORECASE)
        konten_utama = parts[0]
        pustaka_raw = parts[1].strip().split('\n')
        pustaka_clean = sorted([p.strip() for p in pustaka_raw if len(p.strip()) > 10])
        return konten_utama.strip(), pustaka_clean
    return teks.strip(), []

# --- FUNGSI RAPIKAN WORD (STANDAR AKADEMIK) ---
def buat_dokumen_rapi(judul_bab, isi_teks):
    doc = Document()
    for sec in doc.sections:
        sec.left_margin, sec.top_margin = Cm(4), Cm(3)
        sec.right_margin, sec.bottom_margin = Cm(3), Cm(3)

    style = doc.styles['Normal']
    style.font.name, style.font.size = 'Times New Roman', Pt(12)
    
    konten, daftar_pustaka = bersihkan_dan_urutkan(isi_teks)

    head = doc.add_heading(judul_bab.upper(), 0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in head.runs:
        run.font.name, run.font.size, run.bold, run.font.color.rgb = 'Times New Roman', Pt(14), True, None
    
    for p_text in konten.split('\n'):
        t = p_text.strip()
        if t:
            p = doc.add_paragraph()
            fmt = p.paragraph_format
            fmt.line_spacing, fmt.alignment = 1.5, WD_ALIGN_PARAGRAPH.JUSTIFY
            
            match_num = re.match(r"^(\d+\.\d+(\.\d+)?)\s*(.*)", t)
            if match_num:
                run = p.add_run(t)
                run.bold = True
                level = match_num.group(1).count('.')
                fmt.left_indent = Inches(0.2 * level)
            else:
                p.add_run(t)
                fmt.first_line_indent = Inches(0.5)

    if daftar_pustaka:
        doc.add_page_break()
        dp_head = doc.add_heading("DAFTAR PUSTAKA", 0)
        dp_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in dp_head.runs:
            run.font.name, run.font.size, run.bold, run.font.color.rgb = 'Times New Roman', Pt(14), True, None
            
        for ref in daftar_pustaka:
            p = doc.add_paragraph(ref)
            fmt = p.paragraph_format
            fmt.line_spacing = 1.5
            fmt.left_indent = Inches(0.5)
            fmt.first_line_indent = Inches(-0.5)

    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# =========================================================
# 3. ANTARMUKA (UI) STREAMLIT
# =========================================================
st.set_page_config(page_title="SkripsiGen Pro v8.51", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.success("✅ Auto-Sort Bibliography: ON")
    st.success("✅ Margin 4333: ACTIVE")
    
    nama_user = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    st.session_state['user_data
