from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv('BAGISTO_BASE_URL', 'https://commerce.bagisto.com')
email = os.getenv('BAGISTO_EMAIL', 'john@example.com')
password = os.getenv('BAGISTO_PASSWORD', 'password')

options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-blink-features=AutomationControlled')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()

try:
    # Login
    driver.get(f"{base_url}/customer/login")
    time.sleep(2)
    
    # Dismiss cookie
    try:
        accept_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
        accept_btn.click()
        time.sleep(1)
    except:
        pass
    
    # Login
    driver.find_element(By.NAME, 'email').send_keys(email)
    driver.find_element(By.NAME, 'password').send_keys(password)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]").click()
    time.sleep(3)
    
    # Go to cart
    driver.get(f"{base_url}/checkout/cart")
    time.sleep(3)
    
    # Find all links
    all_links = driver.find_elements(By.TAG_NAME, 'a')
    print(f"\n=== FOUND {len(all_links)} LINKS IN CART ===\n")
    
    product_links = []
    for i, link in enumerate(all_links):
        href = link.get_attribute('href') or ''
        text = link.text.strip()
        
        if '/product/' in href:
            product_links.append((href, text))
            print(f"{i}. PRODUCT LINK:")
            print(f"   Href: {href}")
            print(f"   Text: {text}")
            print()
    
    print(f"\n=== TOTAL PRODUCT LINKS: {len(product_links)} ===\n")
    
finally:
    input("Press Enter to close...")
    driver.quit()
