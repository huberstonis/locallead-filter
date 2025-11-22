import csv
import requests
from bs4 import BeautifulSoup
import time
import random
import re

# --- CONFIGURATION (The simple front-end for your customer) ---
# NOTE: In a final app, these would come from the user's web input.
TARGET_CITY = "Chicago, IL"
TARGET_CATEGORIES = ["Plumber", "HVAC", "Roofer"]
OUTPUT_FILE = "filtered_leads_report.csv"

# Base URL for a generic, publicly scrapable directory (e.g., a non-specific dummy directory)
# NOTE: Replace this with the actual URL you decide to scrape.
BASE_URL = "http://www.example-business-directory.com/search?city={}&cat={}" 

# --- THE ROBUST, RULE-BASED ENGINE ---

def run_lead_filter_pro(city, categories):
    all_leads = []
    
    # 1. Loop through all target categories
    for category in categories:
        print(f"--- Searching for {category} in {city} ---")
        
        # NOTE: This URL is illustrative. A real scraper would use the correct structure.
        search_url = BASE_URL.format(city, category)
        
        try:
            # 2. Robust HTTP Request with anti-block headers and random delay
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/'
            }
            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status() # Raise error for bad status codes (4xx or 5xx)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # --- The COMPLEX FILTERING LOGIC (The high-value part) ---
            
            # NOTE: Adjust the selector based on the directory structure (e.g., 'div.listing-card')
            listings = soup.select('div.business-listing') 
            
            for listing in listings:
                name = listing.select_one('h2.name').text.strip() if listing.select_one('h2.name') else "N/A"
                address = listing.select_one('p.address').text.strip() if listing.select_one('p.address') else "N/A"
                
                # The HIGH-VALUE RULE: Check for signs of being 'underserved'
                
                # Rule 1: Check for explicit email address (Indicates they are already marketed to)
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', listing.text)
                has_email = bool(email_match)
                
                # Rule 2: Check for a dedicated 'Modern Website' link text (Indicates they are tech-savvy)
                website_link = listing.select_one('a[href*="modern-web-template"]') 
                has_modern_website = bool(website_link)

                # Rule 3: Robust Check (The core filter)
                # We only want leads that are LACKING both a visible email AND a clear website link.
                if not has_email and not has_modern_website:
                    all_leads.append({
                        'Name': name,
                        'Category': category,
                        'Address': address,
                        'Reason': 'Underserved (No Email/Modern Site Detected)'
                    })
                    print(f"  [FOUND] {name}")
                else:
                    print(f"  [SKIP] {name} (Already tech-savvy)")

            time.sleep(random.uniform(2, 5)) # Anti-block delay
            
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Failed to scrape {category}. Reason: {e}")
            continue # Move to the next category

    return all_leads

def save_to_csv(data, filename):
    """Saves the final, clean, high-value data to a CSV file."""
    if not data:
        print("No leads found to save.")
        return

    fieldnames = ['Name', 'Category', 'Address', 'Reason']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"\n✅ LEAD GENERATION COMPLETE. Saved {len(data)} high-value leads to {filename}")

# --- EXECUTION ---

if __name__ == "__main__":
    # The actual scraping and filtering starts here
    filtered_leads = run_lead_filter_pro(TARGET_CITY, TARGET_CATEGORIES)
    
    # Save the final deliverable (The asset you sell)
    save_to_csv(filtered_leads, OUTPUT_FILE)
    
    print("\n--- Next Steps ---")
    print("1. Find a customer (e.g., a marketing agency on LinkedIn).")
    print("2. Run this script locally with their desired parameters.")
    print("3. Email them the CSV and collect payment!")
