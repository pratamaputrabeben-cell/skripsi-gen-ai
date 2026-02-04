def dapatkan_prompt_fenomena(tipe, t, n, m, lok, kota, p_lama, c=""):
    instruksi_pustaka = f"Sertakan daftar pustaka lama ini: {p_lama}" if p_lama else ""
    
    if "Bab 1" in tipe:
        instruksi_khusus = f"Susun Latar Belakang Piramida Terbalik dari Nasional ke lokasi {lok}."
    elif "Bab 2" in tipe:
        instruksi_khusus = f"""
        TUGAS KHUSUS BAB 2 (TINJAUAN PUSTAKA):
        1. Identifikasi kata kunci/variabel utama dari judul '{t}'.
        2. Buatkan LANDASAN TEORI untuk MASING-MASING kata kunci tersebut secara terpisah (Sub-bab 2.1, 2.2, dst).
        3. Untuk setiap variabel, wajib ada: Definisi menurut para ahli, Indikator-indikatornya, dan Faktor yang mempengaruhinya.
        4. Tambahkan Penelitian Terdahulu dalam bentuk poin/narasi.
        5. Buat Kerangka Berpikir dan Hipotesis (jika {m} adalah Kuantitatif).
        """
    else:
        instruksi_khusus = f"Kerjakan {tipe} dengan fokus pada lokasi {lok}."

    if c:
        return f"Revisi {tipe} skripsi {m} judul {t} di {lok} berdasarkan: {c}. {instruksi_pustaka}. Gunakan kutipan APA 7th."
    else:
        return f"Buatkan draf {tipe} skripsi {m} judul {t}. {instruksi_khusus}. {instruksi_pustaka}. WAJIB gunakan kutipan ahli dan Daftar Pustaka APA 7th."
