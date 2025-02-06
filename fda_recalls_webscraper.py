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

# List of irrelevant product types related to food allergies
IRRELEVANT_PRODUCT_TYPES = [
    "Animal & Veterinary", "Pet Food", "Medicated Feed", "Livestock Feed", "Medical Devices", 
    "Animal Drugs", "Drugs", "Animal Feed", "Cosmetics", "Biologics", "Skin Care Products", 
    "Contaminants", "Dietary Supplements", "Nutritional Supplement", "Generic Drugs", 
    "Over-the-Counter Drugs", "Foodborne Illness", "Tobacco", "Cardiovascular", 
    "General Hospital & Personal Use", "General & Plastic Surgery"
]

# Function to generate caption
ALWAYS_INCLUDED_HASHTAGS = "#FigApp #DietaryRestrictions #FoodAllergies #FoodAllergy #FoodIntolerances"

def generate_caption(recall):
    """Generates a smooth and accurate recall caption, with relevant hashtags."""
    brand_name = recall.get('Brand Name')
    product_description = recall.get('Product Description')
    recall_reason = recall.get('Recall Reason')
    recall_url = recall.get('Recall Page URL')
    
    # Process recall reason for a clean caption
    if "due to" in recall_reason.lower():
        recall_reason = f"due to {recall_reason.split('due to')[1].strip()}"
    
    safety_advice = "Please check the product details to determine if you are affected."
    
    caption = (
        f"🚨 Recall Alert! 🚨\n"
        f"{brand_name} is recalling {product_description} {recall_reason}. {safety_advice}\n"
        f"🔗 More info: {recall_url}\n"
    )

    hashtags = []
    if "milk" in recall_reason.lower(): hashtags.append("#MilkAllergy")
    if "peanut" in recall_reason.lower(): hashtags.append("#PeanutAllergy")
    if "egg" in recall_reason.lower(): hashtags.append("#EggAllergy")
    hashtags.append(ALWAYS_INCLUDED_HASHTAGS)

    caption += " ".join(hashtags)
    return caption.strip()

# Function to download images
def download_image(img_url, folder, filename):
    """Downloads and saves an image correctly."""
    response = requests.get(img_url, stream=True, headers=HEADERS)
    if response.status_code == 200:
        file_extension = os.path.splitext(img_url.split("?")[0])[-1] or ".png"
        file_path = os.path.join(folder, filename + file_extension)
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Image saved: {file_path}")
    else:
        print(f"Failed to download image: {img_url}")

# Function to scrape recall data and images
def scrape_fda_recalls():
    try:
        response = requests.get(RECALLS_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve recall page: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='lcds-datatable')
    if not table:
        print("Could not find the recall table.")
        return

    recalls = []
    for tr in table.find_all('tr')[1:]:
        cells = tr.find_all('td')
        if len(cells) < 7:
            continue

        brand_name = cells[1].text.strip()
        recall_link_tag = cells[1].find('a')
        recall_url = f"{BASE_URL}{recall_link_tag['href']}" if recall_link_tag else ""
        product_type = cells[3].text.strip()

        if any(irrelevant in product_type for irrelevant in IRRELEVANT_PRODUCT_TYPES):
            continue

        recall_entry = {
            'Date': cells[0].text.strip(),
            'Brand Name': brand_name,
            'Product Description': cells[2].text.strip(),
            'Product Type': product_type,
            'Recall Reason': cells[4].text.strip(),
            'Company Name': cells[5].text.strip(),
            'Recall Page URL': recall_url
        }
        recall_entry['Caption'] = generate_caption(recall_entry)
        recalls.append(recall_entry)

        if recall_url:
            scrape_recall_images(brand_name, recall_url)
        time.sleep(1)

    save_to_csv(recalls)
    print("Scraping completed.")

# Function to scrape product images from a recall page
def scrape_recall_images(brand_name, recall_url):
    response = requests.get(recall_url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    recall_photos_section = soup.find('div', id='recall-photos')
    if not recall_photos_section:
        print(f"No product images found for {brand_name}.")
        return

    images = recall_photos_section.find_all('picture')
    largest_image_dict = {}  # Store the largest image URLs

    for picture in images:
        source_tags = picture.find_all('source')
        for source in source_tags:
            img_url = source['srcset'].split(" ")[0]  # Extract URL
            img_width = int(source['srcset'].split(" ")[-1].replace('w', ''))  # Get width

            if img_url.startswith('/'):
                img_url = f"{BASE_URL}{img_url}"

            base_url = img_url.split("?")[0]  # Remove query parameters
            if base_url not in largest_image_dict or img_width > largest_image_dict[base_url][1]:
                largest_image_dict[base_url] = (img_url, img_width)

    # Download the largest images
    for index, (img_url, _) in enumerate(largest_image_dict.values(), start=1):
        img_filename = f"{brand_name}_image_{index}"
        img_filename = re.sub(r'[^\w\-_\. ]', '_', img_filename)  # Sanitize filename
        download_image(img_url, IMAGE_FOLDER, img_filename)

    if largest_image_dict:
        print(f"Downloaded {len(largest_image_dict)} unique largest images for {brand_name}.")
    else:
        print(f"No unique images to download for {brand_name}.")

# Run the scraper
scrape_fda_recalls()