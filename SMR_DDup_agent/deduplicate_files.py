import re
import difflib
import os

def normalize_text(text):
    if not text:
        return ""
    # Remove non-alphanumeric characters and lowercase
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

def title_similarity(a, b):
    if not a or not b: return 0
    # Quick length check
    if abs(len(a) - len(b)) > max(len(a), len(b)) * 0.2:
        return 0
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

class Record:
    def __init__(self, source_file, original_text, pmid=None, doi=None, title=None, authors=None, year=None):
        self.source_file = source_file
        self.original_text = original_text
        self.pmid = pmid
        self.doi = doi.lower() if doi else None
        self.title = title.strip() if title else ""
        self.normalized_title = normalize_text(self.title)
        self.authors = authors # List of strings
        self.year = str(year) if year else None

    def is_duplicate_of(self, other):
        # 1. DOI Match
        if self.doi and other.doi and self.doi == other.doi:
            return True
        
        # 2. PMID Match (if both are PubMed)
        if self.pmid and other.pmid and self.pmid == other.pmid:
            return True

        # 3. Exact Normalized Title Match
        if self.normalized_title and other.normalized_title and self.normalized_title == other.normalized_title:
            return True

        # 4. Title Similarity (95%+) - only run if length is similar
        if abs(len(self.title) - len(other.title)) < 20: 
            sim = title_similarity(self.title, other.title)
            if sim >= 0.95:
                return True
            if sim >= 0.90 and self.year and other.year and self.year == other.year:
                return True
        
    def is_duplicate_of(self, other):
        # 1. DOI Match
        if self.doi and other.doi and self.doi == other.doi:
            return True
        
        # 2. PMID Match (if both are PubMed)
        if self.pmid and other.pmid and self.pmid == other.pmid:
            return True

        # 3. Exact Normalized Title Match
        if self.normalized_title and other.normalized_title and self.normalized_title == other.normalized_title:
            return True

        # 4. Title Similarity (95%+) - only run if length is similar
        if abs(len(self.title) - len(other.title)) < 20: 
            sim = title_similarity(self.title, other.title)
            if sim >= 0.95:
                return True
            if sim >= 0.90 and self.year and other.year and self.year == other.year:
                return True
        
        return False

def parse_pubmed(filename):
    records = []
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = re.split(r'\n(?=PMID- )', content)
    for block in blocks:
        if not block.strip(): continue
        
        pmid = re.search(r'^PMID- (.*)', block, re.M)
        doi = re.search(r'^LID - (.*) \[doi\]', block, re.M) or re.search(r'^AID - (.*) \[doi\]', block, re.M)
        title = re.search(r'^TI  - (.*?)(?=\n[A-Z]{2,4} - |\n\n|$)', block, re.S | re.M)
        year = re.search(r'^DP  - (\d{4})', block, re.M)
        
        # Extract authors
        authors = re.findall(r'^FAU - (.*)', block, re.M)
        
        t_str = ""
        if title:
            t_str = " ".join(line.strip() for line in title.group(1).split('\n'))

        records.append(Record(
            source_file=filename,
            original_text=block,
            pmid=pmid.group(1).strip() if pmid else None,
            doi=doi.group(1).strip() if doi else None,
            title=t_str,
            authors=authors,
            year=year.group(1).strip() if year else None
        ))
    return records

def parse_bib(filename):
    records = []
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Improved regex for BibTeX entries
    entries = re.findall(r'@\w+\s*\{.*?\n\}', content, re.S)
    for entry in entries:
        title_match = re.search(r'title\s*=\s*[\{"](.*?)[}\"],', entry, re.S | re.I) or \
                      re.search(r'title\s*=\s*\{(.*)\}', entry, re.S | re.I)
        doi_match = re.search(r'doi\s*=\s*[\{"](.*?)[}\"]', entry, re.S | re.I)
        year_match = re.search(r'year\s*=\s*[\{"]?(\d{4})[\"\}]?', entry, re.S | re.I)
        author_match = re.search(r'author\s*=\s*[\{"](.*?)[}\"]', entry, re.S | re.I)
        
        t_str = ""
        if title_match:
            t_str = " ".join(line.strip() for line in title_match.group(1).split('\n'))
            t_str = re.sub(r'[\{\}]', '', t_str)

        records.append(Record(
            source_file=filename,
            original_text=entry,
            doi=doi_match.group(1).strip() if doi_match else None,
            title=t_str,
            authors=author_match.group(1).split(' and ') if author_match else [],
            year=year_match.group(1).strip() if year_match else None
        ))
    return records

