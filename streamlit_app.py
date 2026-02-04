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
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(3)
        section.bottom_margin = Cm(3)
        section.left_margin = Cm(4)
        section.right_margin = Cm(3)

    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    
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
st.set_page_config(page_title="SkripsiGen Pro v8.48", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.success("✅ Clean Code System")
    
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
            if st.button("Generate License ✨"): 
                st.code(gen_lic(pbl))
    
    if st.button("🗑️ Reset Pekerjaan"):
        st.session_state['db'] = {}
        st.rerun()

# --- 4. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.48")
st.caption("Auto-Formatter: Times New Roman, 1.5 Spacing, Margin 4333")

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
pil_bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran: Surat Izin, Kuesioner & Kisi-kisi"])

def jalankan_proses(target_bab=None, catatan_dosen=""):
    bab_aktif = target_bab if target_bab else pil_bab
    if topik and nama_user:
        with st.spinner(f"Menyusun & Memformat {bab_aktif}..."):
            try:
                model = inisialisasi_ai()
                prompt = f"Susun draf {bab_aktif} skripsi {metode} judul '{topik}' di {lokasi}, {kota}. Catatan: {catatan_dosen}. Gunakan Anti-Plagiarism, Paraphrase, Ref RIIL 2023-2026, APA 7th."
                res = model.generate_content(prompt)
                st.session_state['db'][bab_aktif] = res.text
                st.success(f"{bab_aktif} Berhasil Disusun!")
            except: st.error("Klik roket sekali lagi!")
    else: st.warning("Nama dan Judul wajib diisi!")

if st.button("🚀 Susun & Kalibrasi Sekarang"):
    jalankan_proses()

# --- 5. BOX OUTPUT ---
if st.session_state['db']:
    st.divider()
    for b in sorted(st.session_state['db'].keys()):
        content = st.session_state['db'][b]
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            is_trial = b in ["Bab 1", "Bab 2"]
            is_pro = user_lic == gen_lic(nama_user)
            if "Lampiran" not in b:
                catatan = st.text_area(f"✍️ Revisi Dosen {b}:", key=f"rev_{b}")
                if st.button(f"🔄 Jalankan Revisi {b}", key=f"br_{b}"):
                    jalankan_proses(target_bab=b, catatan_dosen=catatan)
            with st.expander(f"Lihat Hasil {b}"):
                st.markdown(content)
                if is_trial or is_pro:
                    data_word = buat_dokumen_rapi(b, content)
                    st.download_button(f"📥 Download {b}", data=data_word, file_name=f"{b}.docx", key=f"dl_{b}")
                else:
                    st.error(f"🔑 {b} Terkunci (Mode PRO)")
                    nomor_wa = "6281273347072" 
                    url_wa = f"https://wa.me/{nomor_wa}?text=Halo%20Admin%2C%20saya%20{nama_user}.%20Mau%20beli%20lisensi%20PRO."
                    st.link_button("💬 Hubungi Admin (Beli Lisensi)", url_wa)
