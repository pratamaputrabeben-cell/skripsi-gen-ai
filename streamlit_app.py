import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import time
import re

# ==========================================
# 1. GOOGLE SEARCH CONSOLE VERIFICATION
# ==========================================
# Ganti 'KODE_DARI_GOOGLE_DISINI' dengan kode asli dari Google Search Console
# Biasanya kodenya panjang seperti: <meta name="google-site-verification" content="ABC123XYZ..." />
google_tag = '<meta name="google-site-verification" content="L6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI" />'
st.components.v1.html(google_tag, height=0)

# ==========================================
# 2. KONFIGURASI ENGINE & DATABASE
# ==========================================
ALL_KEYS = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])
if 'db' not in st.session_state: st.session_state['db'] = {}
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
    except: return genai.GenerativeModel('gemini-1.5-flash')

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
        sec.left_margin, sec.top_margin = Cm(4
