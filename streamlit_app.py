import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import re

# --- 1. INITIAL CONFIG (WAJIB PERTAMA) ---
st.set_page_config(
    page_title="SkripsiGen Pro - Solusi Skripsi Otomatis",
    page_icon="🎓",
    layout="wide"
)

# --- 2. GOOGLE VERIFICATION TAG (SESUAI REQUEST BOS) ---
# Trik ini menyisipkan tag meta ke dalam body yang akan dibaca bot Google sebagai bagian dari head
st.markdown("""
    <head>
        <meta name="google-site-verification" content="L6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI" />
    </head>
    """, unsafe_allow_html=True)

# Pintu Rahasia tambahan (Jaga-jaga jika metode Tag HTML gagal)
if "google" in st.query_params:
    st.write("google-site-verification: googleL6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI.html")
    st.stop()

# --- 3. DATABASE & SESSION STATE ---
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

# --- 4. ENGINE SETUP ---
def inisialisasi_ai():
    try:
        keys = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])
        genai.configure(api_key=random.choice(keys))
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        st.error("Cek Secrets di Dashboard Streamlit!")
        st.stop()

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
    st.success("SEO Tag: Active")
    st.session_state['user_data']['nama'] = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    
    def gen_lic(n):
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{datetime.now().strftime('%d%m')}-SKR"

    if st.button("🗑️ Reset Semua"):
        st.session_state['db'] = {}
        st.rerun()

# --- 6. TAMPILAN UTAMA ---
st.title("🎓 SkripsiGen Pro v8.64")
st.caption("Standard: Academic Formatting 4-3-3-3 | Verified by Google")

c1, c2 = st.columns(2)
with c1:
    st.session_state['user_data']['topik'] = st.text_input("📝 Judul Skripsi:", value=st.session_state['user_data']['topik'])
with c2:
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
bab_pilih = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5"])

if st.button("🚀 Susun & Kalibrasi Sekarang"):
    if st.session_state['user_data']['topik'] and st.session_state['user_data']['nama']:
        with st.spinner("AI sedang menyusun draf..."):
            model = inisialisasi_ai()
            prompt = f"Susun {bab_pilih} skripsi {metode} judul '{st.session_state['user_data']['topik']}'. Pakai Ref 2023-2026."
            res = model.generate_content(prompt)
            st.session_state['db'][bab_pilih] = res.text
            st.rerun()
    else: st.warning("Isi Nama & Judul!")

# Box Output
if st.session_state['db']:
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            is_pro = user_lic == gen_lic(st.session_state['user_data']['nama'])
            with st.expander("Buka Draf"):
                st.markdown(content)
                if b in ["Bab 1", "Bab 2"] or is_pro:
                    doc = buat_dokumen_rapi(b, content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download {b}", data=bio.getvalue(), file_name=f"{b}.docx", key=f"dl_{b}")
                else:
                    st.error("🔑 Terkunci (Mode PRO)")
                    st.link_button("💬 Hubungi Admin", f"https://wa.me/6281273347072?text=Beli%20Lisensi%20{st.session_state['user_data']['nama']}")
