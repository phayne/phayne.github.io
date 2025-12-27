#!/usr/bin/env python3
'''
Script to fetch publications from NASA ADS and update
the BibTeX file for a Jekyll website using the al-folio theme.

This script requires an ADS API key, which you can get by creating an account at:
https://ui.adsabs.harvard.edu/user/account/register
'''

import os
import re
import time
import json
import requests
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from datetime import datetime

# Configuration
AUTHOR_QUERIES = ["author:\"Hayne, P\"", "author:\"Hayne, Paul\"", "author:\"Hayne, Paul O\""]  # Multiple author name variants
ORCID = "0000-0003-4399-0449"  # Your ORCID if you have one (leave empty if not)
BIBTEX_PATH = "../_bibliography/papers.bib"
ADS_API_TOKEN = "RpjG7e1XAinDGLpWnnKWf5VBJIXdiGuY8c9OT017"  # Get your API key from https://ui.adsabs.harvard.edu/user/settings/token
ADS_API_URL = "https://api.adsabs.harvard.edu/v1/search/query"
MAX_PUBLICATIONS = 300  # Maximum number of publications to fetch
REFEREED_ONLY = True  # Set to True to only include peer-reviewed publications
FILTER_TYPES = ["article", "inbook", "inproceedings"]  # Types of publications to include
MIN_YEAR = 2003  # Minimum publication year to include (filter out publications before this year)

def get_ads_publications():
    """Fetch publications from ADS API"""
    print(f"Fetching publications for author from ADS using multiple name variants...")
    
    if not ADS_API_TOKEN:
        print("Error: ADS API token not set. Please get your API key from https://ui.adsabs.harvard.edu/user/settings/token")
        return []
    
    headers = {
        "Authorization": f"Bearer {ADS_API_TOKEN}",
        "Content-type": "application/json"
    }
    
    # Build the query
    query_parts = []
    
    # Use OR to combine multiple author name variants
    author_query = " OR ".join(AUTHOR_QUERIES)
    query_parts.append(f"({author_query})")
    
    # Use ORCID as an OR condition if provided
    if ORCID:
        query_parts.append(f"OR orcid:{ORCID}")
    
    if REFEREED_ONLY:
        query_parts.append("property:refereed")
    
    # Add year filter to exclude publications before MIN_YEAR
    query_parts.append(f"year:{MIN_YEAR}-")
    
    query = " ".join(query_parts)
    
    params = {
        "q": query,
        "fl": "bibcode,title,author,pub,volume,issue,page,year,doctype,identifier,doi,abstract",
        "rows": MAX_PUBLICATIONS,
        "sort": "date desc"
    }
    
    try:
        response = requests.get(ADS_API_URL, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        
        data = response.json()
        if 'response' not in data:
            print(f"Error: Unexpected response from ADS API: {data}")
            return []
        
        print(f"Found {data['response']['numFound']} publications in total")
        
        # Filter by publication type if needed
        publications = []
        for doc in data['response']['docs']:
            if not FILTER_TYPES or doc.get('doctype', '').lower() in FILTER_TYPES:
                publications.append(doc)
        
        print(f"Including {len(publications)} publications after filtering")
        return publications
    
    except Exception as e:
        print(f"Error fetching publications from ADS: {e}")
        return []

def get_bibtex_for_publications(publications):
    """Get BibTeX entries for a list of publications using the ADS API"""
    print("Fetching BibTeX entries from ADS...")
    
    if not publications:
        return []
    
    headers = {
        "Authorization": f"Bearer {ADS_API_TOKEN}",
        "Content-type": "application/json"
    }
    
    bibcodes = [pub['bibcode'] for pub in publications]
    bibtex_entries = []
    
    # Process in batches of 50 to avoid API limits
    batch_size = 50
    for i in range(0, len(bibcodes), batch_size):
        batch = bibcodes[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(bibcodes) + batch_size - 1)//batch_size}...")
        
        data = {
            "bibcode": batch
        }
        
        try:
            response = requests.post(
                "https://api.adsabs.harvard.edu/v1/export/bibtex",
                headers=headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            
            result = response.json()
            if 'export' not in result:
                print(f"Error: Unexpected response from ADS API: {result}")
                continue
            
            # Parse the BibTeX entries
            bibtex_str = result['export']
            parser = BibTexParser()
            bib_database = bibtexparser.loads(bibtex_str, parser)
            bibtex_entries.extend(bib_database.entries)
            
            # Wait a bit to avoid hitting rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching BibTeX entries from ADS: {e}")
    
    print(f"Successfully fetched {len(bibtex_entries)} BibTeX entries")
    return bibtex_entries

def process_bibtex_entries(entries):
    """Process BibTeX entries to add links and ensure consistency"""
    print("Processing BibTeX entries...")
    
    for entry in entries:
        # Ensure year is a string
        if 'year' in entry:
            entry['year'] = str(entry['year'])
        
        # Add title links if DOI is available
        if 'title' in entry:
            title = entry['title']
            # Remove any existing formatting
            title = re.sub(r'[{}]', '', title)
            
            if 'doi' in entry:
                doi = entry['doi']
                link = f"https://doi.org/{doi}"
                entry['title'] = f"{{<a href=\"{link}\" target=\"\\_\">{title}</a>}}"
            else:
                entry['title'] = f"{{{title}}}"
    
    return entries

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
            
            # Copy any additional fields from existing entry
            for field_key, value in existing.items():
                if field_key not in entry and field_key not in ['ID', 'ENTRYTYPE']:
                    entry[field_key] = value
            
            updated_count += 1
            del existing_entries[key]
        else:
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
        # Fetch publications from ADS
        publications = get_ads_publications()
        
        if not publications:
            print("No publications were fetched. Exiting.")
            return
        
        # Get BibTeX entries from ADS
        bibtex_entries = get_bibtex_for_publications(publications)
        
        if not bibtex_entries:
            print("No BibTeX entries were generated. Exiting.")
            return
        
        # Process BibTeX entries
        processed_entries = process_bibtex_entries(bibtex_entries)
        
        # Update BibTeX file
        update_bibtex_file(processed_entries)
        
        print("Publication update completed successfully.")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()