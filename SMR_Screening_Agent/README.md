# SMR Screening Agent

This agent automates the title and abstract screening process for academic articles, specifically tailored for Systematic Mixed Reviews (SMR). It uses keyword-based logic to include or exclude articles based on predefined criteria.

## Features
- **Automated Keywords**: Searches for disease-specific keywords (e.g., Giant Cell Tumor), anatomical locations (e.g., Cervical Spine), and study types.
- **Exclusion Logic**: Automatically filters out systematic reviews, meta-analyses, and irrelevant diagnoses.
- **Reasoning**: Provides a clear reason for every exclusion, helping in the PRISMA workflow.

## How to Use

### 1. Prepare Your Input Records
Replace the `articles.bib` file in this folder with your own BibTeX file exported from databases like PubMed, Scopus, or WoS.

### 2. Parse the BibTeX File
Run the parser to convert the `.bib` file into a processable JSON format:
```powershell
python parse_bib.py
```
This will create `parsed_articles.json`.

### 3. Run the Screening
Execute the screening script:
```powershell
python screen_articles.py
```
This will analyze the articles based on the criteria defined in the script.

### 4. Get the Output
The results will be saved in `screening_results.csv`, which includes:
- **Key**: The unique identifier from the BibTeX.
- **Title**: The article title.
- **Decision**: `Include` or `Exclude`.
- **Reason**: The specific reasoning for the decision.

## Customization
You can modify the inclusion/exclusion keywords (such as `gct_keywords` or `cervical_keywords`) directly in `screen_articles.py` to suit your specific research topic.
