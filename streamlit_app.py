import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime

# --- 1. KONEKSI API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    def get_model():
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods: return m.name
        except: pass
        return "models/gemini-pro"
    model = genai.GenerativeModel(get_model())
except Exception as e:
    st.error(f"API Error: {e}"); st.stop()

# --- 2. LOGIKA LISENSI ---
def gen_lic(n):
    d = datetime.now().strftime("%d%m")
    nm = n.split(' ')[0].upper() if n else "USER"
    return f"PRO-{nm}-{d}-SKR"

# --- 3. SESSION STATE ---
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'pus' not in st.session_state: st.session_state['pus'] = ""

# --- 4. UI SETUP ---
st.set_page_config(page_title="SkripsiGen Pro v8.11", layout="wide")

# SIDEBAR
with st.sidebar:
    st.header("🔓 Aktivasi")
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Budi Santoso")
    user_lic = st.text_input("🔑 Kode Lisensi:", type="password")
    
    st.divider()
    st.write("🔍 **Cek Jurnal**")
    cj = st.text_input("Judul/DOI:", placeholder="Cek keaslian...")
    if cj:
        st.link_button("Cek Google Scholar", f"https://scholar.google.com/scholar?q={cj.replace(' ', '+')}")

    st.divider()
    with st.expander("🛠️ MENU OWNER"):
        pw = st.text_input("Password Admin:", type="password")
        if pw == "BEBEN-BOSS":
            st.subheader("Buat Kode")
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate ✨"):
                st.code(gen_lic(pbl))

# --- 5. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.11")
st.caption("Standard 2026 | Ref 2023-2026 | Academic Style")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Analisis...")
    lokasi = st.text_input("📍 Lokasi:", placeholder="PT. ABC")
with c2:
    kota = st.text_input("🏙️ Kota/Prov:", placeholder="Jakarta")
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran"])

if st.button("🚀 Generate Draf"):
    if topik and nama_user:
        with st.spinner("Menyusun draf..."):
            # Baris ini sudah disatukan agar tidak terpotong:
            rnt = "2023-2026"; old = st.session_state['pus']
            prompt = f"Buat draf {pil_bab} skripsi {metode} judul '{topik}' lokasi {lokasi}. Gunakan ahli RIIL, APA 7th, referensi {rnt}. Pustaka: {old}"
            try:
                res = model.generate_content(prompt).text
                st.session_state['db'][pil_bab] = res
                if "DAFTAR PUSTAKA" in res.upper():
                    st.session_state['pus'] += "\n" + res.upper().split("DAFTAR PUSTAKA")[-1]
                st.rerun()
            except Exception as e:
                st.error("Limit API harian tercapai atau koneksi terputus. Tunggu 1 menit.")
    else:
        st.warning("Isi Nama di sidebar & Judul!")

# --- 6. DOCUMENT BOX ---
if st.session_state['db']:
    st.divider()
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            st.markdown(content[:300] + "...")
            with st.expander("Lihat & Download"):
                st.markdown(content)
                if user_lic == gen_lic(nama_user):
                    doc = Document()
                    doc.add_heading(b, 0)
                    doc.add_paragraph(content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"Download {b}", data=bio.getvalue(), file_name=f"{b}.docx", key=f"d_{b}")
                else:
                    st.warning("Masukkan lisensi untuk download.")
