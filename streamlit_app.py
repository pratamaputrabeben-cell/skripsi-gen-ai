import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import re

# --- 1. KONFIGURASI ENGINE ---
ALL_KEYS = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

def inisialisasi_ai():
    key_aktif = random.choice(ALL_KEYS)
    genai.configure(api_key=key_aktif)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except:
        return genai.GenerativeModel('gemini-1.5-flash')

# --- Fungsi Baca File Word (Fitur Baru) ---
def baca_file_word(file_upload):
    doc = Document(file_upload)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

# --- 2. FUNGSI MEMBERSIHKAN TEKS ---
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

# --- 3. FUNGSI RAPIKAN WORD (4333) ---
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
            if re.match(r"^(\d+\.\d+)", t):
                run = p.add_run(t); run.bold = True
            else:
                p.add_run(t); fmt.first_line_indent = Inches(0.5)
    bio = BytesIO(); doc.save(bio)
    return bio.getvalue()

# --- 4. UI STREAMLIT ---
st.set_page_config(page_title="SkripsiGen Pro v8.60", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    nama_user = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    st.session_state['user_data']['nama'] = nama_user
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    def gen_lic(n):
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{datetime.now().strftime('%d%m')}-SKR"
    st.divider()
    with st.expander("🛠️ OWNER PANEL"):
        pw = st.text_input("Admin Password:", type="password")
        if pw == "RAHASIA-BEBEN-2026":
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate License ✨"): st.code(gen_lic(pbl))
    if st.button("🗑️ Reset Semua"):
        st.session_state['db'] = {}; st.rerun()

st.title("🎓 SkripsiGen Pro v8.60")
st.caption("Standard: 4333 | Fitur: Bedah File Word & Perbaikan Ocehan Dosen")

# --- AREA UPLOAD ---
with st.expander("📤 UPLOAD FILE WORD (Opsional)", expanded=False):
    up_file = st.file_uploader("Upload file .docx mahasiswa di sini", type=["docx"])
    if up_file:
        st.session_state['db']['File_Upload'] = baca_file_word(up_file)
        st.success("✅ File berhasil dibaca!")

st.divider()
col1, col2 = st.columns(2)
with col1:
    topik = st.text_input("📝 Judul Skripsi:", value=st.session_state['user_data']['topik'])
    st.session_state['user_data']['topik'] = topik
    lokasi = st.text_input("📍 Lokasi:", value=st.session_state['user_data']['lokasi'])
    st.session_state['user_data']['lokasi'] = lokasi
with col2:
    st.session_state['user_data']['kota'] = st.text_input("🏙️ Kota:", value=st.session_state['user_data']['kota'])
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bab:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5"])

if st.button("🚀 Proses & Kalibrasi Sekarang"):
    if topik and nama_user:
        with st.spinner("Sedang memproses..."):
            try:
                model = inisialisasi_ai()
                konten_lama = st.session_state['db'].get('File_Upload', "Tidak ada.")
                prmt = f"Tugas: Susun {pil_bab}. Judul: {topik}. Lokasi: {lokasi}. Metode: {metode}. Referensi: 2023-2026. File asal: {konten_lama}"
                res = model.generate_content(prmt)
                st.session_state['db'][pil_bab] = res.text
                st.rerun()
            except: st.error("Server sibuk, klik sekali lagi!")
    else: st.warning("Nama & Judul wajib diisi!")

# --- BOX OUTPUT ---
if st.session_state['db']:
    for b in sorted(st.session_state['db'].keys()):
        if b == "File_Upload": continue
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            ocehan = st.text_area(f"📢 Ocehan Dosen untuk {b}:", placeholder="Contoh: Tambahkan teori dari Sugiyono...", key=f"rev_{b}")
            if st.button(f"🔄 Jalankan Revisi {b}", key=f"btn_{b}"):
                with st.spinner("Memperbaiki draf..."):
                    model = inisialisasi_ai()
                    prmt_rev = f"Draf: {st.session_state['db'][b]}. Revisi Dosen: {ocehan}. Perbaiki draf tersebut sesuai instruksi."
                    res_rev = model.generate_content(prmt_rev)
                    st.session_state['db'][b] = res_rev.text
                    st.rerun()
            with st.expander("Buka Draf"):
                st.markdown(st.session_state['db'][b])
                is_pro = user_lic == gen_lic(nama_user)
                if b in ["Bab 1", "Bab 2"] or is_pro:
                    data_word = buat_dokumen_rapi(b, st.session_state['db'][b])
                    st.download_button(f"📥 Download {b}", data=data_word, file_name=f"{b}.docx", key=f"dl_{b}")
                else:
                    st.error("🔑 Mode PRO Terkunci")
                    st.link_button("💬 Hubungi Admin", f"https://wa.me/6281273347072?text=Beli%20Lisensi%20{nama_user}")
