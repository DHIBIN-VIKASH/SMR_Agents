# SMR Data Extraction Agent

This agent automates the extraction of study characteristics and outcomes from PDF articles using the Gemini AI through browser automation (Playwright). It is designed to populate a systematic review table automatically.

## Features
- **PDF Data Extraction**: Automatically uploads PDF files to Gemini and prompts for structured data extraction.
- **Incremental Progress**: Saves results after each file, allowing the process to be resumed if interrupted.
- **Structured Output**: Generates an Excel file with predefined columns for study details (age, sex, BMI, etc.) and outcomes (SSI, mortality, readmission, etc.).
- **Resident Browser Profile**: Uses a local Chrome/Edge profile to stay logged into Google Gemini.

## Prerequisites
- Python 3.8+
- Playwright (`pip install playwright`)
- Pandas & Openpyxl (`pip install pandas openpyxl`)
- A Google account (logged in to Gemini)

## How to Use

### 1. Setup Your Files
- Place your PDF articles in the `Articles` folder.
- (Optional) Refer to `Study Characteristics Table.docx` for the list of fields being extracted.

### 2. Browser Authentication
The script uses a persistent browser profile. You only need to log in once:
1. Run the script: `python gemini_extractor.py --browser chrome`
2. If it's your first time, the browser will wait for you to log in to your Google account on Gemini.
3. Once logged in, the script will remember your session for future runs.

### 3. Run the Extraction
Start the automation:
```powershell
python gemini_extractor.py
```
Options:
- `--limit N`: Only process the first N files.
- `--browser msedge`: Use Microsoft Edge instead of Chrome.

### 4. Get the Output
The results will be incrementally saved to `extracted_studies.xlsx` in this folder. Each row represents one study extracted from a PDF.

## Troubleshooting
- **Login Issues**: If the script is failing to find the "Plus" button, ensure you are fully logged into Gemini in the browser window that opens.
- **Selectors**: Web UI changes may break selectors. Check `gemini_extractor.py` and update the `plus_button` or `text_area` selectors if needed.
- **Rate Limits**: If Gemini stops responding, the script might need longer sleep times between files.
