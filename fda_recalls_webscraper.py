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
# Always included hashtags
ALWAYS_INCLUDED_HASHTAGS = "#FigApp #DietaryRestrictions #FoodAllergies #FoodAllergy #FoodIntolerances"

# Function to generate caption
def generate_caption(recall):
    """Generates a smooth and accurate recall caption, with relevant hashtags."""
    
    # Retrieve the relevant recall details
    brand_name = recall.get('Brand Name')
    product_description = recall.get('Product Description')
    recall_reason = recall.get('Recall Reason')
    recall_url = recall.get('Recall Page URL')
    
    # Check if 'due to' exists before splitting
    if "due to" in recall_reason.lower():
        if "undeclared" in recall_reason.lower():
            recall_reason = f"because the product contains {recall_reason.split('due to')[1].strip()}"
        elif "allergen" in recall_reason.lower():
            recall_reason = f"due to the presence of {recall_reason.split('due to')[1].strip()}"
        else:
            recall_reason = f"due to a safety concern: {recall_reason.split('due to')[1].strip()}"
    else:
        recall_reason = f"due to a safety concern: {recall_reason}"
    
    # Actionable safety advice
    if "milk" in recall_reason.lower():
        safety_advice = "If you have a dairy allergy, do not consume this product."
    else:
        safety_advice = "Please check the product details to determine if you are affected."
    
    # Construct the final caption
    caption = (
        f"🚨 Recall Alert! 🚨\n"
        f"{brand_name} is recalling {product_description} {recall_reason}. {safety_advice}\n"
        f"🔗 More info: {recall_url}\n"
    )

    # Adding relevant hashtags
    hashtags = []

    # Add specific allergen-related hashtags based on the recall reason
    if "milk" in recall_reason.lower():
        hashtags.append("#MilkAllergy")
    if "peanut" in recall_reason.lower():
        hashtags.append("#PeanutAllergy")
    if "egg" in recall_reason.lower():
        hashtags.append("#EggAllergy")
    if "soy" in recall_reason.lower():
        hashtags.append("#SoyAllergy")
    if "wheat" in recall_reason.lower():
        hashtags.append("#WheatAllergy")
    if "tree nut" in recall_reason.lower():
        hashtags.append("#TreeNutAllergy")
    if "fish" in recall_reason.lower():
        hashtags.append("#FishAllergy")
    if "shellfish" in recall_reason.lower():
        hashtags.append("#ShellfishAllergy")
    if "gluten" in recall_reason.lower():
        hashtags.append("#GlutenFree")

    # Append the always included hashtags
    hashtags.append(ALWAYS_INCLUDED_HASHTAGS)

    # Add the hashtags to the caption
    caption += " ".join(hashtags)

    return caption.strip()

# Example of how this would work with raw recall data:
recall_example = {
    'Brand Name': 'Fresh Direct',
    'Product Description': 'Dark Chocolate Covered Pretzels',
    'Recall Reason': 'Undeclared milk',
    'Recall Page URL': 'https://www.fda.gov/recalls/fresh-direct-dark-chocolate-covered-pretzels'
}

# Generate a caption
caption = generate_caption(recall_example)
print(caption)

# Example of how this would work with raw recall data:
recall_example = {
    'Brand Name': 'Fresh Direct',
    'Product Description': 'Dark Chocolate Covered Pretzels',
    'Recall Reason': 'Undeclared milk',
    'Recall Page URL': 'https://www.fda.gov/recalls/fresh-direct-dark-chocolate-covered-pretzels'
}

# Generate a caption
caption = generate_caption(recall_example)
print(caption)

# Function to download images
def download_image(img_url, folder, filename):
    """Downloads and saves an image correctly."""
    response = requests.get(img_url, stream=True, headers=HEADERS)
    if response.status_code == 200:
        file_extension = os.path.splitext(img_url.split("?")[0])[-1]  # Extracts proper file extension
        if not file_extension:
            file_extension = ".png"  # Default to PNG if unknown
        
        file_path = os.path.join(folder, filename + file_extension)

        # Save image in binary mode
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

        recall_url = ""
        if recall_link_tag and 'href' in recall_link_tag.attrs:
            recall_url = f"{BASE_URL}{recall_link_tag['href']}"

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

        # Generate caption and add to the recall entry
        recall_entry['Caption'] = generate_caption(recall_entry)

        recalls.append(recall_entry)

        if recall_url:
            scrape_recall_images(brand_name, recall_url)

        time.sleep(1)  # Pause to avoid hitting the server too frequently

    save_to_csv(recalls)
    print("Scraping completed.")

# Function to scrape product images from a recall page
def scrape_recall_images(brand_name, recall_url):
    response = requests.get(recall_url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the recall photos section
    recall_photos_section = soup.find('div', id='recall-photos')
    if not recall_photos_section:
        print(f"No product images found for {brand_name}.")
        return

    # Extract images from <picture> sources
    images = recall_photos_section.find_all('picture')
    unique_image_urls = set()  # Use a set to store unique image URLs

    for picture in images:
        source_tags = picture.find_all('source')

        for source in source_tags:
            img_url = source['srcset'].split(" ")[0]  # Get the URL from srcset

            # Convert relative URLs to absolute URLs
            if img_url.startswith('/'):
                img_url = f"{BASE_URL}{img_url}"

            unique_image_urls.add(img_url)  # Add to the set of unique URLs

    # Download each unique image
    for img_url in unique_image_urls:
        # Generate a clean filename
        img_filename = f"{brand_name}_image"
        img_filename = re.sub(r'[^\w\-_\. ]', '_', img_filename)  # Sanitize filename

        # Download the image
        download_image(img_url, IMAGE_FOLDER, img_filename)

    if unique_image_urls:
        print(f"Downloaded {len(unique_image_urls)} unique images for {brand_name}.")
    else:
        print(f"No unique images to download for {brand_name}.")

# Function to save recall data to CSV
def save_to_csv(data, filename='recalls.csv'):
    if not data:
        print("No new recalls to save.")
        return

    fieldnames = list(data[0].keys())

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"Recall data saved to {filename}")

# Run the scraper
scrape_fda_recalls()