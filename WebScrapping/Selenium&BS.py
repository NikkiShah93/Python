from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Set up the driver
driver = webdriver.Chrome()
driver.maximize_window()

# Navigate to the page
url = 'https://www.example.com'
driver.get(url)

# Enter a search query and submit the form
search_box = driver.find_element(By.NAME, 'q')
search_box.send_keys('python')
search_box.send_keys(Keys.RETURN)

# Wait for the search results to load
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, 'search-results')))

# Extract information from the search results
soup = BeautifulSoup(driver.page_source, 'html.parser')
results = soup.find_all('div', {'class': 'search-result'})

for result in results:
    title = result.find('h2').text.strip()
    link = result.find('a')['href']
    description = result.find('p').text.strip()
    print(f'Title: {title}')
    print(f'Link: {link}')
    print(f'Description: {description}')
    print()

# Navigate to the next page of search results
next_button = driver.find_element(By.CLASS_NAME, 'next')
next_button.click()

# Wait for the next page of search results to load
wait.until(EC.presence_of_element_located((By.ID, 'search-results')))

# Extract information from the next page of search results
soup = BeautifulSoup(driver.page_source, 'html.parser')
results = soup.find_all('div', {'class': 'search-result'})

for result in results:
    title = result.find('h2').text.strip()
    link = result.find('a')['href']
    description = result.find('p').text.strip()
    print(f'Title: {title}')
    print(f'Link: {link}')
    print(f'Description: {description}')
    print()

# Close the driver
driver.quit()
