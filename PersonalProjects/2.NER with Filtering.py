
'''For this method I utilized spacy's Named Entity Recognition (NER) capabilities to identify entities within the webpage content. 
The reason for this is because of spacy's capabilities to filter entities based on predefined labels such as GPE (Geopolitical Entity), 
LOC (Location), and CARDINAL (Numerical Value) to extract address-related information. The code will then process the identified entities 
to capture country, region, city, postcode, road, and road numbers. This approach is more robust and flexible compared to keyword search, 
as it leverages NER to understand the semantic meaning of entities and handle variations in address formats effectively.'''


import pandas as pd
import requests
import spacy

# Here I load the list of domains from the Parquet file. I decided to use Pandas for this action.
df_domains = pd.read_parquet('list_of_company_websites.snappy.parquet')

# Load English language model for spacy.
nlp = spacy.load("en_core_web_sm")

#Main function used to extract country-related information from the webpage content.
def extract_address_info(url):
    try:
        # Fetch webpage content
        response = requests.get(url)
        content = response.text

        #Here I decided to use Named Entity Recognition (NER) to extract entities using spacy
        doc = nlp(content)

        # Dictionary to store address information
        address_info = {'Country': None, 'Region': None, 'City': None, 'Postcode': None, 'Road': None, 'Road Numbers': None}

        # We extract relevant entities identified by spaCy
        for ent in doc.ents:
            if ent.label_ == 'GPE':   #If the entity is a geographical/political entity(GPE)
                if address_info['Country'] is None:
                    address_info['Country'] = ent.text
                elif address_info['Region'] is None:
                    address_info['Region'] = ent.text
                elif address_info['City'] is None:
                    address_info['City'] = ent.text
            elif ent.label_ == 'LOC':  # If the entity is a location(LOC)
                if address_info['Road'] is None:
                    address_info['Road'] = ent.text
            elif ent.label_ == 'CARDINAL':  # If entity is a numerical value(CARDINAL)
                if address_info['Postcode'] is None:
                    address_info['Postcode'] = ent.text
                elif address_info['Road Numbers'] is None:
                    address_info['Road Numbers'] = ent.text

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

