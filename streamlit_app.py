import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime
import random
import time

# --- 1. KONEKSI MULTI-KEY ---
ALL_KEYS = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])

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

# --- 2. LOGIKA LISENSI ---
def gen_lic(n):
    d = datetime.now().strftime("%d%m")
    nm = n.split(' ')[0].upper() if n else "USER"
    return f"PRO-{nm}-{d}-SKR"

if 'db' not in st.session_state: st.session_state['db'] = {}

# --- 3. UI SETUP ---
st.set_page_config(page_title="SkripsiGen Pro v8.37", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.success("✅ Engine: Scholar Edition 2026")
    st.info("Fitur Lampiran Lengkap & Anti-Plagiasi Aktif.")
    
    st.divider()
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Contoh: Beny")
    user_lic = st.text_input("🔑 Kode Lisensi:", type="password")
    
    st.divider()
    with st.expander("🛠️ MENU OWNER"):
        pw = st.text_input("Admin Pass:", type="password")
        if pw == "BEBEN-BOSS":
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate ✨"): st.code(gen_lic(pbl))

# --- 4. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.37")
st.caption("Status: All Systems Operational | Multi-Key Ready")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Analisis Kinerja...")
    lokasi = st.text_input("📍 Lokasi:", value="SMK PGRI 1 Kabupaten Lahat")
with c2:
    kota = st.text_input("🏙️ Kota:", value="Lahat")
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", [
    "Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", 
    "Lampiran: Surat Izin, Kuesioner & Kisi-kisi"
])

# --- FUNGSI GENERATE UTAMA ---
def jalankan_proses(target_bab=None, catatan_dosen=""):
    # Mendefinisikan bab yang diproses di dalam fungsi agar tidak NameError
    bab_aktif = target_bab if target_bab else pil_bab
    
    if topik and nama_user:
        placeholder = st.empty()
        for i in range(3):
            try:
                with placeholder.container():
                    st.spinner(f"Sedang memproses {bab_aktif}...")
                    model = inisialisasi_ai()
                    
                    if "Lampiran" in bab_aktif:
                        prompt = f"""
                        Buatkan dokumen LAMPIRAN PENELITIAN SUPER LENGKAP untuk mahasiswa bernama {nama_user} dengan judul '{topik}' di {lokasi}, {kota}.
                        Wajib mencakup:
                        1. SURAT IZIN PENELITIAN & OBSERVASI AWAL ke Kepala Sekolah {lokasi}.
                        2. KUESIONER DATA AWAL (Pra-Riset).
                        3. KUESIONER PENELITIAN UTAMA (PST: Pengetahuan, Sikap, Tindakan) dengan Skala Likert/Guttman.
                        4. KISI-KISI INSTRUMEN (Tabel Variabel, Indikator, dan No Soal).
                        5. LEMBAR VALIDASI AHLI & INFORMED CONSENT (Persetujuan Responden).
                        Format profesional, siap cetak, dan rapi.
                        """
                    else:
                        revisi_str = f"REVISI BERDASARKAN CATATAN: {catatan_dosen}" if catatan_dosen else ""
                        prompt = f"""
                        Susun draf {bab_aktif} skripsi {metode} judul '{topik}' di {lokasi}, {kota}. {revisi_str}
                        Gunakan Referensi RIIL 2023-2026, format APA 7th, dan Deep Paraphrase.
                        Sertakan LAPORAN AUDIT KALIBRASI di akhir.
                        """
                    
                    res = model.generate_content(prompt)
                    st.session_state['db'][bab_aktif] = res.text
                    st.rerun()
                    break
            except Exception as e:
                if "429" in str(e):
                    st.warning("Jalur padat, mencoba lagi...")
                    time.sleep(5)
                else:
                    st.error(f"Error teknis: {e}"); break
    else: st.warning("Mohon isi Nama Mahasiswa dan Judul Skripsi!")

if st.button("🚀 Susun Draf / Lampiran"):
    jalankan_proses()

# --- 5. BOX OUTPUT ---
if st.session_state['db']:
    st.divider()
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            
            if "Lampiran" not in b:
                catatan = st.text_area(f"✍️ Catatan Revisi Dosen untuk {b}:", key=f"revisi_{b}")
                col1, col2 = st.columns([1, 4])
                if col1.button(f"🔄 Revisi {b}", key=f"btn_{b}"):
                    jalankan_proses(target_bab=b, catatan_dosen=catatan)
            
            st.markdown(content[:400] + "...")
            with st.expander("Buka Dokumen & Sertifikat Audit"):
                st.markdown(content)
                if user_lic == gen_lic(nama_user):
                    doc = Document()
                    doc.add_heading(b, 0)
                    doc.add_paragraph(content)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button(f"📥 Download Word", data=bio.getvalue(), file_name=f"{b}.docx", key=f"dl_{b}")
                else:
                    st.warning("Gunakan lisensi untuk mengaktifkan tombol download.")
