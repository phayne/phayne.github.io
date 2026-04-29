#!/usr/bin/env python3
'''
Script to generate a group members page from a YAML file for a Jekyll website
using the al-folio theme.
'''

import yaml
import os
import re
from datetime import datetime

# Configuration
YAML_PATH = "../_data/group_members.yml"
OUTPUT_PATH = "../_pages/2_group.md"
IMAGE_PATH = "/assets/img/group/"  # Path to group member images (web path)
IMAGE_DIR = "../assets/img/group/"  # Actual directory path for file existence check
DEFAULT_IMAGE = "missing.jpg"  # Default image for members without a photo

def read_group_data():
    """Read group member data from YAML file"""
    if not os.path.exists(YAML_PATH):
        print(f"Error: YAML file not found at {YAML_PATH}")
        return []
        
    try:
        with open(YAML_PATH, 'r', encoding='utf-8') as f:
            members = yaml.safe_load(f)
        
        print(f"Read {len(members)} members from YAML")
        return members
    except Exception as e:
        print(f"Error reading YAML file: {e}")
        return []

def extract_custom_content():
    """Extract the EPIC group description and photo from the current group page if they exist"""
    if not os.path.exists(OUTPUT_PATH):
        return None
        
    try:
        with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
            current_content = f.read()
            
        # Look for content between the style block and the "Last updated" line
        pattern = r'</style>\s*(.*?)\s*\*Last updated:'
        match = re.search(pattern, current_content, re.DOTALL)
        
        if match and len(match.group(1).strip()) > 0:
            custom_content = match.group(1).strip()
            print("Found existing custom content (EPIC description and/or photo)")
            return custom_content
        return None
    except Exception as e:
        print(f"Error reading existing group page: {e}")
        return None

def image_exists(image_filename):
    """Check if an image file exists in the assets directory"""
    if not image_filename:
        return False
    
    image_path = os.path.join(IMAGE_DIR, image_filename)
    return os.path.isfile(image_path)

def get_last_name(name):
    """Extract the last name from a full name for sorting purposes
    
    Handles cases like "John Doe", "Jane M. Doe", and "John von Neumann"
    Special case for names with parentheses like "John Doe (Ph.D.)"
    """
    # Remove any parenthetical information
    name_without_parentheses = name.split('(')[0].strip()
    
    # Split the name by spaces
    parts = name_without_parentheses.split()
    
    # If only one part, return it
    if len(parts) == 1:
        return parts[0]
    
    # Handle common prefixes like 'von', 'van', 'de', etc.
    common_prefixes = ['von', 'van', 'de', 'la', 'du', 'di', 'del']
    
    # Check if the second-to-last part is a common prefix
    if len(parts) > 2 and parts[-2].lower() in common_prefixes:
        # Return the prefix + last name together
        return f"{parts[-2]} {parts[-1]}"
    
    # Return just the last part (assumed to be last name)
    return parts[-1]

def categorize_members(members):
    """Categorize members by role and status with specific ordering"""
    categories = {
        "Current": {},
        "Alumni": []
    }
    
    # Define the order of roles (with Research Associates and Postdocs grouped together)
    role_order = [
        "Principal Investigator",
        "Research Associates and Postdocs",  # Combined category
        "PhD Student",
        "Graduate Student",
        "Undergraduate Student",
        "Other"  # Catch-all for any undefined roles
    ]
    
    # Initialize categories with ordered roles
    for role in role_order:
        categories["Current"][role] = []
    
    # Second pass: assign members to categories
    for member in members:
        status = member["status"].lower()
        if status.startswith("alumni") or "former" in status:
            categories["Alumni"].append(member)
        else:
            role = member["role"]
            
            # Special case: Keep Paul Hayne as Principal Investigator regardless of role
            if member["name"] == "Paul Hayne":
                categories["Current"]["Principal Investigator"].append(member)
            # Map Research Associate and Postdoc to the combined category
            elif role == "Research Associate" or role == "Postdoc":
                categories["Current"]["Research Associates and Postdocs"].append(member)
            elif role in categories["Current"]:
                categories["Current"][role].append(member)
            else:
                # For any undefined roles, put them in "Other"
                categories["Current"]["Other"].append(member)
    
    # Remove empty categories
    for role in list(categories["Current"].keys()):
        if not categories["Current"][role]:
            del categories["Current"][role]
    
    # Sort each category by last name
    for role in categories["Current"]:
        # Skip sorting the PI category if it's just Paul Hayne
        if role == "Principal Investigator" and len(categories["Current"][role]) <= 1:
            continue
        categories["Current"][role] = sorted(
            categories["Current"][role], 
            key=lambda x: get_last_name(x["name"]).lower()
        )
    
    # Sort alumni by last name
    categories["Alumni"] = sorted(
        categories["Alumni"], 
        key=lambda x: get_last_name(x["name"]).lower()
    )
    
    return categories

