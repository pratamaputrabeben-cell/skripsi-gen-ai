import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime
import random

# --- 1. KONEKSI MULTI-KEY & AUTO-MODEL ---
# Mengambil daftar key dari Secrets (Pastikan di Secrets namanya GEMINI_API_KEYS)
ALL_KEYS = st.secrets.get("GEMINI_API_KEYS", [st.secrets.get("GEMINI_API_KEY", "")])

def inisialisasi_ai():
    if not ALL_KEYS or ALL_KEYS[0] == "":
        st.error("API Key belum dipasang di Secrets!"); st.stop()
        
    # Pilih satu key secara acak
    key_aktif = random.choice(ALL_KEYS)
    genai.configure(api_key=key_aktif)
    
    # DAFTAR NAMA MODEL TERBARU 2026 (Urutan Prioritas)
    # Kita tidak pakai 'models/gemini-pro' lagi karena sudah dihapus Google
    model_targets = ['gemini-1.5-flash', 'gemini-1.5-pro']
    
    try:
        # Cek model apa yang benar-benar tersedia di akun kamu
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        for target in model_targets:
            for real_model in available_models:
                if target in real_model:
                    return genai.GenerativeModel(real_model)
        
        # Jika tidak ada yang cocok, ambil yang pertama tersedia
        return genai.GenerativeModel(available_models[0])
    except:
        # Fallback terakhir jika list_models gagal
        return genai.GenerativeModel('gemini-1.5-flash')

try:
    model = inisialisasi_ai()
    nama_mesin = model.model_name
except Exception as e:
    st.error(f"Gagal Inisialisasi: {e}"); st.stop()

# --- 2. SISTEM LISENSI ---
def gen_lic(n):
    d = datetime.now().strftime("%d%m")
    nm = n.split(' ')[0].upper() if n else "USER"
    return f"PRO-{nm}-{d}-SKR"

# --- 3. DATABASE & UI ---
if 'db' not in st.session_state: st.session_state['db'] = {}
st.set_page_config(page_title="SkripsiGen Pro v8.22", layout="wide")

with st.sidebar:
    st.header("🔓 Aktivasi")
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Budi Santoso")
    user_lic = st.text_input("🔑 Kode Lisensi:", type="password")
    st.divider()
    with st.expander("🛠️ MENU OWNER"):
        pw = st.text_input("Admin Pass:", type="password")
        if pw == "BEBEN-BOSS":
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate ✨"): st.code(gen_lic(pbl))

# --- 4. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.22")
st.caption(f"Jalur Aktif: {nama_mesin} | Status: Online")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Analisis Pengaruh X terhadap Y...")
    lokasi = st.text_input("📍 Lokasi:", placeholder="Contoh: PT. ABC")
with c2:
    kota = st.text_input("🏙️ Kota:", placeholder="Contoh: Jakarta")
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran"])

if st.button("🚀 Susun Draf Skripsi"):
    if topik and nama_user:
        with st.spinner("AI sedang meriset jurnal riil & membedah variabel..."):
            # Prompt tetap mempertahankan fitur Bedah Variabel & Referensi Riil
            prompt = f"""
            Buatkan draf {pil_bab} skripsi {metode} dengan judul '{topik}' di {lokasi}, {kota}.
            Instruksi Khusus:
            1. Bedah variabel dari judul secara mendalam.
            2. Gunakan referensi ahli riil tahun 2023-2026.
            3. Ikuti standar APA 7th Edition.
            4. Gunakan bahasa akademik formal Indonesia.
            """
            try:
                res = model.generate_content(prompt)
                st.session_state['db'][pil_bab] = res.text
                st.rerun()
            except Exception as e:
                if "429" in str(e):
                    st.warning("⚠️ Jalur penuh, mencoba pindah jalur... Klik tombol sekali lagi!")
                else:
                    st.error(f"Kendala: {e}")
    else: st.warning("Isi Nama & Judul!")

# --- 5. BOX OUTPUT ---
if st.session_state['db']:
    st.divider()
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            col1, col2 = st.columns([5, 1])
            col1.markdown(f"### 📄 {b}")
            if col2.button("🗑️ Hapus", key=f"del_{b}"):
                del st.session_state['db'][b]; st.rerun()
            
            st.markdown(content[:300] + "...")
            with st.expander("Lihat & Download"):
                st.markdown(content)
                if user_lic == gen_lic(nama_user):
                    doc = Document()
                    doc.add_heading(b, 0); doc.add_paragraph(content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download Word", data=bio.getvalue(), file_name=f"{b}.docx", key=f"d_{b}")
                else: st.warning("Masukkan lisensi di sidebar untuk download.")
