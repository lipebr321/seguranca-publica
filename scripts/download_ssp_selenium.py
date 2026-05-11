from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

options = webdriver.ChromeOptions()

options.binary_location = "/usr/bin/chromium-browser"

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")

driver = webdriver.Chrome(
    service=service,
    options=options
)

url = "https://www.ssp.sp.gov.br/estatistica/consultas"

print("Abrindo SSP-SP...")

driver.get(url)

time.sleep(5)

print("Título:")
print(driver.title)

print("\nLinks encontrados:\n")

links = driver.find_elements(By.TAG_NAME, "a")

for link in links:

    href = link.get_attribute("href")

    if href:
        if (
            ".xls" in href or
            ".xlsx" in href or
            ".csv" in href
        ):
            print(href)

driver.quit()
