import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime
import random

# --- 1. KONEKSI MULTI-KEY (OTOMATIS) ---
# Mengambil daftar key dari Secrets
ALL_KEYS = st.secrets.get("GEMINI_API_KEYS", [st.secrets["GEMINI_API_KEY"]])

def inisialisasi_ai():
    # Pilih satu key secara acak untuk membagi beban (Anti-Limit)
    key_aktif = random.choice(ALL_KEYS)
    genai.configure(api_key=key_aktif)
    
    # Cari model 1.5-flash (Gratis & Tercepat)
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if '1.5-flash' in m.name: return genai.GenerativeModel(m.name)
    return genai.GenerativeModel('gemini-pro')

try:
    model = inisialisasi_ai()
    nama_mesin = model.model_name
except Exception as e:
    st.error(f"Gagal memanggil AI: {e}"); st.stop()

# --- 2. SISTEM LISENSI ---
def gen_lic(n):
    d = datetime.now().strftime("%d%m")
    nm = n.split(' ')[0].upper() if n else "USER"
    return f"PRO-{nm}-{d}-SKR"

# --- 3. DATABASE & UI ---
if 'db' not in st.session_state: st.session_state['db'] = {}
st.set_page_config(page_title="SkripsiGen Pro v8.21", layout="wide")

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
st.title("🎓 SkripsiGen Pro v8.21")
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

if st.button("🚀 Susun Draf Skripsi (Turbo Mode)"):
    if topik and nama_user:
        with st.spinner("AI sedang meriset jurnal riil..."):
            prompt = f"Buat draf {pil_bab} skripsi {metode} judul '{topik}' di {lokasi}. Bedah variabel, kutip ahli riil 2023-2026, format APA 7th."
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
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            st.markdown(content[:300] + "...")
            with st.expander("Lihat & Download"):
                st.markdown(content)
                if user_lic == gen_lic(nama_user):
                    doc = Document()
                    doc.add_heading(b, 0); doc.add_paragraph(content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download Word", data=bio.getvalue(), file_name=f"{b}.docx", key=f"d_{b}")
                else: st.warning("Masukkan lisensi di sidebar untuk download.")
