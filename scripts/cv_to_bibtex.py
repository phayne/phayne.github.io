#!/usr/bin/env python3
'''
Script to extract publications from a LaTeX CV file and update
the BibTeX file for a Jekyll website using the al-folio theme.
'''

import os
import re
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from datetime import datetime

# Configuration
CV_PATH = "../assets/files/Hayne-CV/main.tex"
BIBTEX_PATH = "../_bibliography/papers.bib"

def extract_publications_from_cv():
    """Extract publication entries from the CV LaTeX file"""
    print(f"Reading CV file from {CV_PATH}...")
    
    try:
        with open(CV_PATH, 'r', encoding='utf-8') as f:
            cv_content = f.read()
    except Exception as e:
        print(f"Error reading CV file: {e}")
        return []
    
    # Find the publications section
    pubs_pattern = r"\\hrulefill\s*\\vspace\{0\.1in\}\\\\\\{\\large\\textcolor\{darkgray\}\{Paul O\. Hayne: Refereed Journal Articles\}\}(.*?)\\noindent"
    pubs_match = re.search(pubs_pattern, cv_content, re.DOTALL)
    
    if not pubs_match:
        print("Publications section not found in CV. Searching for alternative section markers...")
        # Try alternative markers
        alt_pattern = r"\\noindent\s*\\begin\{longtable\}.*?\\textcolor\{darkgray\}\{(2\d{3})\}(.*?)\\end\{longtable\}"
        pub_years = re.findall(alt_pattern, cv_content, re.DOTALL)
        
        if not pub_years:
            print("Could not find publications section in CV.")
            return []
        
        print(f"Found publications from years: {[year for year, _ in pub_years]}")
        
        # Extract publications by year
        all_pubs = []
        for year, year_content in pub_years:
            # Extract individual publications using item pattern
            pub_pattern = r"\\item\{\\small(.*?)(?=\\item\{|$)"
            year_pubs = re.findall(pub_pattern, year_content, re.DOTALL)
            
            print(f"Found {len(year_pubs)} publications for year {year}")
            for pub in year_pubs:
                all_pubs.append((year, pub.strip()))
        
        return all_pubs
    
    pubs_content = pubs_match.group(1)
    
    # Extract publications by year
    year_pattern = r"\\noindent\\textcolor\{darkgray\}\{(\d{4})\}(.*?)(?=\\noindent\\textcolor\{darkgray\}\{|\Z)"
    pub_years = re.findall(year_pattern, pubs_content, re.DOTALL)
    
    all_pubs = []
    for year, year_content in pub_years:
        # Extract individual publications using item pattern
        pub_pattern = r"\\item\{\\small(.*?)(?=\\item\{|$)"
        year_pubs = re.findall(pub_pattern, year_content, re.DOTALL)
        
        print(f"Found {len(year_pubs)} publications for year {year}")
        for pub in year_pubs:
            all_pubs.append((year, pub.strip()))
    
    print(f"Total publications found: {len(all_pubs)}")
    return all_pubs

def parse_publication(year, pub_text):
    """Parse a publication entry from CV to extract components"""
    # Clean up LaTeX commands and symbols
    pub_text = pub_text.replace('\\textcolor{darkred}{$^*$(G)', '')
    pub_text = pub_text.replace('\\textcolor{darkred}{$^*$(U)', '')
    pub_text = pub_text.replace('\\textcolor{blue}{$^*$(P)', '')
    pub_text = pub_text.replace('}', '')
    pub_text = pub_text.replace('\\textbf{', '')
    pub_text = pub_text.replace('\\textit{', '')
    pub_text = pub_text.replace('\\href{', '')
    pub_text = pub_text.replace('}{', ' ')
    pub_text = re.sub(r'\\\w+', ' ', pub_text)  # Remove other LaTeX commands
    pub_text = re.sub(r'\s+', ' ', pub_text)    # Normalize whitespace
    
    # Extract authors - usually everything before the year in parentheses
    authors_match = re.search(r'^(.*?)\((\d{4})\)', pub_text)
    if not authors_match:
        return None
    
    authors = authors_match.group(1).strip()
    pub_year = authors_match.group(2)
    
    # Extract title - usually between year and journal
    rest = pub_text[authors_match.end():].strip()
    title_journal_match = re.search(r'(.*?),\s*(.*?)(?:,|$)', rest)
    
    if not title_journal_match:
        title = rest
        journal = "Unknown Journal"
    else:
        title = title_journal_match.group(1).strip()
        journal = title_journal_match.group(2).strip()
    
    # Extract volume, number, pages
    vol_pages_match = re.search(r'(\d+)(?:\((\d+)\))?,\s*(?:pp\.\s*)?(\d+)--(\d+)', rest)
    volume = ""
    number = ""
    pages = ""
    
    if vol_pages_match:
        volume = vol_pages_match.group(1)
        number = vol_pages_match.group(2) if vol_pages_match.group(2) else ""
        pages = f"{vol_pages_match.group(3)}--{vol_pages_match.group(4)}"
    
    # Create citation key from first author's last name and year
    author_parts = authors.split(',')[0].strip().split()
    if author_parts:
        last_name = author_parts[-1].lower()
        key = f"{last_name}{pub_year}"
    else:
        key = f"unknown{pub_year}"
    
    # Format author names for BibTeX
    authors = authors.replace(' & ', ' and ')
    
    return {
        'key': key,
        'title': title,
        'authors': authors,
        'journal': journal,
        'year': pub_year,
        'volume': volume,
        'number': number,
        'pages': pages
    }

