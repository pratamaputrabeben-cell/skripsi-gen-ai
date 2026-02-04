import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime

# --- 1. KONFIGURASI API (MODEL FLASH - GRATIS & CEPAT) ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Kita kunci ke model flash agar kuota gratisnya melimpah (15 RPM)
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error("Koneksi API Terputus. Cek pengaturan Secrets kamu."); st.stop()

# --- 2. LOGIKA LISENSI ---
def gen_lic(n):
    d = datetime.now().strftime("%d%m")
    nm = n.split(' ')[0].upper() if n else "USER"
    return f"PRO-{nm}-{d}-SKR"

# --- 3. SESSION STATE ---
if 'db' not in st.session_state: st.session_state['db'] = {}
if 'pus' not in st.session_state: st.session_state['pus'] = ""

# --- 4. UI SETUP ---
st.set_page_config(page_title="SkripsiGen Pro v8.13", layout="wide")

with st.sidebar:
    st.header("🔓 Aktivasi")
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Budi Santoso")
    user_lic = st.text_input("🔑 Kode Lisensi:", type="password")
    
    st.divider()
    st.write("🔍 **Cek Jurnal Riil**")
    cj = st.text_input("Salin Judul/DOI:", placeholder="Cek keaslian...")
    if cj:
        st.link_button("Cek di Google Scholar ↗️", f"https://scholar.google.com/scholar?q={cj.replace(' ', '+')}")

    st.divider()
    with st.expander("🛠️ MENU OWNER"):
        pw = st.text_input("Password Admin:", type="password")
        if pw == "BEBEN-BOSS":
            st.subheader("Buat Kode Lisensi")
            pbl = st.text_input("Nama Pembeli:")
            if st.button("Generate ✨"):
                st.code(gen_lic(pbl))
                st.info("Berikan kode ini ke pembeli.")

# --- 5. MAIN CONTENT ---
st.title("🎓 SkripsiGen Pro v8.13")
st.caption("Mode Stabil: Gratis & Cepat | Standar Akademik 2026")

c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Analisis Kepuasan Pelanggan...")
    lokasi = st.text_input("📍 Lokasi:", placeholder="Contoh: PT. Maju Bersama")
with c2:
    kota = st.text_input("🏙️ Kota:", placeholder="Contoh: Jakarta")
    metode = st.selectbox("🔬 Metode:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()
pil_bab = st.selectbox("📄 Pilih Bagian:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran"])

if st.button("🚀 Susun Draf Skripsi"):
    if topik and nama_user:
        with st.spinner("Kecerdasan Buatan sedang menyusun draf..."):
            # Perintah khusus referensi riil
            prompt = f"Buat draf {pil_bab} skripsi {metode} judul '{topik}' lokasi {lokasi}. Gunakan ahli riil, APA 7th, dan referensi tahun 2023-2026. Akhiri dengan Daftar Pustaka."
            try:
                res = model.generate_content(prompt).text
                st.session_state['db'][pil_bab] = res
                st.rerun()
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ Server sedang penuh/antre. Mohon tunggu 30-60 detik lalu klik tombol lagi.")
                else:
                    st.error(f"Terjadi kendala teknis: {e}")
    else:
        st.warning("Silakan isi Nama (di sidebar) dan Judul Skripsi!")

# --- 6. DOKUMEN BOX ---
if st.session_state['db']:
    for b, content in st.session_state['db'].items():
        with st.container(border=True):
            st.markdown(f"### 📄 {b}")
            st.markdown(content[:300] + "...")
            with st.expander("Lihat Full & Download"):
                st.markdown(content)
                if user_lic == gen_lic(nama_user):
                    doc = Document()
                    doc.add_heading(b, 0)
                    doc.add_paragraph(content)
                    bio = BytesIO(); doc.save(bio)
                    st.download_button(f"📥 Download Word ({b})", data=bio.getvalue(), file_name=f"{b}.docx", key=f"d_{b}")
                else:
                    st.warning("⚠️ Masukkan kode lisensi di sidebar untuk mendownload file Word.")
