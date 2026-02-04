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

# --- 2. RUMUS RAHASIA LISENSI ---
def generate_license_logic(nama):
    hari_ini = datetime.now().strftime("%d%m")
    nama_clean = nama.split(' ')[0].upper() if nama else "USER"
    return f"PRO-{nama_clean}-{hari_ini}-SKR"

# --- 3. TAMPILAN WEBSITE ---
st.set_page_config(page_title="SkripsiGen Pro - Full Package", layout="wide")

# --- FITUR ADMIN ---
with st.expander("🛠️ Admin Panel (Khusus Owner)"):
    kunci_admin = st.text_input("Masukkan Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        st.subheader("Generator Kode Lisensi")
        nama_pembeli = st.text_input("Input Nama Pembeli:")
        if st.button("Generate Kode"):
            hasil_kode = generate_license_logic(nama_pembeli)
            st.code(hasil_kode, language="text")
            st.success(f"Berikan kode ini ke {nama_pembeli}")
    else:
        st.write("Panel terkunci.")

st.title("🎓 SkripsiGen Pro v5.5")

# --- 4. TAMPILAN SIDEBAR ---
with st.sidebar:
    st.header("👤 Identitas Pengguna")
    nama_user = st.text_input("Nama Lengkap:", placeholder="Budi Santoso")
    
    st.divider()
    st.header("⚙️ Pengaturan Skripsi")
    topik = st.text_input("Judul Skripsi:")
    metode = st.radio("Metode Penelitian:", ["Kuantitatif", "Kualitatif", "R&D"])
    
    # Tambahan menu Lampiran
    bab_pilihan = st.selectbox("Pilih Bab/Dokumen:", 
                              ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", "Lampiran: Instrumen Penelitian"])
    
    st.divider()
    st.write("🔓 **Aktivasi Download**")
    wa_number = "6283173826717"
    st.link_button("📲 Beli Lisensi via WA", f"https://wa.me/{wa_number}")
    user_license = st.text_input("Masukkan Kode Lisensi:", type="password")

# --- 5. LOGIKA GENERATE ---
if st.button(f"Generate {bab_pilihan} ✨"):
    if topik and nama_user:
        with st.spinner(f"Sedang menyusun {bab_pilihan}..."):
            
            # Pengaturan Prompt Khusus Lampiran
            if "Lampiran" in bab_pilihan:
                if metode == "Kuantitatif":
                    instruksi = "Buatkan Kuesioner penelitian dengan Skala Likert (1-5). Sertakan kisi-kisi instrumen dan daftar pertanyaan yang valid sesuai variabel."
                elif metode == "Kualitatif":
                    instruksi = "Buatkan Pedoman Wawancara mendalam (Indepth Interview) untuk informan kunci, lengkap dengan daftar pertanyaan terbuka."
                else: # R&D
                    instruksi = "Buatkan Lembar Validasi Ahli (Materi/Media) untuk menguji produk yang dikembangkan."
            else:
                instruksi = f"Buatkan draf {bab_pilihan} sesuai kaidah akademik Indonesia."

            full_prompt = f"Judul: {topik}\nMetode: {metode}\nTugas: {instruksi}\nFormat: Bahasa Indonesia Formal, Anti-Plagiat, Profesional."
            
            try:
                response = model.generate_content(full_prompt)
                hasil_teks = response.text
                
                st.markdown(f"### 📄 Hasil {bab_pilihan}")
                st.write(hasil_teks)
                
                # VALIDASI LISENSI UNTUK DOWNLOAD
                kode_seharusnya = generate_license_logic(nama_user)
                if user_license == kode_seharusnya:
                    st.success("✅ Lisensi Aktif!")
                    doc = Document()
                    doc.add_heading(f"{bab_pilihan}: {topik}", 0)
                    doc.add_paragraph(hasil_teks)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button("📥 Download File Word", data=bio.getvalue(), file_name=f"{bab_pilihan}_{nama_user}.docx")
                else:
                    st.warning("⚠️ Fitur download terkunci. Hubungi admin untuk kode lisensi.")
                    
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Nama dan Judul wajib diisi!")