def generate_bibtex_entries(publications):
    """Generate BibTeX entries from parsed publications"""
    print("Generating BibTeX entries...")
    bibtex_entries = []
    
    for i, (year, pub_text) in enumerate(publications):
        pub_data = parse_publication(year, pub_text)
        
        if not pub_data:
            print(f"Failed to parse publication {i+1}")
            continue
        
        # Create unique key if duplicates exist
        base_key = pub_data['key']
        key = base_key
        suffix_idx = 0
        while any(entry.get('ID') == key for entry in bibtex_entries):
            suffix_idx += 1
            key = f"{base_key}{chr(96 + suffix_idx)}"  # a, b, c, ...
        
        # Create the BibTeX entry
        entry = {
            'ID': key,
            'ENTRYTYPE': 'article',
            'title': f"{{{pub_data['title']}}}",
            'author': pub_data['authors'],
            'journal': pub_data['journal'],
            'year': pub_data['year'],
        }
        
        # Add optional fields if available
        if pub_data['volume']:
            entry['volume'] = pub_data['volume']
        
        if pub_data['number']:
            entry['number'] = pub_data['number']
        
        if pub_data['pages']:
            entry['pages'] = pub_data['pages']
        
        bibtex_entries.append(entry)
    
    return bibtex_entries

def update_bibtex_file(bibtex_entries):
    """Update the BibTeX file with new entries, preserving existing links"""
    print("Updating BibTeX file...")
    existing_entries = {}
    
    # Read existing BibTeX file if it exists
    if os.path.exists(BIBTEX_PATH):
        with open(BIBTEX_PATH, 'r') as f:
            content = f.read()
            # Extract YAML front matter
            yaml_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
            yaml_header = yaml_match.group(0) if yaml_match else "---\n---\n\n"
            
            # Parse existing entries
            parser = BibTexParser()
            bib_database = bibtexparser.loads(content.replace(yaml_header, ""), parser)
            
            for entry in bib_database.entries:
                existing_entries[entry.get('ID')] = entry
    else:
        yaml_header = "---\n---\n\n"
    
    print(f"Found {len(existing_entries)} existing entries.")
    
    # Merge new entries with existing ones
    merged_entries = []
    new_count = 0
    updated_count = 0
    preserved_count = 0
    
    for entry in bibtex_entries:
        key = entry.get('ID')
        if key in existing_entries:
            # If this entry already exists, preserve any custom fields
            existing = existing_entries[key]
            
            # Preserve title with links from existing entry if it has links
            if '<a href=' in existing.get('title', ''):
                entry['title'] = existing['title']
            else:
                # Add links to title if we have a URL but the existing entry doesn't have links
                entry['title'] = f"{{<a href=\"\" target=\"\\_\">{entry['title'].strip('{}')}</a>}}"
            
            # Copy any additional fields from existing entry
            for field_key, value in existing.items():
                if field_key not in entry and field_key not in ['ID', 'ENTRYTYPE']:
                    entry[field_key] = value
            
            updated_count += 1
            del existing_entries[key]
        else:
            # For new entries, add placeholder link
            entry['title'] = f"{{<a href=\"\" target=\"\\_\">{entry['title'].strip('{}')}</a>}}"
            new_count += 1
        
        merged_entries.append(entry)
    
    # Add any remaining existing entries that weren't in the new entries
    for key, entry in existing_entries.items():
        merged_entries.append(entry)
        preserved_count += 1
    
    # Sort entries by year (descending)
    merged_entries.sort(key=lambda x: int(x.get('year', '0')), reverse=True)
    
    # Write the updated BibTeX file
    writer = BibTexWriter()
    writer.indent = '  '
    bib_database = bibtexparser.bibdatabase.BibDatabase()
    bib_database.entries = merged_entries
    
    with open(BIBTEX_PATH, 'w') as f:
        f.write(yaml_header)
        f.write(writer.write(bib_database))
    
    print(f"Successfully updated {BIBTEX_PATH} with {len(merged_entries)} publications:")
    print(f"  - {new_count} new entries added")
    print(f"  - {updated_count} existing entries updated")
    print(f"  - {preserved_count} existing entries preserved")

def main():
    try:
        # Extract publications from CV
        publications = extract_publications_from_cv()
        
        if not publications:
            print("No publications were extracted. Exiting.")
            return
        
        # Generate BibTeX entries
        bibtex_entries = generate_bibtex_entries(publications)
        
        if not bibtex_entries:
            print("No BibTeX entries generated. Exiting.")
            return
        
        # Update BibTeX file
        update_bibtex_file(bibtex_entries)
        
        print("Publication update completed successfully.")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()