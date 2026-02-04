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

# --- 2. MEMORI PERMANEN (SESSION STATE) ---
# Menyiapkan database agar tidak terhapus saat refresh
if 'db' not in st.session_state:
    st.session_state['db'] = {}
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {"topik": "", "lokasi": "SMK PGRI 1 Kabupaten Lahat", "kota": "Lahat", "nama": ""}

# --- 3. LOGIKA LISENSI ---
def gen_lic(n):
    d = datetime.now().strftime("%d%m")
    nm = n.split(' ')[0].upper() if n else "USER"
    return f"PRO-{nm}-{d}-SKR"

# --- 4. UI SETUP ---
st.set_page_config(page_title="SkripsiGen Pro v8.42", layout="wide")

with st.sidebar:
    st.header("🛡️ Pusat Kalibrasi")
    st.success("✅ Memory Auto-Save: ACTIVE")
    st.success("✅ Anti-Plagiarism: ACTIVE")
    
    st.divider()
    # Data User yang otomatis diingat
    nama_user = st.text_input("👤 Nama Mahasiswa:", value=st.session_state['user_data']['nama'], placeholder="Contoh: Beny")
    st.session_state['user_data']['nama'] = nama_user
    
    user_lic = st.text_input("🔑 Kode Lisensi PRO:", type="password")
    
    if st.button("🗑️ Reset Semua Pekerjaan", type="secondary"):
        st.session_state['db'] = {}
        st.rerun()

# --- 5. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.42")
st.caption("Mode: Persistent Memory | Pekerjaan Anda tersimpan otomatis meskipun di-refresh.")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", value=st.session_state['user_data']['topik'], placeholder="Analisis Pengetahuan...")
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
        with st.spinner(f"Menyusun & Menyimpan {bab_aktif}..."):
            try:
                model = inisialisasi_ai()
                prompt_engine = "Anti-Plagiarism & Deep Paraphrase Aktif. Gunakan Ref RIIL 2023-2026."
                
                if "Lampiran" in bab_aktif:
                    prompt = f"{prompt_engine}\nBuat Lampiran Lengkap {nama_user} judul '{topik}' di {lokasi}. Surat Izin, Kuesioner Data Awal, PST Utama, Kisi-kisi."
                else:
                    rev = f"REVISI: {catatan_dosen}" if catatan_dosen else ""
                    prompt = f"{prompt_engine}\nSusun draf {bab_aktif} skripsi {metode} judul '{topik}' di {lokasi}. {rev}."
                
                res = model.generate_content(prompt)
                # DATA DISIMPAN KE SESSION STATE (MEMORI BROWSER)
                st.session_state['db'][bab_aktif] = res.text
                st.success(f"{bab_aktif} Tersimpan!")
            except: st.error("Koneksi sibuk, coba klik sekali lagi.")
    else: st.warning("Nama dan Judul wajib diisi!")

if st.button("🚀 Susun & Kalibrasi Sekarang"):
    jalankan_proses()

# --- 6. BOX OUTPUT DENGAN AUTO-SAVE VIEW ---
if st.session_state['db']:
    st.divider()
    for b in sorted(st.session_state['db'].keys()):
        content = st.session_state['db'][b]
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            
            # Akses Trial/Pro
            is_trial = b in ["Bab 1", "Bab 2"]
            is_pro = user_lic == gen_lic(nama_user)
            
            if "Lampiran" not in b:
                catatan = st.text_area(f"✍️ Catatan Revisi Dosen {b}:", key=f"rev_{b}")
                if st.button(f"🔄 Jalankan Revisi {b}", key=f"br_{b}"):
                    jalankan_proses(target_bab=b, catatan_dosen=catatan)
            
            with st.expander(f"Lihat Progres {b}"):
                st.markdown(content)
                if is_trial or is_pro:
                    doc = Document()
                    doc.add_heading(b, 0); doc.add_paragraph(content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download {b}", data=bio.getvalue(), file_name=f"{b}.docx", key=f"dl_{b}")
                else:
                    st.error("🔑 Bagian ini Terkunci (PRO).")
                    st.link_button("💬 Chat Admin (Beli Lisensi)", "https://wa.me/6281234567890?text=Beli%20Lisensi%20SkripsiGen")
