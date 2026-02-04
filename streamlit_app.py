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

if 'db' not in st.session_state: st.session_state['db'] = {}

# --- 2. LOGIKA LISENSI & TRIAL ---
def gen_lic(n):
    d = datetime.now().strftime("%d%m")
    nm = n.split(' ')[0].upper() if n else "USER"
    return f"PRO-{nm}-{d}-SKR"

# --- 3. UI SETUP ---
st.set_page_config(page_title="SkripsiGen Pro v8.40", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.success("🎁 Mode: Trial Bab 1 & 2 Aktif")
    st.info("Download gratis untuk Bab 1 & 2. Bab selanjutnya memerlukan lisensi PRO.")
    
    st.divider()
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Contoh: Beny")
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    
    st.divider()
    with st.expander("🛠️ MENU OWNER"):
        pw = st.text_input("Admin Pass:", type="password")
        if pw == "BEBEN-BOSS":
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate ✨"): st.code(gen_lic(pbl))

# --- 4. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.40")
st.caption("Status: Trial Mode | Free Download: Bab 1-2")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Analisis Hubungan...")
    lokasi = st.text_input("📍 Lokasi:", value="SMK PGRI 1 Kabupaten Lahat")
with c2:
    kota = st.text_input("🏙️ Kota:", value="Lahat")
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", [
    "Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", 
    "Lampiran: Surat Izin, Kuesioner & Kisi-kisi"
])

def jalankan_proses(target_bab=None, catatan_dosen=""):
    bab_aktif = target_bab if target_bab else pil_bab
    if topik and nama_user:
        with st.spinner(f"Menyusun {bab_aktif}..."):
            try:
                model = inisialisasi_ai()
                if "Lampiran" in bab_aktif:
                    prompt = f"Buat Lampiran Lengkap {nama_user} judul '{topik}' di {lokasi}. Surat Izin, Kuesioner Pra-Riset, Kuesioner PST, dan Kisi-kisi."
                else:
                    rev = f"REVISI: {catatan_dosen}" if catatan_dosen else ""
                    prompt = f"Susun draf {bab_aktif} skripsi {metode} judul '{topik}' di {lokasi}. {rev}. Ref RIIL 2023-2026, APA 7th, Deep Paraphrase."
                
                res = model.generate_content(prompt)
                st.session_state['db'][bab_aktif] = res.text
                st.success(f"{bab_aktif} Selesai!")
            except: st.error("Jalur sibuk, coba lagi.")
    else: st.warning("Isi Nama & Judul!")

if st.button("🚀 Susun Bagian Terpilih"):
    jalankan_proses()

# --- 5. BOX OUTPUT (LOGIKA LOCK TRIAL) ---
if st.session_state['db']:
    st.divider()
    for b in sorted(st.session_state['db'].keys()):
        content = st.session_state['db'][b]
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            
            # Cek Akses Download
            is_trial = b in ["Bab 1", "Bab 2"]
            is_pro = user_lic == gen_lic(nama_user)
            akses_buka = is_trial or is_pro
            
            if "Lampiran" not in b:
                catatan = st.text_area(f"✍️ Revisi Dosen {b}:", key=f"rev_{b}")
                if st.button(f"🔄 Jalankan Revisi {b}", key=f"br_{b}"):
                    jalankan_proses(target_bab=b, catatan_dosen=catatan)
            
            st.markdown(content[:500] + "...")
            with st.expander("Buka Dokumen & Download"):
                st.markdown(content)
                if akses_buka:
                    doc = Document()
                    doc.add_heading(b, 0); doc.add_paragraph(content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download {b} (Word)", data=bio.getvalue(), file_name=f"{b}.docx", key=f"dl_{b}")
                else:
                    st.error("🔑 Bagian ini Terkunci. Masukkan Lisensi PRO untuk mengunduh Bab 3, 4, 5, dan Lampiran.")
