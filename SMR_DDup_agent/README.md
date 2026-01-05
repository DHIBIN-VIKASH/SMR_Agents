# SMR Deduplication Agent

This agent automates the deduplication of bibliographic records from multiple academic databases (PubMed, Scopus, Web of Science, etc.). It uses a hierarchical matching logic (DOI, PMI, Exact Title, and Fuzzy Title Similarity) to identify and remove duplicates across different file formats.

## Features
- **Multi-format Support**: Handles `.txt` (PubMed), `.bib` (BibTeX), and `.ris` files.
- **Cross-Database Deduplication**: Removes duplicates not only within a single file but also across all provided search results.
- **Hierarchical Matching**: 
  1. DOI Match (Highest Priority)
  2. PMID Match
  3. Exact Title Match (Normalized)
  4. Fuzzy Title Similarity (95%+)

## How to Use

### 1. Prepare Your Input Files
Place your exported search results in this folder and name them as follows (or update the configuration in `deduplicate_files.py`):
- **PubMed**: `pubmed_input.txt`
- **Web of Science**: `wos_input.bib`
- **Scopus**: `scopus_input.bib`
- **General RIS**: `articles.ris`

### 2. Run the Program
Ensure you have Python installed. Run the deduplication script:
```powershell
python deduplicate_files.py
```

### 3. Get the Output
The program will generate deduplicated files for each input:
- `pubmed_deduplicated.txt`
- `wos_deduplicated.bib`
- `scopus_deduplicated.bib`
- `ris_deduplicated.ris`

## Troubleshooting
- If no files are found, verify that the filenames match the input names listed above.
- The script prioritizes files in the order: PubMed > Scopus > WoS > RIS. If a duplicate is found between PubMed and Scopus, the PubMed record is kept.
