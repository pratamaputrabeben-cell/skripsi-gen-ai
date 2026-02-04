import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime

# --- 1. KONFIGURASI API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    def get_active_model_name():
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods: return m.name
        except: pass
        return "models/gemini-pro"
    model = genai.GenerativeModel(get_active_model_name())
except Exception as e:
    st.error(f"Koneksi API Gagal: {e}")
    st.stop()

# --- 2. LOGIKA LISENSI ---
def generate_license_logic(nama):
    hari_ini = datetime.now().strftime("%d%m")
    nama_clean = nama.split(' ')[0].upper() if nama else "USER"
    return f"PRO-{nama_clean}-{hari_ini}-SKR"

# --- 3. DATABASE SESI ---
if 'db' not in st.session_state:
    st.session_state['db'] = {}
if 'pustaka_koleksi' not in st.session_state:
    st.session_state['pustaka_koleksi'] = ""

# --- 4. TAMPILAN DASHBOARD ---
st.set_page_config(page_title="SkripsiGen Pro v8.8", layout="wide")

with st.sidebar:
    st.header("🔓 Aktivasi & Verifikasi")
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Budi Santoso")
    user_license = st.text_input("🔑 Kode Lisensi:", type="password")
    
    st.divider()
    st.write("🔍 **Pusat Verifikasi Dokumen**")
    st.caption("Salin judul referensi/DOI dari draf untuk dicek keasliannya:")
    cek_judul = st.text_input("Judul/DOI:", placeholder="Contoh: 10.1038/s41586-020-2012-7")
    
    if cek_judul:
        q = cek_judul.replace(' ', '+')
        c1, c2 = st.columns(2)
        with c1:
            st.link_button("Google Scholar", f"https://scholar.google.com/scholar?q={q}")
            st.link_button("Crossref (DOI)", f"https://search.crossref.org/?q={q}")
        with c2:
            st.link_button("DOAJ (Jurnal)", f"https://doaj.org/search/articles?source=%7B%22query%22%3A%7B%22query_string%22%3A%7B%22query%22%3A%22{q}%22%7D%7D%7D")
            st.link_button("PubMed/ResGate", f"https://www.ncbi.nlm.nih.gov/pubmed/?term={q}")

    st.divider()
    if st.button("🗑️ Hapus Semua Progress"):
        st.session_state['db'] = {}
        st.session_state['pustaka_koleksi'] = ""
        st.rerun()
    
    st.link_button("📲 Beli Lisensi (WA)", "https://wa.me/6283173826717")

st.title("🎓 SkripsiGen Pro v8.8")
st.caption("Referensi Terintegrasi: Google Scholar, Crossref, DOAJ, PubMed, & ResearchGate")

# --- 5. INPUT DATA ---
c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Analisis Pengaruh...")
    lokasi = st.text_input("📍 Lokasi Penelitian:", placeholder="Contoh: RSUD Dr. Soetomo / PT. Telkom")
with c2:
    kota = st.text_input("🏙️ Kota & Provinsi:", placeholder="Surabaya, Jawa Timur")
    metode = st.selectbox("🔬 Metode Penelitian:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()

# --- 6. FORM GENERATOR ---
bab_pilihan = st.selectbox("📄 Pilih Bagian pengerjaan:", 
                          ["Bab 1: Pendahuluan", "Bab 2: Tinjauan Pustaka", "Bab 3: Metodologi Penelitian", 
                           "Bab 4: Hasil dan Pembahasan", "Bab 5: Penutup", "Lampiran: Instrumen"])

if st.button("🚀 Generate Draf Akademik"):
    if topik and nama_user:
        with st.spinner("Sinkronisasi database referensi..."):
            thn = 2026
            rentang = f"{thn-3}-{thn}"
            
            # --- PROMPT DATABASE INTEGRATED ---
            prompt = f"""
            Buatkan draf {bab_pilihan} skripsi {metode} judul '{topik}' di {lokasi}.
            
            ATURAN REFERENSI KETAT:
            1. Gunakan literatur yang memiliki pola data RIIL dari Crossref, DOAJ, PubMed, atau ResearchGate.
            2. WAJIB sertakan minimal 5 referensi terbaru tahun {rentang}.
            3. Gunakan tokoh ahli utama di bidang terkait (Misal: Sugiyono, Kotler, Arikunto, atau pakar internasional PubMed).
            4. Untuk Bab 2: Bedah variabel judul satu per satu secara mendalam.
            5. Gunakan Sitasi APA 7th Edition dan Daftar Pustaka kumulatif: {st.session_state['pustaka_koleksi']}.
            """
            
            try:
                res = model.generate_content(prompt).text
                st.session_state['db'][bab_pilihan] = res
                if "DAFTAR PUSTAKA" in res.upper():
                    st.session_state['pustaka_koleksi'] += "\n" + res.upper().split("DAFTAR PUSTAKA")[-1]
                st.rerun()
            except Exception as e: st.error(f"Gagal: {e}")
    else: st.warning("Nama (sidebar) dan Judul wajib diisi!")

# --- 7. BOX MANAGEMENT ---
st.divider()
if not st.session_state['db']:
    st.info("Dokumen akan muncul di sini setelah di-generate.")
else:
    for bab, isi in st.session_state['db'].items():
        with st.container(border=True):
            ch1, ch2 = st.columns([5, 1])
            with ch1: st.markdown(f"### 📄 {bab}")
            with ch2:
                if st.button("🗑️ Hapus", key=f"del_{bab}"):
                    del st.session_state['db'][bab]
                    st.rerun()
            
            st.markdown(isi[:300] + "...")
            with st.expander("Baca & Download"):
                st.markdown(isi)
                st.divider()
                if user_license == generate_license_logic(nama_user):
                    doc = Document()
                    doc.add_heading(bab, 0)
                    doc.add_paragraph(isi)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button(f"📥 Download (.docx)", data=bio.getvalue(), file_name=f"{bab}.docx", key=f"dl_{bab}")
                else:
                    st.warning("Masukkan kode lisensi di sidebar untuk download.")