def generate_member_html(member):
    """Generate HTML for a group member"""
    html = '<div class="group-member">\n'
    
    # Image (use default if image is missing or doesn't exist)
    if member.get("image") and image_exists(member["image"]):
        html += f'  <img class="profile-img" src="{IMAGE_PATH}{member["image"]}" alt="{member["name"]}">\n'
    else:
        html += f'  <img class="profile-img" src="{IMAGE_PATH}{DEFAULT_IMAGE}" alt="{member["name"]}">\n'
    
    # Name with optional website link
    if member.get("website"):
        html += f'  <h4><a href="{member["website"]}" target="_blank">{member["name"]}</a></h4>\n'
    else:
        html += f'  <h4>{member["name"]}</h4>\n'
    
    # Role
    html += f'  <p class="role">{member["role"]}</p>\n'
    
    # Status for alumni
    if member["status"].lower().startswith("alumni") or "former" in member["status"].lower():
        html += f'  <p class="status">{member["status"]}</p>\n'
    
    # Research interests
    if member.get("research_interest"):
        html += f'  <p class="interests">{member["research_interest"]}</p>\n'
    
    html += '</div>\n'
    return html

def generate_markdown_content(categories, custom_content=None):
    """Generate full markdown content for the group page"""
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Page header
    content = f"""---
layout: page
title: group
permalink: /group/
description: Members of the Hayne Research Group
---

<style>
.group-container {{
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 20px;
}}
.group-member {{
  width: 200px;
  margin-bottom: 30px;
}}
.profile-img {{
  width: 180px;
  height: 180px;
  object-fit: cover;
  border-radius: 5px;
}}
.role {{
  margin: 0;
  color: #555;
}}
.status {{
  margin: 0;
  color: #777;
  font-style: italic;
}}
.interests {{
  margin-top: 5px;
  font-size: 0.9em;
}}
</style>

"""

    # Add the custom content (EPIC description and photo) if it exists
    if custom_content:
        content += custom_content + "\n\n"
    
    # Add the last updated date
    content += f"*Last updated: {current_date}*\n\n"
    
    content += "## Current Group Members\n\n"
    
    # Add current members by category, maintaining the desired order
    for role, members in categories["Current"].items():
        if members:
            # Special case for Principal Investigator (no plural)
            if role == "Principal Investigator":
                content += f"### {role}\n\n"
            else:
                # Determine plural form of role
                role_plural = role + "s" if not role.endswith("s") else role
                content += f"### {role_plural}\n\n"
            
            content += '<div class="group-container">\n'
            
            # Add each member in this role category
            for member in members:
                content += generate_member_html(member)
            
            content += '</div>\n\n'
    
    # Add alumni if any exist
    if categories["Alumni"]:
        content += "## Alumni\n\n"
        content += '<div class="group-container">\n'
        
        # Alumni are already sorted by last name in categorize_members
        for member in categories["Alumni"]:
            content += generate_member_html(member)
        
        content += '</div>\n'
    
    return content

def write_output_file(content):
    """Write the generated content to the output file"""
    directory = os.path.dirname(OUTPUT_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Group page successfully generated at {OUTPUT_PATH}")

def main():
    # Read group data from YAML
    members = read_group_data()
    if not members:
        return
    
    # Extract any existing custom content (EPIC description and photo)
    custom_content = extract_custom_content()
    
    # Categorize members
    categories = categorize_members(members)
    
    # Generate markdown content
    content = generate_markdown_content(categories, custom_content)
    
    # Write to output file
    write_output_file(content)
    
    print("Done! Remember to upload profile photos to the assets/img/group/ directory.")

if __name__ == "__main__":
    main()