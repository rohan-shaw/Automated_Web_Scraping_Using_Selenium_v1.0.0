# Import the required modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService 

# Create a folder to store the scraped data
folder_name = "scraped_data"
if not os.path.exists(folder_name):
    os.mkdir(folder_name)

# Get the site url from the user
site_url = input("Enter the site url: ")

# instantiate options 
options = webdriver.ChromeOptions()

# options.add_argument('--headless')

options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


driver = webdriver.Chrome(options=options)


# Define a function to get all the urls of the site that have the same domain or subdomain
def get_site_urls(site_url):
    # Get the domain name of the site
    domain = site_url.split("//")[-1].split("/")[0]
    # Create a set to store the urls
    site_urls = set()
    # Add the site url to the set
    site_urls.add(site_url)
    # Create a queue to store the urls to be visited
    queue = [site_url]
    # Loop until the queue is empty
    while queue:
        # Get the first url from the queue
        current_url = queue.pop(0)
        # Try to get the response from the url
        try:
            response = requests.get(current_url)
        except:
            # If there is an error, skip this url and continue
            continue
        # Parse the response using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        # Find all the links in the response
        links = soup.find_all("a")
        # Loop through each link
        for link in links:
            # Get the href attribute of the link
            href = link.get("href")
            # If the href is not None and starts with http or https
            if href and href.startswith("http"):
                # If the href contains the domain name of the site
                if domain in href:
                    # If the href is not already in the set of urls
                    if href not in site_urls:
                        # Add it to the set and the queue
                        site_urls.add(href)
                        queue.append(href)
    # Return the set of urls
    return site_urls

# Call the function to get all the urls of the site
site_urls = get_site_urls(site_url)

# Define a function to scrape all the texts from a given url and save it in a txt file
def scrape_and_save(url):
    # Try to load the url using webdriver and wait for 10 seconds for it to load completely
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
    except:
        # If there is an error, skip this url and return
        return
    # Get all the text elements from the page using webdriver
    texts = driver.find_elements_by_xpath("//body//*[not(self::script or self::style)]/text()")
    # Join all the texts into a single string with newlines between them
    text_content = "\n".join([text.strip() for text in texts if text.strip()])
    # Get the file name from the url by removing everything before and including the domain name and replacing / with _
    file_name = url.split(domain)[-1].replace("/", "_")
    # If the file name is empty, use index as file name
    if not file_name:
        file_name = "index"
    # Add .txt extension to the file name
    file_name += ".txt"
    # Create a file path by joining the folder name and file name
    file_path = os.path.join(folder_name, file_name)
    # Open a file in write mode and write the text content to it
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text_content)

# Loop through each url in the site urls set and call the scrape and save function on it
for url in site_urls:
    scrape_and_save(url)

# Close the webdriver instance
driver.close()
