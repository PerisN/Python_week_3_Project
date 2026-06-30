import csv
import json
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

# STEP 1: Fetch Currency Exchange Rates
print("Step 1: Fetching live exchange rates...")

api_url = "https://open.er-api.com/v6/latest/GBP"

try:
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()  
    data = response.json()

    # Extract the KES conversion rate from the rates dictionary
    exchange_rate = data["rates"]["KES"]
    print(f"-> Success! Current Exchange Rate (GBP to KES): {exchange_rate:.2f}\n")

except requests.exceptions.RequestException as e:
    print(f"-> Error fetching exchange rates: {e}")
    print("-> Falling back to a hardcoded rate of 165.00 KES.")
    exchange_rate = 165.00 

# STEP 2: Scrape Product Data from Website
print("Step 2: Scraping data from books.toscrape.com...")

scrape_url = "https://books.toscrape.com/"

try:
    # Send a GET request to the target website
    web_response = requests.get(scrape_url, timeout=10)
    web_response.raise_for_status()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(web_response.text, "html.parser")

    # Find all book containers on the page (each book is inside an <article class="product_pod">)
    book_pods = soup.find_all("article", class_="product_pod")
    print(f"-> Found {len(book_pods)} books on the page. Processing...\n")

except requests.exceptions.RequestException as e:
    print(f"-> Critical Error: Failed to connect to the website. {e}")
    exit()

# List to store our structured data
scraped_books = []

# Loop through the books 
for book in book_pods[:15]:  
    try:
        title = book.h3.a["title"]

        raw_price = book.find("p", class_="price_color").text

        cleaned_price_gbp = float(re.sub(r"[^\d.]", "", raw_price))

        # Calculate the price in Kenyan Shillings (KES)
        price_kes = round(cleaned_price_gbp * exchange_rate, 2)

        # Append the structured data to our list
        scraped_books.append(
            {
                "Title": title,
                "Price (GBP)": f"£{cleaned_price_gbp:.2f}",
                "Price (KES)": f"KES {price_kes:,.2f}",
            }
        )

    except AttributeError:
        print("-> Skipping a book due to missing element or parsing error.")
        continue

# STEP 3: Display the Results using Pandas
print("Step 3: Generating Data Summary...")

# Load our dictionary list into a Pandas DataFrame for clean presentation
df = pd.DataFrame(scraped_books)

# Print the DataFrame in a beautifully aligned table structure
print("\n" + "=" * 70)
print(df.to_string(index=False))
print("=" * 70 + "\n")

# STEP 4: Save Data into a CSV File
csv_filename = "converted_book_prices.csv"
print(f"Step 4: Saving data to {csv_filename}...")

try:
    df.to_csv(csv_filename, index=False, encoding="utf-8")
    print("-> Data saved successfully! Automation complete.")
except Exception as e:
    print(f"-> Failed to save CSV file: {e}")

            

     






