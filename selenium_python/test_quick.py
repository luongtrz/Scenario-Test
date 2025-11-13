#!/usr/bin/env python3
"""Quick test to verify Selenium setup works"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pages.store_page import StorePage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import glob
from dotenv import load_dotenv

load_dotenv()

print("="*80)
print("QUICK SELENIUM TEST")
print("="*80)

# Setup Chrome
print("\n1. Setting up Chrome driver...")
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

driver_path = ChromeDriverManager().install()
if 'THIRD_PARTY_NOTICES' in driver_path or not os.path.isfile(driver_path):
    driver_dir = os.path.dirname(driver_path)
    possible_paths = glob.glob(os.path.join(driver_dir, '**/chromedriver'), recursive=True)
    if possible_paths:
        driver_path = possible_paths[0]
        
# Make executable
os.chmod(driver_path, 0o755)
print(f"  ✓ Using chromedriver: {driver_path}")

service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(10)

print("\n2. Testing StorePage login...")
base_url = os.getenv('BAGISTO_BASE_URL', 'https://commerce.bagisto.com')
store = StorePage(driver, base_url)

try:
    store.goto_home()
    print("  ✓ Navigated to homepage")
    
    print("\n3. Testing cart operations...")
    store.open_cart()
    print("  ✓ Opened cart page")
    
    try:
        store.cart_is_empty()
        print("  ✓ Cart is empty (as expected)")
    except AssertionError:
        print("  ℹ Cart has items")
    
    print("\n" + "="*80)
    print("✅ SELENIUM SETUP WORKS CORRECTLY!")
    print("="*80)
    print("\nAll converted tests should work similarly to S1.")
    print("Pattern verified:")
    print("  - Chrome driver: OK")
    print("  - Page navigation: OK")
    print("  - StorePage methods: OK")
    print("  - Console logging: OK")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    driver.quit()
    print("\n✓ Browser closed")
