import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import re
import json

# --- 1. CONFIG & STORAGE ENGINE ---
ALL_KEYS = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])

if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

def inisialisasi_ai():
    key_aktif = random.choice(ALL_KEYS)
    genai.configure(api_key=key_aktif)
    return genai.GenerativeModel('gemini-1.5-flash')

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
        run.font.name, run.font.size, run.bold, run.font.color.rgb = 'Times New Roman', Pt(14), True, None

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
    
    bio = BytesIO(); doc.save(bio)
    return bio.getvalue()

# --- 3. UI SIDEBAR (PANEL ADMIN DI SINI) ---
st.set_page_config(page_title="SkripsiGen Pro v8.55", layout="wide", page_icon="🎓")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.success("🔒 AUTO-SAVE: AKTIF")
    
    # Input User
    st.session_state['user_data']['nama'] = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    
    def gen_lic(n):
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{datetime.now().strftime('%d%m')}-SKR"

    st.divider()
    
    # --- OWNER PANEL (GAMPANG DICARI) ---
    st.markdown("### 🛠️ PANEL ADMIN")
    pw = st.text_input("Masukan Password Admin:", type="password", key="admin_pw")
    if pw == "RAHASIA-BEBEN-2026":
        st.info("Halo Bos Beben! Siap Jualan?")
        pbl = st.text_input("Nama Pembeli Baru:")
        if st.button("Generate License ✨"):
            st.code(gen_lic(pbl))
            st.caption("Salin kode di atas & kirim ke pembeli.")
    
    st.divider()
    if st.button("🗑️ Reset & Hapus Semua"):
        st.session_state['db'] = {}
        st.session_state['user_data'] = {"topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""}
        st.rerun()

# --- 4. TAMPILAN UTAMA ---
st.title("🎓 SkripsiGen Pro v8.55")
st.caption("Anti-Close Tech | Standard Academic Formatting 4333")

c1, c2 = st.columns(2)
with c1:
    st.session_state['user_data']['topik'] = st.text_input("📝 Judul Skripsi:", value=st.session_state['user_data']['topik'])
    st.session_state['user_data']['lokasi'] = st.text_input("📍 Lokasi:", value=st.session_state['user_data']['lokasi'])
with c2:
    st.session_state['user_data']['kota'] = st.text_input("🏙️ Kota:", value=st.session_state['user_data']['kota'])
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran"])

if st.button("🚀 Susun & Simpan"):
    if st.session_state['user_data']['topik'] and st.session_state['user_data']['nama']:
        with st.spinner(f"Menyusun {pil_bab}..."):
            try:
                model = inisialisasi_ai()
                prompt = f"Susun {pil_bab} skripsi {metode} judul '{st.session_state['user_data']['topik']}' di {st.session_state['user_data']['lokasi']}, {st.session_state['user_data']['kota']}. Pakai bahasa Indonesia formal & referensi 2023-2026."
                res = model.generate_content(prompt)
                st.session_state['db'][pil_bab] = res.text
                st.rerun()
            except: st.error("Klik sekali lagi, Bos!")
    else: st.warning("Nama & Judul Wajib Isi!")

# --- 5. OUTPUT BOX ---
if st.session_state['db']:
    for b in sorted(st.session_state['db'].keys()):
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            is_pro = user_lic == gen_lic(st.session_state['user_data']['nama'])
            
            # Fitur Revisi
            rev_cat = st.text_area(f"✍️ Catatan Revisi {b}:", key=f"rev_{b}")
            if st.button(f"🔄 Jalankan Revisi {b}", key=f"btn_{b}"):
                with st.spinner("Merevisi..."):
                    model = inisialisasi_ai()
                    prompt_rev = f"Revisi draf ini: {st.session_state['db'][b]}. Catatan dosen: {rev_cat}. Tetap pertahankan format akademik."
                    res_rev = model.generate_content(prompt_rev)
                    st.session_state['db'][b] = res_rev.text
                    st.rerun()

            with st.expander("Buka Draf"):
                st.markdown(st.session_state['db'][b])
                if b in ["Bab 1", "Bab 2"] or is_pro:
                    data_word = buat_dokumen_rapi(b, st.session_state['db'][b])
                    st.download_button(f"📥 Download {b}", data=data_word, file_name=f"{b}.docx", key=f"dl_{b}")
                else
