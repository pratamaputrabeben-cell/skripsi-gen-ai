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
    hari_ini = datetime.now().strftime("%d%m") # Format: TanggalBulan (Contoh: 0402)
    nama_clean = nama.split(' ')[0].upper()
    # Rumus: PRO-[NAMA]-0402-[KODE_UNIK]
    return f"PRO-{nama_clean}-{hari_ini}-SKR"

# --- 3. TAMPILAN WEBSITE ---
st.set_page_config(page_title="SkripsiGen Pro - Vendor Edition", layout="wide")

# --- FITUR ADMIN (HANYA UNTUK KAMU) ---
with st.expander("🛠️ Admin Panel (Khusus Owner)"):
    kunci_admin = st.text_input("Masukkan Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS": # GANTI INI DENGAN PASSWORD ADMINMU
        st.subheader("Generator Kode Lisensi")
        nama_pembeli = st.text_input("Input Nama Pembeli:")
        if st.button("Generate Kode"):
            hasil_kode = generate_license_logic(nama_pembeli)
            st.code(hasil_kode, language="text")
            st.success(f"Berikan kode di atas kepada {nama_pembeli}")
    else:
        st.write("Silakan masukkan kunci admin untuk generate lisensi.")

st.title("🎓 SkripsiGen Pro v5.0")

# --- 4. TAMPILAN UNTUK PEMBELI ---
with st.sidebar:
    st.header("👤 Identitas Pengguna")
    nama_user = st.text_input("Nama Lengkap:", placeholder="Contoh: Budi Santoso")
    
    st.divider()
    st.header("⚙️ Pengaturan Bab")
    topik = st.text_input("Judul Skripsi:")
    bab_pilihan = st.selectbox("Pilih Bab:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5"])
    
    st.divider()
    st.write("🔓 **Aktivasi Download**")
    wa_number = "6283173826717"
    pesan_wa = f"Halo Gan, saya {nama_user}. Saya mau beli Kode Lisensi."
    st.link_button("📲 Beli Lisensi via WA", f"https://wa.me/{wa_number}?text={pesan_wa.replace(' ', '%20')}")
    
    user_license = st.text_input("Masukkan Kode Lisensi:", type="password")

# --- 5. LOGIKA GENERATE ---
if st.button(f"Generate Draf {bab_pilihan} ✨"):
    if topik and nama_user:
        with st.spinner("Menyusun draf..."):
            try:
                response = model.generate_content(f"Buatkan draf {bab_pilihan} skripsi tentang '{topik}'. Bahasa formal Indonesia.")
                hasil_teks = response.text
                
                st.markdown(f"### 📄 Preview untuk {nama_user}")
                st.write(hasil_teks)
                
                # VALIDASI LISENSI
                kode_seharusnya = generate_license_logic(nama_user)
                if user_license == kode_seharusnya: 
                    st.success(f"✅ Lisensi Aktif!")
                    doc = Document()
                    doc.add_heading(f"{bab_pilihan}: {topik}", 0)
                    doc.add_paragraph(hasil_teks)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button("📥 Download File Word (.docx)", data=bio.getvalue(), file_name=f"Draf_{nama_user}.docx")
                else:
                    st.warning("⚠️ Kode Lisensi salah atau tidak sesuai nama. Silakan beli ke admin.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Isi Nama dan Judul dulu!")
