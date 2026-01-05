# Automates_agents_for_Systematic_reviews
Accelerate your systematic reviews with AI. This collection of agents automates the transition from raw database exports (PubMed, Scopus, WoS) to a structured evidence table using keyword-based screening and Gemini-powered data extraction.

This repository contains a suite of automated agents designed to streamline the **Systematic Mixed Review (SMR)** workflow. These tools handle deduplication, screening, and data extraction, transforming raw database exports into a structured evidence table.

## Workflow Overview

1.  **Deduplication** (`SMR_DDup_agent`): 
    - Consolidate results from PubMed, Scopus, Web of Science, and others.
    - Remove duplicates using DOI, PMID, and fuzzy title matching.
    
2.  **Screening** (`SMR_Screening_Agent`):
    - Automatically screen titles and abstracts against inclusion/exclusion criteria.
    - Export a decision list with reasoning for each article.

3.  **Data Extraction** (`SMR_Extraction_AGENT`):
    - Use AI (Gemini) to read included PDF articles.
    - Extract study characteristics and outcomes directly into an Excel table.

## Directory Structure
- `SMR_DDup_agent/`: Tools for managing bibliographic duplicates.
- `SMR_Screening_Agent/`: Automated title/abstract screening logic.
- `SMR_Extraction_AGENT/`: PDF-to-Excel data extraction using LLMs.

## Requirements
Each sub-folder contains its own specific instructions and dependencies. Generally, you will need:
- Python 3.8+
- Playwright (for extraction)
- Pandas & Openpyxl

For detailed instructions on running each component, please refer to the `README.md` file inside the respective folder.

---
*Developed for automating high-quality academic synthesis.*
