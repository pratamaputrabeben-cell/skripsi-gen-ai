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

# --- 3. DATABASE SESI (PERSISTENT STORAGE) ---
if 'db' not in st.session_state:
    st.session_state['db'] = {}
if 'pustaka_koleksi' not in st.session_state:
    st.session_state['pustaka_koleksi'] = ""

# --- 4. TAMPILAN DASHBOARD ---
st.set_page_config(page_title="SkripsiGen Pro v8.5", layout="wide")

with st.sidebar:
    st.header("🔓 Aktivasi & Kontrol")
    nama_user = st.text_input("👤 Nama Mahasiswa:", placeholder="Budi Santoso")
    user_license = st.text_input("🔑 Kode Lisensi:", type="password")
    
    st.divider()
    st.write("🔍 **Verifikasi Referensi**")
    cek_judul = st.text_input("Salin judul jurnal ke sini:", placeholder="Cek keaslian jurnal...")
    if cek_judul:
        st.link_button("Cek di Google Scholar ↗️", f"https://scholar.google.com/scholar?q={cek_judul.replace(' ', '+')}")
    
    st.divider()
    if st.button("🗑️ Hapus Semua Progress"):
        st.session_state['db'] = {}
        st.session_state['pustaka_koleksi'] = ""
        st.rerun()
    
    st.divider()
    st.link_button("📲 Beli Lisensi (WhatsApp)", "https://wa.me/6283173826717")

st.title("🎓 SkripsiGen Pro v8.5")
st.caption("Standar Akademik Terbaru 2026 | Referensi Riil 3 Tahun Terakhir")

# --- 5. INPUT IDENTITAS PENELITIAN ---
c1, c2 = st.columns(2)
with c1:
    topik = st.text_input("📝 Judul Lengkap Skripsi:", placeholder="Contoh: Pengaruh AI terhadap Efisiensi Kerja...")
    lokasi = st.text_input("📍 Lokasi Penelitian:", placeholder="Contoh: PT. Sumber Makmur / Universitas Indonesia")
with c2:
    kota = st.text_input("🏙️ Kota & Provinsi:", placeholder="Contoh: Surabaya, Jawa Timur")
    metode = st.selectbox("🔬 Metode Penelitian:", ["Kuantitatif", "Kualitatif", "R&D"])

st.divider()

# --- 6. FORM GENERATOR ---
col_gen1, col_gen2 = st.columns([2, 1])
with col_gen1:
    bab_pilihan = st.selectbox("📄 Pilih Bagian untuk Dikerjakan:", 
                              ["Bab 1: Pendahuluan", "Bab 2: Tinjauan Pustaka", "Bab 3: Metodologi Penelitian", 
                               "Bab 4: Hasil dan Pembahasan", "Bab 5: Penutup", "Lampiran: Instrumen", "Lampiran: Surat Izin"])
with col_gen2:
    st.write("") # Spacer
    if st.button("🚀 Generate Draf Sekarang"):
        if topik and nama_user:
            with st.spinner(f"Menyusun {bab_pilihan} dengan referensi riil..."):
                thn = 2026
                rentang = f"{thn-3} s/d {thn}"
                p_lama = st.session_state['pustaka_koleksi']
                
                # --- LOGIKA PROMPT DINAMIS & RIIL ---
                if "Bab 1" in bab_pilihan:
                    instruksi = f"Buat Latar Belakang Piramida Terbalik (Nasional -> {kota} -> {lokasi}). Gunakan data fenomena riil tahun {rentang}."
                elif "Bab 2" in bab_pilihan:
                    instruksi = f"BEDAH JUDUL '{topik}' per variabel. Berikan Landasan Teori mendalam tiap variabel (Definisi ahli RIIL, Indikator, Faktor). Tambahkan penelitian terdahulu & kerangka berpikir. WAJIB kutipan tahun {rentang}."
                elif "Surat" in bab_pilihan:
                    instruksi = f"Buatkan surat izin penelitian formal untuk {nama_user} lokasi {lokasi}."
                else:
                    instruksi = f"Susun {bab_pilihan} untuk lokasi {lokasi} dengan standar akademik tinggi tahun {rentang}."

                prompt = f"""
                Bertindaklah sebagai Dosen Pembimbing. Buatkan draf {bab_pilihan} skripsi {metode} judul '{topik}'.
                ATURAN WAJIB:
                1. {instruksi}
                2. Gunakan Nama Ahli RIIL (Contoh: Sugiyono, Kotler, Arikunto, Robbins, dll).
                3. Gunakan judul jurnal yang umum dan nyata di Indonesia/Internasional.
                4. Referensi WAJIB antara {rentang}.
                5. Sertakan referensi lama ini jika relevan: {p_lama}.
                6. Gunakan Sitasi APA 7th Edition dan akhiri dengan DAFTAR PUSTAKA lengkap.
                """
                
                try:
                    res = model.generate_content(prompt).text
                    st.session_state['db'][bab_pilihan] = res
                    if "DAFTAR PUSTAKA" in res.upper():
                        st.session_state['pustaka_koleksi'] += "\n" + res.upper().split("DAFTAR PUSTAKA")[-1]
                    st.rerun()
                except Exception as e: st.error(f"Gagal: {e}")
        else: st.warning("Nama (di sidebar) dan Judul wajib diisi!")

st.divider()

# --- 7. MANAJEMEN DOKUMEN (BOX SYSTEM) ---
st.subheader("📁 Koleksi Dokumen Pengerjaan")
if not st.session_state['db']:
    st.info("Belum ada dokumen. Silakan isi data dan klik Generate.")
else:
    for bab, isi in st.session_state['db'].items():
        with st.container(border=True):
            col_h1, col_h2 = st.columns([5, 1])
            with col_h1:
                st.markdown(f"### 📄 {bab}")
            with col_h2:
                if st.button("🗑️ Hapus", key=f"del_{bab}"):
                    del st.session_state['db'][bab]
                    st.rerun()
            
            # Preview Ringkas
            st.markdown(isi[:400] + "..." if len(isi) > 400 else isi)
            
            with st.expander("Buka Teks Lengkap & Download"):
                st.markdown(isi)
                st.divider()
                
                # Logika Lisensi Model 6.4 (Nempel di bawah teks)
                if user_license == generate_license_logic(nama_user):
                    st.success("✅ Lisensi Aktif - Dokumen siap diunduh.")
                    doc = Document()
                    doc.add_heading(bab, 0)
                    doc.add_paragraph(f"Judul: {topik}\nOleh: {nama_user}\n\n")
                    doc.add_paragraph(isi)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button(f"📥 Download {bab} (Word)", data=bio.getvalue(), file_name=f"{bab}.docx", key=f"dl_{bab}")
                else:
                    st.warning("⚠️ Masukkan lisensi di sidebar untuk membuka tombol download.")
