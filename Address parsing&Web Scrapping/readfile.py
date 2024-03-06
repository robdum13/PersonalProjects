import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


df = pd.read_parquet('list_of_company_websites.snappy.parquet')

for domain in df['domain']:
    print(domain)


#Code for reading the parquet file.
