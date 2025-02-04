import requests
from bs4 import BeautifulSoup
import csv
import os
import re
import time

# Base FDA URL
BASE_URL = "https://www.fda.gov"
RECALLS_URL = f"{BASE_URL}/safety/recalls-market-withdrawals-safety-alerts"

# Create a directory for images if it doesn't exist
IMAGE_FOLDER = 'product_images'
os.makedirs(IMAGE_FOLDER, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Function to download images
def download_image(url, folder_path, filename):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            with open(os.path.join(folder_path, filename), 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download {url} (Status: {response.status_code})")
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")

# Function to scrape recall data and images
def scrape_fda_recalls():
    try:
        response = requests.get(RECALLS_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve recall page: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the recall table
    table = soup.find('table', class_='lcds-datatable')
    if not table:
        print("Could not find the recall table.")
        return

    recalls = []
    
    # Extract recall data
    for tr in table.find_all('tr')[1:]:  # Skip the header row
        cells = tr.find_all('td')
        if len(cells) < 7:
            continue  # Skip rows with missing data
        
        brand_name = cells[1].text.strip()
        recall_link_tag = cells[1].find('a')

        recall_url = ""
        if recall_link_tag and 'href' in recall_link_tag.attrs:
            recall_url = f"{BASE_URL}{recall_link_tag['href']}"
            scrape_recall_images(brand_name, recall_url)

        recalls.append({
            'Date': cells[0].text.strip(),
            'Brand Name': brand_name,
            'Product Description': cells[2].text.strip(),
            'Product Type': cells[3].text.strip(),
            'Recall Reason': cells[4].text.strip(),
            'Company Name': cells[5].text.strip(),
            'Terminated Recall': cells[6].text.strip(),
            'Recall Page URL': recall_url
        })

        time.sleep(1)  # Avoid overloading the server

    # Save recalls to CSV
    save_to_csv(recalls)
    print("Scraping completed.")

# Function to scrape product images from a recall page
def scrape_recall_images(brand_name, recall_url):
    response = requests.get(recall_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the recall photos section
    recall_photos_section = soup.find('div', id='recall-photos')
    if not recall_photos_section:
        print(f"No product images found for {brand_name}.")
        return

    # Extract images from <img> inside <picture>
    images = recall_photos_section.find_all('img')

    for img in images:
        img_url = img['src']

        # Convert relative URLs to absolute URLs
        if img_url.startswith('/'):
            img_url = f"{BASE_URL}{img_url}"

        img_filename = f"{brand_name}_{os.path.basename(img_url)}"
        img_filename = re.sub(r'[^\w\-_\. ]', '_', img_filename)  # Sanitize filename

        download_image(img_url, IMAGE_FOLDER, img_filename)

# Function to save recall data to CSV
def save_to_csv(data, filename='recalls.csv'):
    if not data:
        print("No new recalls to save.")
        return

    fieldnames = data[0].keys()

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"Recall data saved to {filename}")

# Run the scraper
scrape_fda_recalls()
