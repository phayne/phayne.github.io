#!/usr/bin/env python3
import re
import yaml
import sys
import os
from datetime import datetime
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

def expand_journal_name(abbrev):
    """Expand abbreviated journal names to their full titles"""
    if not abbrev:
        return ""
        
    journal_map = {
        "psj": "Planetary Science Journal",
        "ssr": "Space Science Reviews",
        "ssrv": "Space Science Reviews",
        "grl": "Geophysical Research Letters",
        "jgre": "Journal of Geophysical Research: Planets",
        "planss": "Planetary and Space Science",
        "p&ss": "Planetary and Space Science",
        "natgeo": "Nature Geoscience",
        "natas": "Nature Astronomy",
        "acaau": "Acta Astronautica",
        "revmg": "Reviews in Mineralogy and Geochemistry",
        "rvmg": "Reviews in Mineralogy and Geochemistry",
        "chegg": "Chemie der Erde - Geochemistry",
        "cheg": "Chemie der Erde - Geochemistry",
        "e&ss": "Earth and Space Science",
        "capj": "Current Applications in Planetary Sciences",
        "natco": "Nature Communications",
        "sci": "Science",
        "pnas": "Proceedings of the National Academy of Sciences",
        "jvgr": "Journal of Volcanology and Geothermal Research",
        "rems": "Remote Sensing",
        "plsci": "Planetary Science",
    }
    
    # First check for exact matches with our mapping
    if abbrev.lower() in journal_map:
        return journal_map[abbrev.lower()]
    
    # Special case for Unicode character in Icarus
    if "\u0131carus" in abbrev:
        return "Icarus"
        
    # Special case for ß (beta) which appears in SSRv
    if "ßr" in abbrev:
        return "Space Science Reviews"
    
    # Return the original name if no mapping found
    return abbrev

def latex_to_text(text):
    """Convert LaTeX symbols to HTML or Unicode equivalents."""
    if text is None:
        return ""
    
    # Handle LaTeX subscripts (e.g., CO$_2$ to CO<sub>2</sub>)
    text = re.sub(r'(\$_)(\{[^}]+\}|\d+)(\$)', r'<sub>\2</sub>', text)
    text = re.sub(r'(\$_)(\d+)(\$)', r'<sub>\2</sub>', text)
    text = re.sub(r'(\$\{\\rm )([^}]+)(\}\$)', r'\2', text)
    
    # Remove LaTeX $ delimiters while preserving content
    text = re.sub(r'\$([^$]+)\$', r'\1', text)
    
    # Handle LaTeX superscripts
    text = re.sub(r'(\$\^)(\{[^}]+\}|\d+)(\$)', r'<sup>\2</sup>', text)
    text = re.sub(r'(\$\^)(\d+)(\$)', r'<sup>\2</sup>', text)
    
    # Handle special characters and accents
    replacements = {
        r'\\textquoteright': "'",
        r'\\textquotedbl': '"',
        r'\\textquoteleft': "'",
        r'\\textendash': "–",
        r'\\textemdash': "—",
        r'\\textasciitilde': "~",
        r'\\textbackslash': "\\\\",  # Fixed escape sequence
        r'\\textgreater': ">",
        r'\\textless': "<",
        r'\\textbar': "|",
        r'\\textbf\{([^}]+)\}': r'<b>\1</b>',
        r'\\textit\{([^}]+)\}': r'<i>\1</i>',
        r'\\textsuperscript\{([^}]+)\}': r'<sup>\1</sup>',
        r'\\textsubscript\{([^}]+)\}': r'<sub>\1</sub>',
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
    
    # Handle special character accents separately with simpler patterns
    text = re.sub(r'\\~\{([a-zA-Z])\}', r'\1~', text)  # Simplify tilde handling
    text = re.sub(r'\\~([a-zA-Z])', r'\1~', text)  
    text = re.sub(r'\\"([a-zA-Z])', r'\1"', text)  # Simplify umlaut
    text = re.sub(r"\\'([a-zA-Z])", r'\1\'', text)  # Simplify acute
    text = re.sub(r'\\`([a-zA-Z])', r'\1`', text)  # Simplify grave
    text = re.sub(r'\\^([a-zA-Z])', r'\1^', text)  # Simplify circumflex
    
    # Replace common LaTeX symbols
    more_replacements = {
        r'\\aa': "å",
        r'\\AA': "Å",
        r'\\o': "ø",
        r'\\O': "Ø",
        r'\\ae': "æ",
        r'\\AE': "Æ",
        r'\\ss': "ß",
        r'\\i': "ı",
        r'\\j': "ȷ",
        r'\\l': "ł",
        r'\\L': "Ł",
    }
    
    for pattern, replacement in more_replacements.items():
        text = re.sub(pattern, replacement, text)
    
    # Special handling for CO2 and similar patterns
    text = re.sub(r'CO_2', r'CO<sub>2</sub>', text)
    text = re.sub(r'CO\$_2\$', r'CO<sub>2</sub>', text)
    text = re.sub(r'H\$_2\$O', r'H<sub>2</sub>O', text)
    
    # Remove remaining LaTeX commands (simple ones that don't need special handling)
    text = re.sub(r'\\([a-zA-Z]+)', r'\1', text)
    
    # Clean up any remaining curly braces
    text = text.replace('{', '').replace('}', '')
    
    return text

def get_group_members():
    """Read group members from the YAML file."""
    group_members_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      '_data', 'group_members.yml')
    try:
        with open(group_members_file, 'r') as f:
            members_data = yaml.safe_load(f)
            members = []
            for member in members_data:
                if 'name' in member:
                    full_name = member['name']
                    members.append(full_name)
                    last_name = full_name.split()[-1]
                    members.append(last_name)
            return members
    except Exception as e:
        print(f"Warning: Could not load group members: {e}")
        return []

