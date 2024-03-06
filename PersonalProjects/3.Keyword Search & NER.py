
'''For this method I decided to combine the functionalities of both BeautifulSoup and spacy NER 
for address extraction. It will first extract text from webpages using BeautifulSoup and search for 
address-related keywords. After the keywords are identified, the code applies spacy's NER to further 
process the extracted text and identify address-related entities. By integrating both these methods, 
this approach can provide a more accurate extraction of address information, at the cost of additional 
complexity, however.'''

import pandas as pd
import requests
import re
import spacy
from bs4 import BeautifulSoup

# Here I load the list of domains from the Parquet file. I decided to use Pandas for this action.
df_domains = pd.read_parquet('list_of_company_websites.snappy.parquet')

# Load English language model for spacy
nlp = spacy.load("en_core_web_sm")

#Main function used to extract country-related information from the webpage content.
def extract_address_info(url):
    try:
        # Fetch webpage content
        response = requests.get(url)
        content = response.text

        # Extract text from webpage using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()

        #Here I decided to filter the search for the data by using address-related keywords in the webpage content.
        address_keywords = ['address', 'location', 'contact', 'locate']
        relevant_sections = []
        for keyword in address_keywords:
            if keyword in text.lower():
                relevant_sections.append(text.lower().split(keyword)[1])

        # I also define a regex pattern for extracting addresses
        address_pattern = re.compile(r'\b(\d{1,5}\s+\S+(\s+\S+)*,\s+\S+(\s+\S+)*,\s+\S{2,}\s+\d{5,})\b')

        # Dictionary to store address information
        address_info = {'Country': None, 'Region': None, 'City': None, 'Postcode': None, 'Road': None, 'Road Numbers': None}

        # Extract address information from relevant sections. Here I use the regex pattern
        for section in relevant_sections:
            matches = address_pattern.finditer(section)
            for match in matches:
                address_string = match.group(1)
                doc = nlp(address_string)

                # I initialize variables to store extracted entities
                country = None
                region = None
                city = None
                postcode = None
                road = None
                road_numbers = None

                # Extract entities using spacy NER
                for ent in doc.ents:
                    if ent.label_ == 'GPE': #If the entity is a geographical/political entity(GPE)
                        if ent.text.isalpha():
                            if ent.text[0].isupper():  # Check if the first letter is uppercase
                                country = ent.text
                    elif ent.label_ == 'LOC':  # If the entity is a location(LOC)
                        if ent.text.isalpha():
                            if ent.text[0].isupper():  # Check if the first letter is uppercase
                                if not region:
                                    region = ent.text
                                elif not city:
                                    city = ent.text
                    elif ent.label_ == 'CARDINAL':   # If entity is a numerical value(CARDINAL)
                        if ent.text.isdigit():
                            if not postcode:
                                postcode = ent.text
                            elif not road_numbers:
                                road_numbers = ent.text
                    else:
                        if ent.text.isalpha():
                            if not road:
                                road = ent.text

                # Updates address information dictionary
                address_info['Country'] = country
                address_info['Region'] = region
                address_info['City'] = city
                address_info['Postcode'] = postcode
                address_info['Road'] = road
                address_info['Road Numbers'] = road_numbers

        return address_info

    except Exception as e:
        print(f"Error extracting address information from {url}: {e}")
        return None


# Iterate over each domain
for index, row in df_domains.iterrows():
    domain = row['domain']
    website_url = f'http://{domain}'  
    address_info = extract_address_info(website_url)
    if address_info:
        print(f"Address information found on {website_url}:")
        # We print the extracted address information
        for key, value in address_info.items():
            print(f"{key.capitalize()}: {value}")
        print()
    else:
        print(f"No address information found on {website_url}")
        print()

