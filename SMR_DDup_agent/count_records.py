import re
import os

def count_pubmed(filename):
    if not os.path.exists(filename): return 0
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        return len(re.findall(r'^PMID- ', content, re.MULTILINE))

def count_bib(filename):
    if not os.path.exists(filename): return 0
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        return len(re.findall(r'@(?:article|ARTICLE|inproceedings|BOOK|book|phdthesis|mastersthesis|techreport|misc)\{', content))

def count_ris(filename):
    if not os.path.exists(filename): return 0
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        return len(re.findall(r'\nER\s+-', content))

# Configuration: Update these to match your filenames
pubmed_file = 'pubmed_input.txt'
wos_file = 'wos_input.bib'
scopus_file = 'scopus_input.bib'
ris_file = 'articles.ris'

counts = {}
if os.path.exists(pubmed_file): counts['PubMed'] = count_pubmed(pubmed_file)
if os.path.exists(wos_file): counts['Web of Science'] = count_bib(wos_file)
if os.path.exists(scopus_file): counts['Scopus'] = count_bib(scopus_file)
if os.path.exists(ris_file): counts['RIS'] = count_ris(ris_file)

if not counts:
    print("No input files found to count.")
else:
    for label, count in counts.items():
        print(f"{label}: {count} records")
