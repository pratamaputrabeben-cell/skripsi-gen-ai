import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import re

# --- 1. SET PAGE CONFIG (WAJIB PERTAMA) ---
# Kita gunakan trik menyisipkan tag GSC di dalam parameter icon/title agar terbaca bot
st.set_page_config(
    page_title="SkripsiGen Pro - Solusi Skripsi Anti-Plagiarisme",
    page_icon="🎓",
    layout="wide"
)

# --- 2. SEO INJECTION (TRIK TERBARU) ---
# Menggunakan st.write dengan unsafe_allow_html di awal main body
st.markdown('<meta name="google-site-verification" content="L6kryKGl6065OhPiWKuJIu0TqxEGRW1BwGV5b9KxJhI" />', unsafe_allow_html=True)

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
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        st.error("Konfigurasi API Key belum lengkap di Secrets.")
        st.stop()

# --- 5. WORD GENERATOR (STANDAR 4333) ---
def buat_dokumen_rapi(judul_bab, isi_teks):
    doc = Document()
    for sec in doc.sections:
        sec.left_margin, sec.right_margin = Cm(4), Cm(3)
        sec.top_margin, sec.bottom_margin = Cm(3), Cm(3)
    
    style = doc.styles['Normal']
    style.font.name, style.font.size = 'Times New Roman', Pt(12)
    
    # Cleaning basa-basi AI
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
    
    if st.button("🗑️ Reset Sesi"):
        st.session_state['db'] = {}
        st.rerun()

st.title("🎓 SkripsiGen Pro v8.60")
st.caption("Auto-Format Ready | Google Search Console Verified")

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

if st.button("🚀 Susun Sekarang"):
    if topik and nama_user:
        with st.spinner("AI sedang bekerja..."):
            model = inisialisasi_ai()
            prompt = f"Susun {pil_bab} skripsi {metode} judul '{topik}' di {lokasi}, {kota}. Gunakan Anti-Plagiarism & Ref RIIL 2023-2026."
            res = model.generate_content(prompt)
            st.session_state['db'][pil_bab] = res.text
            st.rerun()
    else: st.warning("Lengkapi Nama & Judul!")

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
                    st.error("🔑 Bagian Terkunci (Mode PRO)")
                    st.link_button("💬 Hubungi Admin", f"https://wa.me/6281273347072?text=Beli%20Lisensi%20{nama_user}")
