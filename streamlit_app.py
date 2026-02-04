import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime

# --- 1. KONFIGURASI API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("API Key belum terpasang di Secrets.")
    st.stop()

model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. LOGIKA LISENSI ---
def generate_license_logic(nama):
    hari_ini = datetime.now().strftime("%d%m")
    nama_clean = nama.split(' ')[0].upper() if nama else "USER"
    return f"PRO-{nama_clean}-{hari_ini}-SKR"

# --- 3. TAMPILAN ---
st.set_page_config(page_title="SkripsiGen Pro - Full Package", layout="wide")

# PANEL ADMIN TETAP DI ATAS
with st.expander("🛠️ Admin Panel (Owner Only)"):
    kunci_admin = st.text_input("Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        st.subheader("Generator Kode Lisensi")
        nama_pembeli = st.text_input("Nama Pembeli:")
        if st.button("Generate Kode"):
            st.code(generate_license_logic(nama_pembeli))
    else: st.write("Terkunci.")

st.title("🎓 SkripsiGen Pro v5.6")

# --- 4. FORM UTAMA (DI TENGAH) ---
st.info("Selesaikan skripsi Anda dalam hitungan detik dengan AI Standar Akademik.")

col1, col2 = st.columns(2)
with col1:
    nama_user = st.text_input("👤 Nama Lengkap Anda:", placeholder="Budi Santoso")
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Analisis Kinerja...")

with col2:
    # --- INI DIA PILIHAN METODENYA (SEKARANG DI TENGAH) ---
    metode = st.selectbox("🔬 Pilih Metodologi Penelitian:", 
                         ["Kuantitatif (Data Angka/Statistik)", 
                          "Kualitatif (Wawancara/Studi Kasus)", 
                          "R&D (Pengembangan Produk/Sistem)"])
    
    bab_pilihan = st.selectbox("📄 Pilih Bab/Dokumen:", 
                              ["Bab 1: Pendahuluan", 
                               "Bab 2: Tinjauan Pustaka", 
                               "Bab 3: Metodologi Penelitian", 
                               "Bab 4: Hasil dan Pembahasan", 
                               "Bab 5: Penutup",
                               "Lampiran: Instrumen Penelitian"])

# --- 5. SIDEBAR HANYA UNTUK AKTIVASI ---
with st.sidebar:
    st.header("🔓 Aktivasi Download")
    st.write("Draf teks gratis dilihat. Untuk ambil file Word (.docx), silakan beli lisensi.")
    wa_number = "6283173826717"
    st.link_button("📲 Beli Lisensi via WhatsApp", f"https://wa.me/{wa_number}")
    user_license = st.text_input("Masukkan Kode Lisensi:", type="password")

# --- 6. PROSES GENERATE ---
if st.button(f"Generate {bab_pilihan} Sekarang ✨"):
    if topik and nama_user:
        with st.spinner(f"Menyusun {bab_pilihan}..."):
            # Logika Konten
            if "Lampiran" in bab_pilihan:
                if "Kuantitatif" in metode:
                    instruksi = "Buatkan Kuesioner Skala Likert (1-5) lengkap dengan kisi-kisi instrumen."
                elif "Kualitatif" in metode:
                    instruksi = "Buatkan Pedoman Wawancara mendalam dengan daftar pertanyaan terbuka."
                else:
                    instruksi = "Buatkan Lembar Validasi Ahli untuk menguji produk (Materi & Media)."
            else:
                instruksi = f"Buatkan draf {bab_pilihan} yang sangat formal, mendalam, dan anti-plagiat."

            try:
                prompt = f"Judul: {topik}\nMetode: {metode}\nTugas: {instruksi}\nSertakan Daftar Pustaka APA 7th Edition."
                response = model.generate_content(prompt)
                hasil = response.text
                
                st.divider()
                st.markdown(f"### 📄 Hasil Preview {bab_pilihan}")
                st.write(hasil)
                
                # VALIDASI LISENSI
                if user_license == generate_license_logic(nama_user):
                    st.success("✅ Lisensi Aktif! File Word siap diunduh.")
                    doc = Document()
                    doc.add_heading(f"{bab_pilihan}", 0)
                    doc.add_paragraph(hasil)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button("📥 Download File Word (.docx)", data=bio.getvalue(), file_name=f"{bab_pilihan}_{nama_user}.docx")
                else:
                    st.warning("⚠️ Masukkan Kode Lisensi di sidebar untuk download file Word.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Nama dan Judul tidak boleh kosong!")
