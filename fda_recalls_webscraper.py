import requests
from bs4 import BeautifulSoup
import csv
import os


## Scrape the FDA recalls page

# Step 1: Send a request to the FDA recalls page
url = "https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts"
response = requests.get(url)
html_content = response.content

# Step 2: Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Step 3: Find the table containing the recall data
table = soup.find('table', class_='lcds-datatable')  # Adjust the class name based on the actual HTML structure

# Step 4: Extract the table headers
headers = []
for th in table.find_all('th'):
    headers.append(th.text.strip())

# Step 5: Extract the rows of data
rows = []
for tr in table.find_all('tr')[1:]:  # Skip the header row
    cells = tr.find_all('td')
    if cells:  # Ensure the row has data
        row_data = {
            'Date': cells[0].text.strip(),
            'Brand Name(s)': cells[1].text.strip(),
            'Product Description': cells[2].text.strip(),
            'Product Type': cells[3].text.strip(),
            'Recall Reason Description': cells[4].text.strip(),
            'Company Name': cells[5].text.strip(),
            'Terminated Recall': cells[6].text.strip()
        }
        rows.append(row_data)

# Step 6: Write the data to a CSV file
with open('recalls.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = headers  # Use the headers extracted from the table
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

print("Data has been successfully scraped and saved to recalls.csv.")


## Scheduler/Check for new recalls

# Function to load previously scraped data
def load_previous_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            return {row['Date']: row for row in csv.DictReader(csvfile)}
    return {}

# Function to save new data
def save_data(filename, rows):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = rows[0].keys()  # Use the keys from the first row as headers
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

# Main function to scrape the FDA recalls page
def scrape_fda_recalls():
    url = "https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts"
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table containing the recall data
    table = soup.find('table', class_='lcds-datatable')
    
    # Load previously scraped data
    previous_data = load_previous_data('recalls.csv')
    new_rows = []

    # Extract the rows of data
    for tr in table.find_all('tr')[1:]:  # Skip the header row
        cells = tr.find_all('td')
        if cells:  # Ensure the row has data
            row_data = {
                'Date': cells[0].text.strip(),
                'Brand Name': cells[1].text.strip(),
                'Product Description': cells[2].text.strip(),
                'Product Type': cells[3].text.strip(),
                'Recall Reason': cells[4].text.strip(),
                'Company Name': cells[5].text.strip(),
                'Terminated Recall': cells[6].text.strip(),
                'Excerpt': cells[7].text.strip(),
            }
            # Check if this entry is new
            if row_data['Date'] not in previous_data:
                new_rows.append(row_data)

    # Save new data if there are any new entries
    if new_rows:
        save_data('recalls.csv', new_rows)
        print(f"New entries added: {len(new_rows)}")
    else:
        print("No new entries found.")

# Run the scraper
scrape_fda_recalls()