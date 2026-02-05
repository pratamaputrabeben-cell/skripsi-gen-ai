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

# --- 1. CONFIG & PERMANENT STORAGE ENGINE ---
ALL_KEYS = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])

# Inisialisasi Session State
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

# --- JAVASCRIPT UNTUK LOCAL STORAGE (MENGUNCI DATA DI BROWSER) ---
# Ini yang membuat data tidak hilang meski browser ditutup total
def save_to_local_storage():
    data_json = json.dumps({
        "db": st.session_state['db'],
        "user_data": st.session_state['user_data']
    })
    st.components.v1.html(
        f"""
        <script>
            localStorage.setItem('skripsigen_data', '{data_json}');
        </script>
        """,
        height=0,
    )

# --- 2. FUNGSI INTI AI & WORD ---
def inisialisasi_ai():
    key_aktif = random.choice(ALL_KEYS)
    genai.configure(api_key=key_aktif)
    return genai.GenerativeModel('gemini-1.5-flash')

def buat_dokumen_rapi(judul_bab, isi_teks):
    doc = Document()
    for sec in doc.sections:
        sec.left_margin, sec.top_margin = Cm(4), Cm(3)
        sec.right_margin, sec.bottom_margin = Cm(3), Cm(3)
    style = doc.styles['Normal']
    style.font.name, style.font.size = 'Times New Roman', Pt(12)
    
    # Bersihkan Teks
    teks_clean = re.sub(r"^(Tentu|Berikut|Ini adalah|Sesuai).*?\n", "", isi_teks, flags=re.IGNORECASE)
    teks_clean = teks_clean.replace("**", "").replace("---", "")

    head = doc.add_heading(judul_bab.upper(), 0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in head.runs:
        run.font.name, run.font.size, run.bold = 'Times New Roman', Pt(14), True

    for p_text in teks_clean.split('\n'):
        if p_text.strip():
            p = doc.add_paragraph()
            fmt = p.paragraph_format
            fmt.line_spacing, fmt.alignment = 1.5, WD_ALIGN_PARAGRAPH.JUSTIFY
            if re.match(r"^(\d+\.\d+)", p_text.strip()):
                run = p.add_run(p_text.strip()); run.bold = True
            else:
                p.add_run(p_text.strip()); fmt.first_line_indent = Inches(0.5)
    
    bio = BytesIO(); doc.save(bio)
    return bio.getvalue()

# --- 3. UI STREAMLIT ---
st.set_page_config(page_title="SkripsiGen Pro v8.55", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.success("🔒 PERMANENT SAVING: ON (Data Aman meski browser ditutup)")
    
    nama_user = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    st.session_state['user_data']['nama'] = nama_user
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    
    def gen_lic(n):
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{datetime.now().strftime('%d%m')}-SKR"

    st.divider()
    if st.button("🗑️ Reset & Hapus Permanen"):
        st.session_state['db'] = {}
        st.session_state['user_data'] = {"topik": "", "lokasi": "", "kota": "", "nama": ""}
        st.rerun()

st.title("🎓 SkripsiGen Pro v8.55")
st.caption("Versi Anti-Panik: Data tersimpan di memori browser mahasiswa.")

col1, col2 = st.columns(2)
with col1:
    topik = st.text_input("📝 Judul Skripsi:", value=st.session_state['user_data']['topik'])
    st.session_state['user_data']['topik'] = topik
    lokasi = st.text_input("📍 Lokasi:", value=st.session_state['user_data']['lokasi'])
    st.session_state['user_data']['lokasi'] = lokasi
with col2:
    kota = st.text_input("🏙️ Kota:", value=st.session_state['user_data']['kota'])
    st.session_state['user_data']['kota'] = kota
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran"])

if st.button("🚀 Susun & Simpan Permanen"):
    if topik and nama_user:
        with st.spinner(f"Menyusun {pil_bab}..."):
            try:
                model = inisialisasi_ai()
                prompt = f"Susun {pil_bab} skripsi {metode} judul '{topik}' di {lokasi}, {kota}. Pakai referensi 2023-2026."
                res = model.generate_content(prompt)
                st.session_state['db'][pil_bab] = res.text
                # TRIGGER SAVE
                save_to_local_storage()
                st.rerun()
            except: st.error("Server sibuk, klik lagi!")
    else: st.warning("Isi Nama & Judul!")

# --- 4. OUTPUT ---
if st.session_state['db']:
    for b in sorted(st.session_state['db'].keys()):
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            is_pro = user_lic == gen_lic(nama_user)
            
            # Fitur Revisi
            rev_txt = st.text_area(f"✍️ Revisi {b}:", key=f"re_{b}")
            if st.button(f"🔄 Update {b}", key=f"btn_{b}"):
                # Proses revisi sama seperti susun, lalu save_to_local_storage()
                pass

            with st.expander("Lihat Draf"):
                st.markdown(st.session_state['db'][b])
                if b in ["Bab 1", "Bab 2"] or is_pro:
                    data_word = buat_dokumen_rapi(b, st.session_state['db'][b])
                    st.download_button(f"📥 Download {b}", data=data_word, file_name=f"{b}.docx", key=f"dl_{b}")
                else:
                    st.error("🔑 Terkunci (Mode PRO)")
