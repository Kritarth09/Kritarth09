import argparse
import csv
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from googlesearch import search

def get_search_results(query, num_results):
    print(f"Searching Google for: '{query}'...")
    try:
        # googlesearch-python uses 'num' in older versions or 'num_results'.
        # Actually it's an iterator, so we fetch exactly what we need.
        # It's better to fetch slightly more and slice it.
        urls = list(search(query, num_results=num_results))
        if not urls:
             # try without num_results to see if it makes a difference
             urls = []
             for i, url in enumerate(search(query)):
                  if i >= num_results:
                       break
                  urls.append(url)
        print(f"Found {len(urls)} URLs.")
        return urls
    except Exception as e:
        print(f"Error during search: {e}")
        return []

def extract_contact_info(url):
    print(f"Scraping: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()

        # Simple Regex for Email
        emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text_content))

        # Simple Regex for Phone Numbers (US/International-ish)
        # Refined to avoid overly matching plain 10+ digit numbers like ISBNs or timestamps.
        # Matches formats like:
        # (123) 456-7890
        # 123-456-7890
        # 123.456.7890
        # +1 123 456 7890
        phone_pattern = r'''(?x)
            (?:(?:\+?\d{1,3})[\s.-]?)?     # Optional country code e.g. +1
            (?:(?:\(\d{3}\))|(?:\d{3}))     # Area code e.g. (123) or 123
            [\s.-]?                         # Separator
            \d{3}                           # 3 digits
            [\s.-]?                         # Separator
            \d{4}                           # 4 digits
        '''

        phones = set(re.findall(phone_pattern, text_content))

        # filter out some obvious non-phones
        valid_phones = set()
        for p in phones:
             p_clean = p.strip()
             # A valid phone string for humans usually has some formatting
             # or length constraints. We filter out purely contiguous large numbers
             # over 11 digits that have no formatting.
             digits = re.sub(r'\D', '', p_clean)
             if 10 <= len(digits) <= 15:
                 if len(digits) == len(p_clean) and len(digits) > 11:
                     continue # likely an ISBN or timestamp
                 valid_phones.add(p_clean)


        return {
            "URL": url,
            "Emails": ", ".join(emails) if emails else "None",
            "Phone Numbers": ", ".join(valid_phones) if valid_phones else "None"
        }
    except requests.exceptions.RequestException as e:
        print(f"  -> Failed to fetch {url}: {e}")
        return {
            "URL": url,
            "Emails": "Error",
            "Phone Numbers": "Error"
        }
    except Exception as e:
        print(f"  -> Error processing {url}: {e}")
        return {
            "URL": url,
            "Emails": "Error",
            "Phone Numbers": "Error"
        }

def main():
    parser = argparse.ArgumentParser(description="Lead Generator for Prism Fold")
    parser.add_argument("query", help="Search query (e.g., 'local coffee shops in Austin')")
    parser.add_argument("--num_results", type=int, default=10, help="Number of Google search results to process")
    parser.add_argument("--output", default="leads.csv", help="Output CSV file name")

    args = parser.parse_args()
    print(f"Starting lead generation for query: '{args.query}'")
    print(f"Will process {args.num_results} results and save to {args.output}")

    urls = get_search_results(args.query, args.num_results)

    if not urls:
        print("No URLs found. Exiting.")
        return

    print("\nExtracting contact info...")
    leads = []

    # Use ThreadPoolExecutor to speed up web requests
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(extract_contact_info, urls)
        for result in results:
            leads.append(result)

    print(f"\nFinished extracting. Saving to {args.output}...")
    try:
        with open(args.output, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["URL", "Emails", "Phone Numbers"])
            writer.writeheader()
            for lead in leads:
                writer.writerow(lead)
        print("Done!")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

if __name__ == "__main__":
    main()
