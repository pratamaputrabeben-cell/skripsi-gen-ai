# --- UPDATE PROMPT LAMPIRAN DI DALAM KODE (v8.36) ---

if "Lampiran" in bab_yg_diproses:
    prompt = f"""
    Buatkan dokumen LAMPIRAN PENELITIAN SUPER LENGKAP untuk mahasiswa bernama {nama_user} 
    dengan judul '{topik}' di {lokasi}, {kota}.

    DOKUMEN WAJIB (Format Akademik Profesional):
    
    1. SURAT IZIN PENELITIAN & OBSERVASI AWAL
       - Ditujukan ke Kepala Sekolah {lokasi}.
       - Mencakup izin pengambilan data awal dan penelitian utama.
    
    2. KUESIONER DATA AWAL (PRA-RISET)
       - Instrumen identifikasi masalah pergaulan remaja di {lokasi}.
    
    3. KUESIONER PENELITIAN UTAMA (PST)
       - Bagian Pengetahuan (15-20 pernyataan Benar/Salah).
       - Bagian Sikap (Skala Likert: SS, S, TS, STS).
       - Bagian Tindakan (Skala Guttman: Ya/Tidak).
    
    4. KISI-KISI INSTRUMEN (INTEL PACK)
       - Tabel yang membedah Variabel -> Sub Variabel -> Indikator -> Nomor Soal.
       - Ini bukti bahwa kuesioner dibuat secara ilmiah, bukan asal tanya.
    
    5. LEMBAR VALIDASI AHLI (EXPERT JUDGEMENT)
       - Draft pernyataan untuk Dosen atau Ahli Kesehatan guna menyetujui kuesioner.
    
    6. LEMBAR PERSETUJUAN RESPONDEN (INFORMED CONSENT)
       - Dokumen etika penelitian sesuai standar kesehatan 2026.

    Gunakan bahasa yang sangat formal, rapi, dan sistematis.
    """
