import requests
from bs4 import BeautifulSoup

# Make a GET request to the URL you want to scrape
url = "https://www.address.com"
response = requests.get(url)

# Parse the HTML content of the page with BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find the element(s) you want to extract data from
title = soup.find("title").get_text()
paragraphs = [p.get_text() for p in soup.find_all("p")]

# Print the extracted data
print("Title:", title)
print("Paragraphs:")
for p in paragraphs:
    print("-", p)
