# Prism Fold Lead Generation

This repository contains several open-source lead generation tools customized to run on Google Cloud without incurring high costs (using the standard environment).

All tools are configured to save leads offline locally as CSV files to avoid continuous API calls and preserve "pro plan" usages for other services.

## Available Tools

We have included three top-rated open-source repositories to generate leads:

### 1. Google Maps Lead Generator (`google-maps-lead-generator/`)
- **Purpose**: Extracts Google Maps business leads.
- **Why it's good**: Free to run. Avoids paid Maps APIs by using headless browser automation/web scraping to pull local businesses.
- **Offline Output**: Generates localized offline data files containing business names, websites, and potential contact information.

### 2. Email Crawler Lead Generator (`Email-Crawler-Lead-Generator/`)
- **Purpose**: Crawls a specific target website to find all associated email addresses.
- **Why it's good**: Useful when you already have a target list of URLs (perhaps generated from Google Maps or `lead_generator.py`) and need to extract emails directly from the domains.
- **Offline Output**: Saves crawled emails to a CSV.

### 3. LinkedIn Lead Generator (`Linkedin-Lead-Generator/`)
- **Purpose**: Scrapes LinkedIn via Sales Navigator and Google to find emails and domains.
- **Why it's good**: Good for finding specific decision-makers (e.g., "Marketing Director"). *Note: LinkedIn scraping requires your own LinkedIn account cookie and can result in rate-limiting.*
- **Offline Output**: Outputs to a local file.

### 4. Custom Generic Web Scraper (`lead_generator.py`)
- **Purpose**: A lightweight custom script that searches Google for a query and scrapes basic contact info (emails/phone numbers) into `leads.csv`.
- **Usage**: `python lead_generator.py "local restaurants in austin" --num_results 50`

## Running on Google Cloud

To run these tools efficiently on Google Cloud (GCP) and avoid usage limits:

1. **Compute Engine (e2-micro / Free Tier)**:
   - Deploy an `e2-micro` instance in a supported region (like `us-central1`).
   - SSH into the instance and run these scripts.
   - Ensure you install dependencies for the tool you want to use (check their respective folders).
   - Once the scripts run, you can download the generated `CSV` files via `gcloud compute scp` or SFTP to work with them offline.

2. **Managing Rate Limits (Avoiding Blocks)**:
   - Automated scripts querying Google or LinkedIn will eventually hit captchas.
   - Run scripts slowly (using built-in sleep/delays).
   - Because you process the data offline in CSV format, you only need to run the generation step occasionally.
