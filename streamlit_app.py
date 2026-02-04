import streamlit as st
import google.generativeai as genai
from docx import Document
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
st.set_page_config(page_title="SkripsiGen Pro - Full Package", layout="wide")

with st.expander("🛠️ Admin Panel (Owner Only)"):
    kunci_admin = st.text_input("Kunci Admin:", type="password")
    if kunci_admin == "BEBEN-BOSS":
        st.subheader("Generator Kode Lisensi")
        nama_pembeli = st.text_input("Nama Pembeli:")
        if st.button("Generate Kode"):
            st.code(generate_license_logic(nama_pembeli))

st.title("🎓 SkripsiGen Pro v6.1")

# --- TAB SISTEM ---
tab_buat, tab_revisi = st.tabs(["📝 Buat Draf Baru", "🔄 Fitur Revisi Dosen"])

with tab_buat:
    col1, col2 = st.columns(2)
    with col1:
        nama_user = st.text_input("👤 Nama Lengkap Anda:", key="n1")
        topik = st.text_input("📝 Judul Skripsi:", key="t1")
    with col2:
        metode = st.selectbox("🔬 Pilih Metode:", ["Kuantitatif", "Kualitatif", "R&D"], key="m1")
        bab_pilihan = st.selectbox("📄 Pilih Bab/Dokumen:", 
                                  ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5", 
                                   "Lampiran: Instrumen", "Lampiran: Surat Izin"], key="b1")

    if st.button("Generate Draf Sekarang ✨"):
        if topik and nama_user:
            with st.spinner(f"Menyusun {bab_pilihan}..."):
                # Logika Instruksi
                if "Instrumen" in bab_pilihan:
                    instruksi = f"Buatkan instrumen penelitian {metode} (kuesioner/pedoman wawancara) untuk judul {topik}."
                elif "Surat Izin" in bab_pilihan:
                    instruksi = f"Buatkan surat izin penelitian formal atas nama {nama_user} untuk judul {topik}."
                else:
                    instruksi = f"Buatkan draf {bab_pilihan} skripsi {metode} formal, mendalam, anti-plagiat, dan sertakan daftar pustaka."
                
                try:
                    prompt = f"Judul: {topik}\nMetode: {metode}\nNama: {nama_user}\nTugas: {instruksi}"
                    response = model.generate_content(prompt)
                    hasil = response.text
                    st.divider()
                    st.write(hasil)
                    
                    # Simpan ke session state agar bisa di-download setelah cek lisensi
                    st.session_state['hasil_gen'] = hasil
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Isi Nama dan Judul dulu!")

with tab_revisi:
    st.info("Gunakan tab ini untuk memperbaiki draf berdasarkan masukan dosen.")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        nama_rev = st.text_input("👤 Nama Lengkap:", key="n2")
        topik_rev = st.text_input("📝 Judul Saat Ini:", key="t2")
    with col_r2:
        bab_rev = st.selectbox("🎯 Bab yang Direvisi:", ["Bab 1", "Bab 2", "Bab 3", "Bab 4", "Bab 5"], key="b2")
        catatan = st.text_area("✍️ Catatan/Revisi Dosen:", placeholder="Contoh: Tambahkan teori X...")

    if st.button("Proses Revisi 🚀"):
        if catatan and topik_rev:
            with st.spinner("Mengolah revisi..."):
                prompt_rev = f"Mahasiswa {nama_rev} judul {topik_rev}. Revisi {bab_rev} berdasarkan: {catatan}. Tulis ulang bab tersebut dan jelaskan dampak perubahannya ke bab selanjutnya agar konsisten."
                try:
                    response = model.generate_content(prompt_rev)
                    hasil_rev = response.text
                    st.divider()
                    st.write(hasil_rev)
                    st.session_state['hasil_gen'] = hasil_rev
                except Exception as e:
                    st.error(f"Error: {e}")

# --- SIDEBAR & DOWNLOAD (BERLAKU UNTUK KEDUA TAB) ---
with st.sidebar:
    st.header("🔓 Aktivasi Download")
    st.write("Beli lisensi untuk ambil file Word (.docx).")
    wa_number = "6283173826717"
    st.link_button("📲 Beli Lisensi via WA", f"https://wa.me/{wa_number}")
    user_license = st.text_input("Masukkan Kode Lisensi:", type="password")
    
    # Tombol Download hanya muncul jika sudah ada hasil dan lisensi benar
    if 'hasil_gen' in st.session_state:
        # Cek lisensi (menggunakan nama dari tab mana pun yang diisi)
        current_name = nama_user if nama_user else nama_rev
        if user_license == generate_license_logic(current_name):
            st.success("✅ Lisensi Aktif!")
            doc = Document()
            doc.add_heading("Draf Skripsi", 0)
            doc.add_paragraph(st.session_state['hasil_gen'])
            bio = BytesIO()
            doc.save(bio)
            st.download_button("📥 Download (.docx)", data=bio.getvalue(), file_name="Draf_Skripsi.docx")
        elif user_license != "":
            st.error("❌ Kode Salah!")
