
'''For this method I decided to utilize BeautifulSoup to parse HTML content and extracts text from webpages.
  This program then searches for the keyword "address" within the extracted text to identify address-related 
  information.Once the keyword is found, it will extract surrounding text to capture potential address details.
  However, this approach is simplistic and does not always accurately identify address information if the word 
  "address" is not present in the expected context or format. '''


import pandas as pd
import requests
from bs4 import BeautifulSoup

# Here I load the list of domains from the Parquet file. I decided to use Pandas for this action.
df_domains = pd.read_parquet('list_of_company_websites.snappy.parquet')

#Main function used to extract country-related information from the webpage content.
def extract_country_info(url):
    try:
        # Fetch webpage content
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text from webpage using the BeautifulSoup extention
        text = soup.get_text()

        # Here I decided to search for the keyword "country" in the webpage content in order to find relevant data

        country_index = text.lower().find('address')
        if country_index != -1:
            # We extract relevant text around the word "country"
            relevant_text = text[max(0, country_index - 100):country_index + 100]
            return relevant_text.strip()
        else:
            return None
    except Exception as e:
        print(f"Error extracting country information from {url}: {e}")
        return None


# Iterate over each domain
for index, row in df_domains.iterrows():
    domain = row['domain']
    website_url = f'http://{domain}'
    country_info = extract_country_info(website_url)
    if country_info:
        print(f"Country information found on {website_url}:")
        print(country_info)
        print()
    else:
        print(f"No country information found on {website_url}")
        print()

