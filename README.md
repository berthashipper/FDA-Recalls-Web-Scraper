# FDA Allergy Recall Scraper

This project is a web scraper designed to gather recall data from the FDA's recall page, focusing on product recalls related to food allergies. It extracts key information such as the brand name, product description, recall reason, and images (where available) and saves them to a CSV file. The scraper excludes irrelevant product types and downloads relevant product images to a local folder.

## Features

- Scrapes the FDA recall page for product recalls related to food allergies.
- Filters out irrelevant product types (e.g., medical devices, pet food, etc.).
- Downloads product images for relevant recalls and saves them in a local folder.
- Saves the recall data (including brand name, product description, etc.) into a CSV file.
- Includes a cron scheduler to periodically update the CSV file with the latest recall information.

## Installation

To use the scraper, you'll need Python 3.8 or higher and the following dependencies:

- `requests`: For making HTTP requests.
- `beautifulsoup4`: For parsing HTML and extracting relevant data.
- `csv`: For writing the data into CSV format.
- `os`: For file and directory management.
- `re`: For handling regular expressions.
- `time`: For controlling the scraping interval and preventing server overload.

### Installing Dependencies

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FDA-Recalls-Web-Scraper.git
   cd FDA-Recalls-Web-Scraper
2. Install the necessary packages:
   ```bash
   pip install requests beautifulsoup4
  
### Usage

1. Run the scraper to start gathering recall data:
   ```bash
   python fda_recalls_webscraper.py

### The scraper will:
- Visit the FDA recall page.
- Extract relevant recall data, such as:
  - Date of recall
  - Brand name
  - Product description
  - Recall reason
  - Company name
- Filter out irrelevant product types like medical devices and pet food.
- Download images for relevant recalls (saved in the product_images/ folder).
- Save the gathered data to a CSV file named recalls.csv.
  
To ensure the data is updated, accessed, and parsed regularly, you can use a cron job to run the scraper periodically. For example, you can set it to run every day at midnight:

1. Open the crontab file by running:
   ```bash
   crontab -e
3. Add the following line to schedule the script:
   ```bash
   0 0 * * * /usr/bin/python3 /path/to/fda_recalls_webscraper.py

### File Structure
```
fda-recall-scraper/
├── product_images/        # Folder where images will be saved
├── recalls.csv            # CSV file storing recall data
├── fda_recalls_webscraper.py  # Main script for scraping recall data
└── README.md              # This readme file
```

### How It Works
1. **Scraping the Recall Data**:

   The scraper starts by visiting the FDA's recall page and extracting the relevant data from the table containing product recalls. It filters out irrelevant product types (e.g., medical devices, pet food) based on a predefined list.

3. **Downloading Product Images**:
   
   For each relevant recall, the scraper checks if product images are available on the recall page. If images are found, it downloads the largest available image and saves it to the product_images/ folder with a sanitized filename.

5. **Saving Data to CSV**:
   
   All relevant recall data is saved to a CSV file (recalls.csv). This CSV includes columns for the date, brand name, product description, product type, recall reason, company name, and the URL of the recall page.

7. **Cron Job Scheduler**:
   
   A cron job can be set up to periodically run the scraper, ensuring that the CSV file stays up-to-date with the latest recalls. By running the scraper daily (or at any desired interval), the CSV file is updated automatically.


### Acknowledgements
- The FDA for providing public access to recall data.
- BeautifulSoup for parsing HTML data.
- Requests for making HTTP requests.

### Contact
With any questions, contact me via berthashipper@gmail.com.
