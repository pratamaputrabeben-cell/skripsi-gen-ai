import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import re

# --- 1. WAJIB PALING ATAS (TANPA PENGECUALIAN) ---
st.set_page_config(page_title="SkripsiGen Pro v8.59", layout="wide")

# --- 2. LOGIKA SEO (TEKNIK AMAN) ---
def inject_google_seo():
    # Menggunakan st.components agar tidak bentrok dengan st.set_page_config
    google_tag = '<meta name="google-site-verification" content="L6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI" />'
    st.components.v1.html(f"<html><head>{google_tag}</head><body></body></html>", height=0)

# Panggil SEO Injection
inject_google_seo()

# --- 3. SESSION STATE ---
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

# --- 4. ENGINE SETUP ---
def inisialisasi_ai():
    try:
        keys = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])
        key_aktif = random.choice(keys)
        genai.configure(api_key=key_aktif)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for target in ['gemini-1.5-flash', 'gemini-1.5-pro']:
            for real_model in available_models:
                if target in real_model: return genai.GenerativeModel(real_model)
        return genai.GenerativeModel(available_models[0])
    except Exception as e:
        st.error(f"⚠️ Masalah API Key: {e}")
        st.stop()

# --- 5. WORD GENERATOR ---
def buat_dokumen_rapi(judul_bab, isi_teks):
    doc = Document()
    for sec in doc.sections:
        sec.left_margin, sec.right_margin = Cm(4), Cm(3)
        sec.top_margin, sec.bottom_margin = Cm(3), Cm(3)
    
    style = doc.styles['Normal']
    style.font.name, style.font.size = 'Times New Roman', Pt(12)
    
    # Cleaning
    teks_clean = re.sub(r"^(Tentu|Berikut|Ini adalah|Sesuai).*?\n", "", isi_teks, flags=re.IGNORECASE)
    teks_clean = teks_clean.replace("&nbsp;", " ").replace("**", "").replace("---", "")
    
    head = doc.add_heading(judul_bab.upper(), 0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in head.runs:
        run.font.name, run.font.size, run.bold, run.font.color.rgb = 'Times New Roman', Pt(14), True, None
    
    for p_text in teks_clean.split('\n'):
        t = p_text.strip()
        if t:
            p = doc.add_paragraph()
            fmt = p.paragraph_format
            fmt.line_spacing, fmt.alignment = 1.5, WD_ALIGN_PARAGRAPH.JUSTIFY
            if t[0].isdigit() and "." in t[:5]:
                run = p.add_run(t); run.bold = True
                fmt.left_indent = Inches(0.2 * t.split(' ')[0].count('.'))
            else:
                p.add_run(t); fmt.first_line_indent = Inches(0.5)
    return doc

# --- 6. UI ---
with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
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
        if pw == "RAHASIA-BEBEN-2026": 
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate License ✨"): st.code(gen_lic(pbl))
    
    if st.button("🗑️ Reset Semua"):
        st.session_state['db'] = {}
        st.rerun()

st.title("🎓 SkripsiGen Pro v8.59")
st.caption("Auto-Format Ready (4333, Times New Roman, Spasi 1.5)")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", value=st.session_state['user_data']['topik'])
    st.session_state['user_data']['topik'] = topik
    lokasi = st.text_input("📍 Lokasi:", value=st.session_state['user_data']['lokasi'])
    st.session_state['user_data']['lokasi'] = lokasi
with c2:
    kota = st.text_input("🏙️ Kota:", value=st.session_state['user_data']['kota'])
    st.session_state['user_data']['kota'] = kota
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran"])

if st.button("🚀 Susun & Kalibrasi Sekarang"):
    if topik and nama_user:
        with st.spinner("Menghubungi AI..."):
            model = inisialisasi_ai()
            prompt = f"Susun {pil_bab} skripsi {metode} judul '{topik}' di {lokasi}, {kota}. Pakai Ref 2023-2026."
            res = model.generate_content(prompt)
            st.session_state['db'][pil_bab] = res.text
            st.rerun()
    else: st.warning("Isi Nama & Judul!")

if st.session_state['db']:
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            is_trial, is_pro = b in ["Bab 1", "Bab 2"], user_lic == gen_lic(nama_user)
            with st.expander(f"Buka Draf"):
                st.markdown(content)
                if is_trial or is_pro:
                    doc = buat_dokumen_rapi(b, content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download {b}", data=bio.getvalue(), file_name=f"{b}.docx", key=f"dl_{b}")
                else:
                    st.error("🔑 Terkunci (Mode PRO)")
                    st.link_button("💬 Hubungi Admin", f"https://wa.me/6281273347072?text=Beli%20Lisensi%20{nama_user}")
