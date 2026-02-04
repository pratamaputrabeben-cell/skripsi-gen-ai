import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from datetime import datetime

# --- 1. KONFIGURASI API (DENGAN PENANGANAN ERROR MODEL) ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Fungsi otomatis mencari model yang aktif di akun Anda
    def get_active_model_name():
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # Cari yang ada nama 'flash' dulu, kalau tidak ada pakai apa saja yang tersedia
                    return m.name
        except:
            return "models/gemini-pro" # Fallback terakhir
            
    active_model = get_active_model_name()
    model = genai.GenerativeModel(active_model)
except Exception as e:
    st.error(f"Koneksi API Gagal: {e}")
    st.stop()

# --- 2. LOGIKA LISENSI ---
def generate_license_logic(nama):
    hari_ini = datetime.now().strftime("%d%m")
    nama_clean = nama.split(' ')[0].upper() if nama else "USER"
    return f"PRO-{nama_clean}-{hari_ini}-SKR"

# --- 3. TAMPILAN ---
st.set_page_config(page_title="SkripsiGen Pro - Anti Error", layout="wide")

with st.expander("🛠️ Admin Panel (Owner Only)"):
    kunci_admin = st.text_input("Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        st.subheader("Generator Kode Lisensi")
        nama_pembeli = st.text_input("Nama Pembeli:")
        if st.button("Generate Kode"):
            st.code(generate_license_logic(nama_pembeli))
    else: st.write("Terkunci.")

st.title("🎓 SkripsiGen Pro v5.8")
st.caption(f"Sistem aktif menggunakan model: {active_model}")

# --- 4. FORM UTAMA ---
col1, col2 = st.columns(2)
with col1:
    nama_user = st.text_input("👤 Nama Lengkap Anda:", placeholder="Budi Santoso")
    topik = st.text_input("📝 Judul Skripsi:", placeholder="Contoh: Pengaruh Lingkungan Kerja...")

with col2:
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
                               "Lampiran: Instrumen Penelitian",
                               "Lampiran: Surat Izin Penelitian"])

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("🔓 Aktivasi Download")
    st.write("Beli lisensi untuk ambil file Word (.docx).")
    wa_number = "6283173826717"
    st.link_button("📲 Beli Lisensi via WhatsApp", f"https://wa.me/{wa_number}")
    user_license = st.text_input("Masukkan Kode Lisensi:", type="password")

# --- 6. PROSES GENERATE ---
if st.button(f"Generate {bab_pilihan} ✨"):
    if topik and nama_user:
        with st.spinner(f"Menyusun {bab_pilihan}..."):
            # --- LOGIKA KONTEN ---
            if "Instrumen" in bab_pilihan:
                if "Kuantitatif" in metode:
                    instruksi = "Buatkan Kuesioner Skala Likert (1-5) lengkap dengan kisi-kisi instrumen."
                elif "Kualitatif" in metode:
                    instruksi = "Buatkan Pedoman Wawancara mendalam dengan daftar pertanyaan terbuka."
                else:
                    instruksi = "Buatkan Lembar Validasi Ahli untuk menguji produk (Materi & Media)."
            elif "Surat Izin" in bab_pilihan:
                instruksi = f"Buatkan draf Surat Permohonan Izin Penelitian formal atas nama {nama_user} untuk judul {topik}."
            else:
                instruksi = f"Buatkan draf {bab_pilihan} yang sangat formal, mendalam, dan anti-plagiat."

            try:
                prompt = f"Judul: {topik}\nMetode: {metode}\nNama Mahasiswa: {nama_user}\nTugas: {instruksi}\nSertakan Daftar Pustaka APA 7th Edition."
                
                # Menggunakan generate_content dengan penanganan fallback jika nama model berubah
                response = model.generate_content(prompt)
                hasil = response.text
                
                st.divider()
                st.markdown(f"### 📄 Hasil Preview {bab_pilihan}")
                st.write(hasil)
                
                # VALIDASI LISENSI
                if user_license == generate_license_logic(nama_user):
                    st.success("✅ Lisensi Aktif!")
                    doc = Document()
                    doc.add_heading(