def parse_ris(filename):
    records = []
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by ER  - (End of Record)
    entries = re.split(r'\nER\s+-', content)
    for entry in entries:
        if not entry.strip(): continue
        
        # Extract title (TI or T1)
        title_match = re.search(r'^(?:TI|T1)\s+-\s+(.*)', entry, re.M | re.I)
        # Extract DOI
        doi_match = re.search(r'^DO\s+-\s+(.*)', entry, re.M | re.I)
        # Extract Year
        year_match = re.search(r'^PY\s+-\s+(\d{4})', entry, re.M | re.I)
        # Extract Authors (multiple AU lines)
        authors = re.findall(r'^AU\s+-\s+(.*)', entry, re.M | re.I)
        
        t_str = title_match.group(1).strip() if title_match else ""

        records.append(Record(
            source_file=filename,
            original_text=entry + "\nER  -",
            doi=doi_match.group(1).strip() if doi_match else None,
            title=t_str,
            authors=authors,
            year=year_match.group(1).strip() if year_match else None
        ))
    return records

def process_file(records, label, master_seen_dois, master_seen_titles, master_unique_list):
    print(f"Deduplicating {label}...")
    local_unique = []
    for r in records:
        # Check against master first
        if r.doi and r.doi in master_seen_dois:
            continue
        if r.normalized_title and r.normalized_title in master_seen_titles:
            continue
            
        is_dup = False
        for u in master_unique_list:
            if r.is_duplicate_of(u):
                is_dup = True
                break
        
        if is_dup: continue
        
        # Check against current local unique (intra-file)
        for lu in local_unique:
            if r.is_duplicate_of(lu):
                is_dup = True
                break
        
        if not is_dup:
            local_unique.append(r)
            master_unique_list.append(r)
            if r.doi: master_seen_dois.add(r.doi)
            if r.normalized_title: master_seen_titles.add(r.normalized_title)
            
    return local_unique

def save_pubmed(records, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(r.original_text.strip() for r in records))

def save_bib(records, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(r.original_text.strip() for r in records))

def save_ris(records, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(r.original_text.strip() for r in records))

# Configuration: Update these filenames to match your input files
pubmed_path = 'pubmed_input.txt'
wos_path = 'wos_input.bib'
scopus_path = 'scopus_input.bib'
ris_path = 'articles.ris'

def main():
    all_recs_to_process = []
    
    # Check and parse PubMed
    if os.path.exists(pubmed_path):
        print(f"Found PubMed: {pubmed_path}")
        all_recs_to_process.append((parse_pubmed(pubmed_path), "PubMed", "pubmed_deduplicated.txt", save_pubmed))
    
    # Check and parse WoS
    if os.path.exists(wos_path):
        print(f"Found WoS: {wos_path}")
        all_recs_to_process.append((parse_bib(wos_path), "WoS", "wos_deduplicated.bib", save_bib))
        
    # Check and parse Scopus
    if os.path.exists(scopus_path):
        print(f"Found Scopus: {scopus_path}")
        all_recs_to_process.append((parse_bib(scopus_path), "Scopus", "scopus_deduplicated.bib", save_bib))

    # Check and parse RIS
    if os.path.exists(ris_path):
        print(f"Found RIS: {ris_path}")
        all_recs_to_process.append((parse_ris(ris_path), "RIS", "ris_deduplicated.ris", save_ris))

    if not all_recs_to_process:
        print("No input files found. Please ensure your files are named correctly:")
        print(f" - {pubmed_path}")
        print(f" - {wos_path}")
        print(f" - {scopus_path}")
        print(f" - {ris_path}")
        return

    master_seen_dois = set()
    master_seen_titles = set()
    master_unique_list = []

    final_results = []
    for recs, label, out_name, save_func in all_recs_to_process:
        final_recs = process_file(recs, label, master_seen_dois, master_seen_titles, master_unique_list)
        final_results.append((final_recs, out_name, save_func))

    print(f"\nFinal counts (Deduplicated):")
    for recs, out_name, _ in final_results:
        print(f"{out_name}: {len(recs)}")

    # Save the files
    for recs, out_name, save_func in final_results:
        save_func(recs, out_name)

    print("\nFiles saved successfully.")

if __name__ == "__main__":
    main()
