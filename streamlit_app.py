import streamlit as st
import google.generativeai as genai
# ... (import lainnya tetap sama) ...

def inisialisasi_ai():
    # Ambil semua kunci dari secrets
    keys = st.secrets.get("GEMINI_API_KEYS", [])
    if not keys:
        # Cadangan jika Bos lupa ganti nama variabel
        keys = [st.secrets.get("GEMINI_API_KEY", "")]
    
    # Pilih kunci secara acak setiap kali dipanggil
    key_aktif = random.choice(keys)
    genai.configure(api_key=key_aktif)
    return genai.GenerativeModel('gemini-1.5-flash')

# --- FUNGSI PROSES DENGAN AUTO-RETRY ---
def eksekusi_ai_kebal(prompt):
    max_retries = 3  # Coba sampai 3 kali otomatis
    for i in range(max_retries):
        try:
            model = inisialisasi_ai()
            res = model.generate_content(prompt)
            return res.text
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(2)  # Tunggu 2 detik sebelum coba lagi
                continue
            else:
                raise e # Menyerah setelah 3x gagal

# ... (kode lainnya tetap pakai v8.60) ...

if st.button("🚀 Proses & Kalibrasi Sekarang"):
    if topik and nama_user:
        with st.spinner("Sedang memproses (Percobaan otomatis aktif)..."):
            try:
                # Memakai fungsi kebal yang baru
                konten_lama = st.session_state['db'].get('File_Upload', "Tidak ada.")
                prmt = f"Tugas: Susun {pil_bab}. Judul: {topik}. Lokasi: {lokasi}. Metode: {metode}. Referensi: 2023-2026. File asal: {konten_lama}"
                
                hasil_teks = eksekusi_ai_kebal(prmt) # Panggil fungsi sakti
                
                st.session_state['db'][pil_bab] = hasil_teks
                st.rerun()
            except:
                st.error("Server Google benar-benar penuh. Tunggu 30 detik lalu coba lagi ya Bos!")