def is_hayne(author):
    """Check if an author is Paul Hayne using a strict pattern match"""
    return bool(re.search(r'Hayne\b', author, re.IGNORECASE)) and not bool(re.search(r'Hayes\b', author, re.IGNORECASE))

def format_author_name_apa(author):
    """Format an author name in APA style: Last, F. M."""
    # Remove any remaining special characters and extra spaces
    author = author.replace('~', ' ').strip()
    
    # Check if the name is already in "Last, First" format
    if ',' in author:
        parts = author.split(',', 1)
        last = parts[0].strip()
        firsts = parts[1].strip().split()
        
        # Format first name and middle name initials
        initials = ' '.join([f"{n[0]}." for n in firsts if n])
        return f"{last}, {initials}"
    else:
        # Assuming "First Last" format
        parts = author.split()
        if len(parts) <= 1:
            return author
            
        last = parts[-1]
        firsts = parts[:-1]
        
        # Format first name and middle name initials
        initials = ' '.join([f"{n[0]}." for n in firsts if n])
        return f"{last}, {initials}"

def format_author_name(author, group_members):
    """Format an individual author name with appropriate styling."""
    # First convert to APA style
    author_apa = format_author_name_apa(author)
    
    # Check if this is Paul Hayne
    if is_hayne(author):
        return f"<b>Hayne, P. O.</b>"  # Consistent naming for Paul Hayne
    
    # Check if the author is a group member (other than Paul)
    for member in group_members:
        # Skip if member is Paul Hayne (handled above)
        if "hayne" in member.lower() and "paul" in member.lower():
            continue
            
        # Check if current author name contains or matches a group member name
        member_parts = member.lower().split()
        author_lower = author_apa.lower()
        
        # For each part of the member name (first name, last name)
        for part in member_parts:
            # Only match if part is at least 4 characters (to avoid false positives)
            if len(part) >= 4 and part in author_lower:
                # Use a lighter blue for group members
                return f'<b><span style="color:#6495ED">{author_apa}</span></b>'
    
    return author_apa

def process_author_list(authors_string, group_members):
    """Process the author list to format names and handle et al."""
    if not authors_string:
        return ""
    
    # First, identify already formatted HTML entries (they might contain commas)
    html_pattern = r'<[^>]+>[^<]+<\/[^>]+>'
    html_tags = re.findall(html_pattern, authors_string)
    
    # Replace HTML tags with placeholders to protect them during splitting
    placeholders = {}
    for i, tag in enumerate(html_tags):
        placeholder = f"__HTML_TAG_{i}__"
        authors_string = authors_string.replace(tag, placeholder)
        placeholders[placeholder] = tag
    
    # Split the authors by 'and' or by commas
    # This approach handles both BibTeX-style "and" separators and comma separators
    if " and " in authors_string:
        authors = [a.strip() for a in authors_string.split(" and ")]
    else:
        # For comma-separated authors, be careful about commas within author names
        authors = []
        parts = [p.strip() for p in authors_string.split(",")]
        i = 0
        while i < len(parts):
            if i + 1 < len(parts) and re.match(r'^[A-Z]\.', parts[i+1].strip()):
                # This looks like a first initial after a last name, keep them together
                authors.append(f"{parts[i]}, {parts[i+1]}")
                i += 2
            else:
                authors.append(parts[i])
                i += 1
    
    # Restore HTML tags
    for i, author in enumerate(authors):
        for placeholder, tag in placeholders.items():
            if placeholder in author:
                authors[i] = author.replace(placeholder, tag)
    
    # Filter out empty entries and "et al."
    authors = [a.strip() for a in authors if a.strip() and "et al." not in a.lower()]
    
    # Check if Paul Hayne is in the author list and find his position
    paul_hayne_index = -1
    for i, author in enumerate(authors):
        if is_hayne(author):
            paul_hayne_index = i
            break
    
    # Format each author name
    formatted_authors = [format_author_name(author, group_members) for author in authors]
    
    # For longer lists, always show the first three authors, then "et al."
    if len(formatted_authors) > 3:
        # Explicitly join exactly three authors
        result = ", ".join(formatted_authors[:3]) + ", et al."
        
        # Add note if Paul Hayne is beyond position 2
        if paul_hayne_index > 2:
            result += " (including P. O. Hayne)"
    else:
        # If 3 or fewer authors, show them all
        result = ", ".join(formatted_authors)
    
    return result

