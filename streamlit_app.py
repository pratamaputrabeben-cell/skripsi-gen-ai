import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime
import random
import re
import time

# --- 1. KONFIGURASI ENGINE ---
def inisialisasi_ai():
    # Ambil kunci dari secrets
    keys = st.secrets.get("GEMINI_API_KEYS", [])
    if not keys: 
        keys = [st.secrets.get("GEMINI_API_KEY", "")]
    
    # Pilih kunci secara acak
    key_aktif = random.choice(keys)
    genai.configure(api_key=key_aktif)
    
    # Gunakan model FLASH (Lebih cepat & jarang sibuk)
    return genai.GenerativeModel('gemini-1.5-flash')

if 'db' not in st.session_state: st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK Negeri 2 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

# --- FUNGSI EKSEKUSI DENGAN RETRY LEBIH KUAT ---
def eksekusi_ai_kebal(prompt):
    # Coba sampai 5 kali (Lebih tangguh)
    for i in range(5):
        try:
            model = inisialisasi_ai()
            res = model.generate_content(prompt)
            if res and res.text:
                return res.text
        except Exception as e:
            # Jika gagal, tunggu lebih lama (detik bertambah)
            time.sleep(i + 2) 
            continue
    return None

# --- 2. FUNGSI WORD ---
def baca_file_word(file_upload):
    try:
        doc = Document(file_upload)
        return "\n".join([para.text for para in doc.paragraphs])
    except: return ""

def buat_dokumen_rapi(judul_bab, isi_teks):
    doc = Document()
    for sec in doc.sections:
        sec.left_margin, sec.top_margin, sec.right_margin, sec.bottom_margin = Cm(4), Cm(3), Cm(3), Cm(3)
    style = doc.styles['Normal']
    style.font.name, style.font.size = 'Times New Roman', Pt(12)
    t_clean = re.sub(r"^(Tentu|Berikut|Ini adalah|Sesuai).*?\n", "", isi_teks, flags=re.IGNORECASE).replace("**", "").replace("---", "")
    head = doc.add_heading(judul_bab.upper(), 0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in head.runs: run.font.name, run.font.size, run.bold = 'Times New Roman', Pt(14), True
    for p_text in t_clean.split('\n'):
        if p_text.strip():
            p = doc.add_paragraph()
            fmt = p.paragraph_format
            fmt.line_spacing, fmt.alignment = 1.5, WD_ALIGN_PARAGRAPH.JUSTIFY
            if re.match(r"^(\d+\.\d+)", p_text.strip()):
                run = p.add_run(p_text.strip()); run.bold = True
            else:
                p.add_run(p_text.strip()); fmt.first_line_indent = Inches(0.5)
    bio = BytesIO(); doc.save(bio); return bio.getvalue()

# --- 3. UI SIDEBAR ---
st.set_page_config(page_title="SkripsiGen v8.63", layout="wide")
with st.sidebar:
    st.header("🛡️ Kontrol Panel")
    st.session_state['user_data']['nama'] = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'])
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    def gen_lic(n):
        nm = n.split(' ')[0].upper() if n else "USER"
        return f"PRO-{nm}-{datetime.now().strftime('%d%m')}-SKR"
    st.divider()
    with st.expander("🛠️ ADMIN"):
        pw = st.text_input("Password:", type="password")
        if pw == "RAHASIA-BEBEN-2026":
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Gen License"): st.code(gen_lic(pbl))
    if st.button("🗑️ Reset Data"):
        st.session_state['db'] = {}; st.rerun()

# --- 4. TAMPILAN UTAMA ---
st.title("🎓 SkripsiGen Pro v8.63")
st.caption("Status: Ultra Stable | Anti-Server Busy Optimization")

with st.expander("📤 UPLOAD DRAF LAMA (Opsional)"):
    up_file = st.file_uploader("Upload .docx", type=["docx"])
    if up_file:
        st.session_state['db']['File_Upload'] = baca_file_word(up_file)
        st.success("✅ File terbaca!")

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.session_state['user_data']['topik'] = st.text_input("📝 Judul:", value=st.session_state['user_data']['topik'])
    st.session_state['user_data']['lokasi'] = st.text_input("📍 Lokasi:", value=st.session_state['user_data']['lokasi'])
with c2:
    st.session_state['user_data']['kota'] = st.text_input("🏙️ Kota:", value=st.session_state['user_data']['kota'])
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bab:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5"])

if st.button("🚀 SUSUN SEKARANG"):
    if st.session_state['user_data']['topik'] and st.session_state['user_data']['nama']:
        with st.spinner("Menghubungi server Google..."):
            k_lama = st.session_state['db'].get('File_Upload', "Tidak ada.")
            jdl = st.session_state['user_data']['topik']
            lks = st.session_state['user_data']['lokasi']
            prmt = f"Susun {pil_bab}. Judul: {jdl}. Lokasi: {lks}. Draf: {k_lama}. Bahasa Indonesia Formal."
            
            hasil = eksekusi_ai_kebal(prmt)
            if hasil:
                st.session_state['db'][pil_bab] = hasil
                st.rerun()
            else:
                st.error("Google sedang overload parah. Coba ganti Judul sedikit atau tunggu 1 menit.")
    else: st.warning("Nama & Judul wajib diisi!")

# --- 5. OUTPUT ---
if st.session_state['db']:
    for b in sorted(st.session_state['db'].keys()):
        if b == "File_Upload": continue
        with st.container(border=True):
            st.subheader(f"📄 {b}")
            ocehan = st.text_area(f"📢 Revisi Dosen {b}:", key=f"rev_{b}")
            if st.button(f"🔄 Perbaiki {b}", key=f"btn_{b}"):
                with st.spinner("Memproses revisi..."):
                    p_rev = f"Draf: {st.session_state['db'][b]}. Revisi: {ocehan}. Perbaiki draf ini."
                    hasil_rev = eksekusi_ai_kebal(p_rev)
                    if hasil_rev:
                        st.session_state['db'][b] = hasil_rev
                        st.rerun()
            with st.expander("Lihat Hasil"):
                st.markdown(st.session_state['db'][b])
                is_pro = user_lic == gen_lic(st.session_state['user_data']['nama'])
                if b in ["Bab 1", "Bab 2"] or is_pro:
                    dt_word = buat_dokumen_rapi(b, st.session_state['db'][b])
                    st.download_button(f"📥 Download {b}", data=dt_word, file_name=f"{b}.docx", key=f"dl_{b}")
                else:
                    st.error("🔑 Mode PRO Aktif")
