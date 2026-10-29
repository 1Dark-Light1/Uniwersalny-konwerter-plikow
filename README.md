# Uniwersalny konwerter plików

Prosta aplikacja desktopowa napisana w Pythonie z wykorzystaniem biblioteki Tkinter. Umożliwia konwersję plików między różnymi formatami.

## Funkcje

Aplikacja obsługuje następujące konwersje:

- CSV → JSON
- JSON → CSV
- TXT → DOCX
- TXT → PDF
- DOCX → TXT
- DOCX → PDF
- PDF → DOCX

## Technologie

- Python
- Tkinter
- python-docx
- ReportLab
- PyPDF

## Instalacja

1. Sklonuj repozytorium.
2. Zainstaluj wymagane biblioteki:

```bash
pip install -r requirements.txt
```

3. Uruchom aplikację:

```bash
python app.py
```

## Testy

Aby uruchomić testy, wpisz:

```bash
python -m unittest discover -s FileFlow/tests -v
```

## Autor

Projekt edukacyjny — Uniwersalny konwerter plików.