def clean_bibtex_authors(authors_string):
    """Clean author names from BibTeX format."""
    if not authors_string:
        return ""
    
    # Remove curly braces around entire author list or individual names
    authors_string = re.sub(r'^\{(.*?)\}$', r'\1', authors_string)
    
    # Handle LaTeX formatting without using the main latex_to_text function
    # to avoid regex issues with complex author strings
    authors_string = authors_string.replace('\\', '')  # Remove backslashes
    authors_string = authors_string.replace('{', '').replace('}', '')  # Remove braces
    
    # Remove all tildes that are used in BibTeX for non-breaking spaces
    authors_string = authors_string.replace('~', ' ')
    
    return authors_string

def convert_bibtex_to_yaml(bibtex_file, yaml_file):
    """Convert BibTeX file to YAML."""
    with open(bibtex_file) as bibfile:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(bibfile, parser=parser)
    
    # Get group members for highlighting
    group_members = get_group_members()
    
    entries = []
    for entry in bib_database.entries:
        yaml_entry = {}
        
        # Extract key information from the BibTeX entry
        yaml_entry['key'] = entry.get('ID', '')
        
        # Clean up author names and apply formatting
        authors = entry.get('author', '')
        cleaned_authors = clean_bibtex_authors(authors)
        yaml_entry['authors'] = process_author_list(cleaned_authors, group_members)
        
        # Process title with proper HTML conversions
        title = entry.get('title', '')
        # Remove the HTML link wrapping if present
        title = re.sub(r'<a href="[^"]*" target="[^"]*">(.*?)</a>', r'\1', title)
        yaml_entry['title'] = latex_to_text(title)
        
        # Process other fields
        for field in ['year', 'month', 'volume', 'number', 'pages', 'doi']:
            if field in entry:
                yaml_entry[field] = latex_to_text(entry[field])
        
        # Process journal name separately to expand abbreviations
        if 'journal' in entry:
            journal = latex_to_text(entry['journal'])
            yaml_entry['journal'] = expand_journal_name(journal)
        
        # Add URL
        if 'doi' in yaml_entry:
            yaml_entry['url'] = f"https://doi.org/{yaml_entry['doi']}"
        elif 'adsurl' in entry:
            yaml_entry['url'] = latex_to_text(entry['adsurl'])
        
        entries.append(yaml_entry)
    
    # Sort entries by year (descending) and then by month
    month_order = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 
                  'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}
    
    def entry_sort_key(e):
        year = int(e.get('year', '0'))
        month_str = e.get('month', '').lower()
        month = month_order.get(month_str, 0)
        return (-year, -month)  # Negative to sort in descending order
    
    sorted_entries = sorted(entries, key=entry_sort_key)
    
    # Write to YAML file
    with open(yaml_file, 'w') as outfile:
        outfile.write(f"# Generated from {os.path.basename(bibtex_file)} on {datetime.now().strftime('%Y-%m-%d')}\n")
        yaml.dump(sorted_entries, outfile, default_flow_style=False, sort_keys=False)
    
    print(f"Converted {len(entries)} entries from {bibtex_file} to {yaml_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python bibtex_to_yaml.py input.bib output.yml")
        sys.exit(1)
    
    bibtex_file = sys.argv[1]
    yaml_file = sys.argv[2]
    
    convert_bibtex_to_yaml(bibtex_file, yaml_file)