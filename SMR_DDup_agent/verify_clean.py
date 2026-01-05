import re

def count_pubmed(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        return len(re.findall(r'^PMID- ', content, re.MULTILINE))

def count_bib(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        return len(re.findall(r'@(?:article|ARTICLE|inproceedings|BOOK|book|phdthesis|mastersthesis|techreport|misc)\{', content))

files = {
    'PubMed Clean': 'pubmed_deduplicated.txt',
    'Scopus Clean': 'scopus_deduplicated.bib',
    'WoS Clean': 'wos_deduplicated.bib'
}

for label, path in files.items():
    if label == 'PubMed Clean':
        count = count_pubmed(path)
    else:
        count = count_bib(path)
    print(f"{label}: {count}")
