# FB-OSINT Investigator Pro

**Coded by mr sabaz ali khan**

A privacy-conscious Facebook OSINT case-management toolkit for Windows 10/11 and Kali Linux. It organizes user-supplied URLs, notes, and evidence metadata. It does **not** scrape Facebook, bypass access controls, collect private data, automate logins, or claim that a profile/page is genuine.

## Features
- CLI for creating cases, adding public URLs and notes, listing cases, and exporting reports.
- Optional Streamlit dashboard for case management.
- URL safety validation (HTTPS and Facebook-related hosts only).
- JSON and CSV reports; local SQLite database.
- Evidence SHA-256 hashes for files you explicitly add.
- Tests for URL validation, case creation, and report export.
- Local-first storage; no network calls to Facebook.

## Ethical use
Use only information you are authorized to collect and information publicly accessible under applicable law and platform rules. Do not use this tool to identify private individuals, infer sensitive attributes, bypass privacy settings, or harass people. A URL or user note is unverified evidence, not proof. Keep case data secure and delete it when no longer needed.

## Project structure
```text
fb_osint_investigator_pro/
├── app.py
├── cli.py
├── fbosint/
│   ├── __init__.py
│   ├── core.py
│   ├── storage.py
│   └── reports.py
├── tests/
│   └── test_core.py
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Install — Windows
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

## Install — Kali Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## CLI usage
```bash
python cli.py init --case "Example investigation" --owner "Authorized analyst"
python cli.py add-url --case-id 1 --url "https://www.facebook.com/examplepage" --label "Public page"
python cli.py add-note --case-id 1 --note "Observed public information; needs independent verification."
python cli.py add-evidence --case-id 1 --path ./evidence/screenshot.png --description "User-provided screenshot"
python cli.py list
python cli.py export --case-id 1 --format json
python cli.py export --case-id 1 --format csv
```
Database and exports are stored in `data/` by default. Set `FBOSINT_HOME` to choose another directory.

## Dashboard
```bash
streamlit run app.py
```
Open the local URL printed by Streamlit. The dashboard is intended for local use. Do not expose it to the public internet.

## Tests
```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

## Limitations
This is a case-management and evidence-reporting toolkit, not an automated Facebook data extractor. It does not verify ownership, profile authenticity, account relationships, location, or the truth of supplied evidence. Facebook's supported APIs and permissions should be used for any platform-connected workflows.
