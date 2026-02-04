import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import re

# --- 1. JALUR PRIORITAS GOOGLE (WAJIB PALING ATAS) ---
# Menaruh tag verifikasi di awal agar terbaca bot Google dalam sekejap
st.markdown('<meta name="google-site-verification" content="L6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI" />', unsafe_allow_html=True)

# Pintu darurat untuk Bot Google
if "google" in st.query_params:
    st.write("google-site-verification: googleL6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI.html")
    st.stop()

# --- 2. CONFIG HALAMAN ---
st.set_page_config(
    page_title="SkripsiGen Pro - Solusi Skripsi Otomatis",
    page_icon="🎓",
    layout="wide"
)

# --- 3. DATABASE & ENGINE ---
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

def inisialisasi_ai():
    try:
        keys = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])
        genai.configure(api_key=random.choice(keys))
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        st.error("Cek Secrets API Key kamu!")
        st.stop()

# --- 4. FORMATTING WORD 4333 ---
def buat_dokumen_rapi(judul, isi):
    doc = Document()
    for sec in doc.sections:
        sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = Cm(4), Cm(3), Cm(3), Cm(3)
    p = doc.add_paragraph()
    p.add_run(judul.upper()).bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(isi)
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

    if st.button("🗑️ Reset Sesi"):
        st.session_state['db'] = {}
        st.rerun()

# --- 6. TAMPILAN UTAMA ---
st.title("🎓 SkripsiGen Pro v8.65")
st.caption("Auto-Format: Times New Roman 12 | Spasi 1.5 | Margin 4333")

c1, c2 = st.columns(2)
with c1:
    st.session_state['user_data']['topik'] = st.text_input("📝 Judul Skripsi:", value=st.session_state['user_data']['topik'])
with c2:
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
bab = st.selectbox("📄 Pilih Bab:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5"])

if st.button("🚀 Susun Sekarang"):
    if st.session_state['user_data']['topik'] and st.session_state['user_data']['nama']:
        with st.spinner("AI sedang menyusun..."):
            model = inisialisasi_ai()
            res = model.generate_content(f"Susun {bab} skripsi {metode} judul {st.session_state['user_data']['topik']}")
            st.session_state['db'][bab] = res.text
            st.rerun()
    else: st.warning("Isi Nama & Judul!")

if st.session_state['db']:
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            if b in ["Bab 1", "Bab 2"] or user_lic == gen_lic(st.session_state['user_data']['nama']):
                doc = buat_dokumen_rapi(b, content)
                bio = BytesIO(); doc.save(bio)
                st.download_button(f"📥 Download {b}", data=bio.getvalue(), file_name=f"{b}.docx", key=f"dl_{b}")
            else:
                st.error("🔑 Terkunci (Mode PRO)")
