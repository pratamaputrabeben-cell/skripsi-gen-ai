# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

SkripsiGen Pro is a single-page Streamlit app (Indonesian-language UI) that uses Google's Gemini API to draft undergraduate thesis ("skripsi") chapters, then exports them as formatted Word documents. There is no backend service, database, or test suite — the entire application lives in `streamlit_app.py`, and Streamlit's `session_state` is the only persistence layer (in-memory, per-session, lost on refresh).

## Commands

```bash
pip install -r requirements.txt   # install dependencies
streamlit run streamlit_app.py    # run the app locally (http://localhost:8501)
```

There are no lint, type-check, build, or test commands configured in this repo.

### Secrets

The app reads API keys via `st.secrets`, not environment variables. For local runs, create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEYS = ["key1", "key2"]
# or a single key:
# GEMINI_API_KEY = "key1"
```

`ALL_KEYS` falls back through `GEMINI_API_KEYS` → `GEMINI_API_KEY` → `""`. A random key from the list is chosen on each `inisialisasi_ai()` call, which is a simple form of key rotation/rate-limit spreading across multiple Gemini API keys.

## Architecture (`streamlit_app.py`)

The file is organized into four numbered sections (search for the `# --- N.` comment markers):

1. **Engine config (`inisialisasi_ai`)** — picks a random API key, configures `google.generativeai`, and probes `genai.list_models()` for an available model, preferring `gemini-2.5-flash` then `gemini-1.5-pro`, falling back to the first available model, then to a hardcoded `gemini-1.5-flash` on any exception. Model availability is re-resolved on every generation call rather than cached.

2. **Text cleanup (`bersihkan_dan_urutkan`)** — strips conversational AI preamble (e.g. "Tentu", "Berikut", "Ini adalah") and markdown artifacts from Gemini's raw output, then splits out and alphabetically sorts the "DAFTAR PUSTAKA" (bibliography) section from the main body. Returns `(konten_utama, pustaka_clean)`.

3. **Word export (`buat_dokumen_rapi`)** — builds a `python-docx` `Document` per academic formatting rules: 4-3-3-3 cm margins, Times New Roman 12pt, 1.5 line spacing, justified body text. It auto-detects markdown-table-like content (pipe-delimited lines containing "No") and converts it into a real Word table with fixed questionnaire columns (`No, Pernyataan, SS, S, N, TS, STS`); otherwise it renders numbered-heading paragraphs (e.g. `1.2.3 ...`) as bold with indentation proportional to heading depth. The bibliography, if present, is appended on a new page with hanging indents.

4. **Streamlit UI** — a sidebar (student name, PRO license key input/generator, reset button) and a main panel (thesis metadata inputs, chapter selector, generate/revise buttons, and per-chapter draft preview/download). Generated content per chapter is cached in `st.session_state['db']`, keyed by chapter label (e.g. `"Bab 1"`).

### Generation flow

`jalankan_proses()` is the single entry point for both initial generation and revision:
- Requires `topik` (title) and `nama_user` (student name) to be set.
- Builds a prompt combining a fixed "GLOBAL MANTRA" instruction block (forces markdown tables for instruments/classifications/statistics, forces APA 7th references from 2018–2026) with the chapter name, method (`Kuantitatif`/`Kualitatif`/`R&D`), location, city, and any lecturer revision notes (`catatan_dosen`).
- Calls `model.generate_content(prompt)` and stores `res.text` in `st.session_state['db'][bab_aktif]`, then `st.rerun()`.
- All exceptions from generation are swallowed into a single generic `st.error("Server sibuk, klik sekali lagi!")` — there is no granular error handling or logging.

### Licensing gate

`gen_lic(nama)` derives a deterministic license code from the student's first name and the current date (`PRO-{FIRSTNAME}-{ddmm}-SKR`). Chapters "Bab 1" and "Bab 2" are always downloadable (`is_trial`); all other chapters/appendices require the user-entered license key to match `gen_lic(nama_user)` before the Word download button appears. The "OWNER PANEL" expander lets an admin (gated by a hardcoded password) generate a license for a given buyer name. This is a lightweight, non-cryptographic gate — the license is trivially derivable from public info (name + date), not a security boundary.

## Conventions

- UI strings, variable/function names, and prompt text are in Indonesian (Bahasa Indonesia); keep new user-facing strings and academic-domain code consistent with this.
- Chapter identifiers are the literal Indonesian strings `"Bab 1"`..`"Bab 5"` and `"Lampiran: Surat Izin, Kuesioner & Kisi-kisi"` — used both as UI labels and as dict keys into `st.session_state['db']`.
- Broad `except:` blocks are used deliberately in a few places (model init fallback, generation error) to keep the single-user Streamlit UI from crashing; follow the existing pattern rather than introducing new failure modes that break the page.
