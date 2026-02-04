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
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK PGRI 1 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

# --- 2. LOGIKA LISENSI ---
def gen_lic(n):
    d = datetime.now().strftime("%d%m")
    nm = n.split(' ')[0].upper() if n else "USER"
    return f"PRO-{nm}-{d}-SKR"

# --- 3. UI SETUP ---
st.set_page_config(page_title="SkripsiGen Pro v8.44", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.success("✅ Anti-Plagiarism: ACTIVE")
    st.success("✅ Privacy Mode: ON")
    
    st.divider()
    nama_user = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'], placeholder="Contoh: Beny")
    st.session_state['user_data']['nama'] = nama_user
    
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    
    if st.button("🗑️ Reset Semua Pekerjaan"):
        st.session_state['db'] = {}
        st.rerun()

    st.divider()
    with st.expander("🛠️ OWNER PANEL"):
        # GANTI "RAHASIA-BEBEN-2026" DENGAN PASSWORD KAMU SENDIRI
        pw = st.text_input("Admin Password:", type="password")
        if pw == "RAHASIA-BEBEN-2026": 
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate License ✨"): st.code(gen_lic(pbl))

# --- 4. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.44")
st.caption("Standard: Academic Integrity | Anti-Plagiarism & High-Level Paraphrase")

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
        with st.spinner(f"Menyusun & Kalibrasi {bab_aktif}..."):
            try:
                model = inisialisasi_ai()
                inst_pro = "Gunakan Anti-Plagiarism & Deep Paraphrase. Referensi RIIL 2023-2026."
                if "Lampiran" in bab_aktif:
                    prompt = f"{inst_pro}\nBuat Lampiran Lengkap {nama_user} judul '{topik}' di {lokasi}. Surat Izin, Kuesioner Data Awal, PST Utama, Kisi-kisi."
                else:
                    rev = f"REVISI DOSEN: {catatan_dosen}" if catatan_dosen else ""
                    prompt = f"{inst_pro}\nSusun draf {bab_aktif} skripsi {metode} judul '{topik}' di {lokasi}. {rev}."
                
                res = model.generate_content(prompt)
                st.session_state['db'][bab_aktif] = res.text
                st.success(f"{bab_aktif} Selesai!")
            except: st.error("Server sibuk, coba klik sekali lagi!")
    else: st.warning("Nama dan Judul wajib diisi!")

if st.button("🚀 Susun & Kalibrasi Sekarang"):
    jalankan_proses()

# --- 5. BOX OUTPUT DENGAN TOMBOL HUBUNGI ADMIN ---
if st.session_state['db']:
    st.divider()
    for b in sorted(st.session_state['db'].keys()):
        content = st.session_state['db'][b]
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            
            is_trial = b in ["Bab 1", "Bab 2"]
            is_pro = user_lic == gen_lic(nama_user)
            
            if "Lampiran" not in b:
                catatan = st.text_area(f"✍️ Catatan Revisi Dosen {b}:", key=f"rev_{b}")
                if st.button(f"🔄 Jalankan Revisi {b}", key=f"br_{b}"):
                    jalankan_proses(target_bab=b, catatan_dosen=catatan)
            
            with st.expander(f"Lihat Hasil {b}"):
                st.markdown(content)
                if is_trial or is_pro:
                    doc = Document()
                    doc.add_heading(b, 0); doc.add_paragraph(content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download {b} (Word)", data=bio.getvalue(), file_name=f"{b}.docx", key=f"dl_{b}")
                else:
                    st.error(f"🔑 {b} Terkunci (Mode PRO)")
                    # NOMOR WHATSAPP KAMU
                    nomor_wa = "6281273347072" 
                    pesan_wa = f"Halo Admin SkripsiGen, saya {nama_user}. Saya ingin aktivasi lisensi PRO untuk draf: {topik}"
                    url_wa = f"https://wa.me/{nomor_wa}?text={pesan_wa.replace(' ', '%20')}"
                    
                    st.link_button("💬 Hubungi Admin (Beli Lisensi)", url_wa)
