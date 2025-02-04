import requests
from bs4 import BeautifulSoup
import csv
import os
import re

# Base FDA URL
BASE_URL = "https://www.fda.gov"
RECALLS_URL = f"{BASE_URL}/safety/recalls-market-withdrawals-safety-alerts"

# Create a directory for images if it doesn't exist
IMAGE_FOLDER = 'product_images'
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Function to download images
def download_image(url, folder_path, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(folder_path, filename), 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download: {url}")

# Function to scrape recall data and images
def scrape_fda_recalls():
    response = requests.get(RECALLS_URL)
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
        if cells:
            brand_name = cells[1].text.strip()
            recall_link_tag = cells[1].find('a')

            if recall_link_tag and 'href' in recall_link_tag.attrs:
                recall_url = f"{BASE_URL}{recall_link_tag['href']}"
                
                # Scrape the recall page for images
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

    # Save recalls to CSV
    save_to_csv(recalls)
    print("Scraping completed.")

# Function to scrape product images from a recall page
def scrape_recall_images(brand_name, recall_url):
    response = requests.get(recall_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find images
    images = soup.find_all('img', src=re.compile(r'\.(jpg|jpeg|png|gif)$'))
    
    for img in images:
        img_url = img['src']

        # Handle relative URLs
        if img_url.startswith('/'):
            img_url = f"{BASE_URL}{img_url}"

        img_filename = f"{brand_name}_{os.path.basename(img_url)}"
        img_filename = re.sub(r'[^\w\-_\. ]', '_', img_filename)  # Clean filename

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
