import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import datetime

# --- 1. KONEKSI API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    def get_active_model_name():
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods: return m.name
        except: pass
        return "models/gemini-pro"
    active_model = get_active_model_name()
    model = genai.GenerativeModel(active_model)
except Exception as e:
    st.error(f"Koneksi Gagal: {e}")
    st.stop()

# --- 2. LOGIKA LISENSI ---
def generate_license_logic(nama):
    hari_ini = datetime.now().strftime("%d%m")
    nama_clean = nama.split(' ')[0].upper() if nama else "USER"
    return f"PRO-{nama_clean}-{hari_ini}-SKR"

# --- 3. TAMPILAN ---
st.set_page_config(page_title="SkripsiGen Pro - Surat Otomatis", layout="wide")

with st.expander("🛠️ Admin Panel (Owner Only)"):
    kunci_admin = st.text_input("Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        st.subheader("Generator Kode Lisensi")
        nama_pembeli = st.text_input("Nama Pembeli:")
        if st.button("Generate Kode"):
            st.code(generate_license_logic(nama_pembeli))

st.title("🎓 SkripsiGen Pro v5.9")

col1, col2 = st.columns(2)
with col1:
    nama_user = st.text_input("👤 Nama Lengkap Anda:", placeholder="Budi Santoso")
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Pengaruh Lingkungan Kerja...")

with col2:
    metode = st.selectbox("🔬 Pilih Metodologi Penelitian:", ["Kuantitatif", "Kualitatif", "R&D"])
    bab_pilihan = st.selectbox("📄 Pilih Bab/Dokumen:", 
                              ["Bab 1: Pendahuluan", "Bab 2: Tinjauan Pustaka", "Bab 3: Metodologi Penelitian", 
                               "Bab 4: Hasil dan Pembahasan", "Bab 5: Penutup", 
                               "Lampiran: Instrumen Penelitian", "Lampiran: Surat Izin Penelitian"])

with st.sidebar:
    st.header("🔓 Aktivasi Download")
    wa_number = "6283173826717"
    st.link_button("📲 Beli Lisensi via WA", f"https://wa.me/{wa_number}")
    user_license = st.text_input("Masukkan Kode Lisensi:", type="password")

# --- 4. PROSES GENERATE ---
if st.button(f"Generate {bab_pilihan} ✨"):
    if topik and nama_user:
        with st.spinner(f"Menyusun {bab_pilihan}..."):
            is_surat = "Surat Izin" in bab_pilihan
            
            if is_surat:
                instruksi = f"Buatkan ISI SURAT saja untuk permohonan izin penelitian mahasiswa nama {nama_user} judul {topik}. Mulai dari Salam Pembuka sampai Salam Penutup. Jangan buat Kop Surat."
            else:
                instruksi = f"Buatkan draf {bab_pilihan} formal dan mendalam."

            try:
                prompt = f"Judul: {topik}\nMetode: {metode}\nNama: {nama_user}\nTugas: {instruksi}\nBahasa Indonesia Formal."
                response = model.generate_content(prompt)
                hasil = response.text
                
                st.divider()
                st.write(hasil)
                
                if user_license == generate_license_logic(nama_user):
                    st.success("✅ Lisensi Aktif!")
                    doc = Document()
                    
                    if is_surat:
                        # --- TEMPLATE SURAT OTOMATIS ---
                        tgl_sekarang = datetime.now().strftime("%d %B %Y")
                        p = doc.add_paragraph(f"Jakarta, {tgl_sekarang}") # Lokasi bisa diubah manual nanti
                        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                        
                        doc.add_paragraph("\nNomor\t: 001/SP/XII/2026\nPerihal\t: Permohonan Izin Penelitian\nLampiran\t: 1 Berkas")
                        doc.add_paragraph("\nYth. Pimpinan Instansi / Kepala Sekolah\ndi Tempat")
                        
                        isi = doc.add_paragraph(hasil)
                        
                        doc.add_paragraph("\n\nHormat Saya,")
                        doc.add_paragraph("\n\n\n( " + nama_user + " )")
                    else:
                        doc.add_heading(f"{bab_pilihan}", 0)
                        doc.add_paragraph(hasil)
                    
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button("📥 Download File Word", data=bio.getvalue(), file_name=f"{bab_pilihan.replace(':', '')}.docx")
                else:
                    st.warning("⚠️ Masukkan Kode Lisensi untuk download.")
            except Exception as e:
                st.error(f"Gagal: {e}")
    else:
        st.warning("Isi Nama dan Judul dulu!")
