from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import csv

# Set up Chrome options and the Selenium WebDriver
options = Options()
ua = UserAgent()
user_agent = ua.random
options.add_argument(f'user-agent={user_agent}')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get('https://store.playstation.com/en-gb/category/c19f9772-9dfb-41c5-a337-a7b9c8f86f08/1?FULL_GAME=storeDisplayClassification&GAME_BUNDLE=storeDisplayClassification&')
time.sleep(10)  # Wait for the page to load

# Initialize the lists to store game names and prices
game_names = []
prices = []
game_images = []
game_urls = []
page = 1

while True:
    time.sleep(5)  # Allow time for the page to load
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    results = soup.find_all("div", {"class": "psw-product-tile psw-interactive-root"})

    # Loop through all results on the current page
    for result in results:
        game_name_element = result.find("span", {"data-qa": lambda x: x and 'product-name' in x})
        price_element = result.find("span", {"data-qa": lambda x: x and 'display-price' in x})
        game_image_element = result.find("img", {"data-qa": lambda x: x and 'game-art#image#image' in x})
        game_url_element = result.find_parent("a", {"class": "psw-link psw-content-link"})  # Check parent anchor for URL

        game_name = game_name_element.get_text().strip() if game_name_element else "Name not found"
        price = price_element.get_text().strip() if price_element else "Price not available"
        game_image = game_image_element['src'] if game_image_element else "Image not available"

        # Check if URL element is found
        if game_url_element:
            game_url = f"https://store.playstation.com{game_url_element['href']}"
        else:
            game_url = "URL not available"

        game_names.append(game_name)
        prices.append(price)
        game_images.append(game_image)
        game_urls.append(game_url)

    print(f"Collected {len(results)} games from page {page}")

    # Navigate to the next page
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "button.psw-button.psw-quick-action-button[aria-label='Go to next page']")
        driver.execute_script("arguments[0].click();", next_button)
        print("Clicked the next button, moving to the next page...")
        page += 1
        time.sleep(5)  # Allow time for the next page to load
        if page > 5:  # Limit to 5 pages
            break
    except Exception as e:
        print("No more pages to scrape or an error occurred:", str(e))
        break

# Print collected game names and prices
for name, price, image, url in zip(game_names, prices, game_images, game_urls):
    print(f"Game: {name}, Price: {price}, Image : {image}, URL : {url}")


# Close the driver
driver.quit()

# Write all collected game names, prices, and images to the CSV file
with open('ps5games.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Game', 'Price', 'Image', 'URL'])  # the header

    # Write each game's data to the CSV
    for name, price, image, url in zip(game_names, prices, game_images, game_urls):
        writer.writerow([name, price, image, url])

print("Data saved to ps5games.csv successfully.")