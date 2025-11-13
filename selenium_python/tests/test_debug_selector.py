"""
Debug Add To Cart button selector
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.store_page import StorePage


class TestDebugSelector:
    def test_check_button_text(self, driver, base_url):
        """Check actual button text on product page"""
        print("\n" + "="*80)
        print("DEBUG: Checking Add To Cart button text")
        print("="*80)
        
        store = StorePage(driver, base_url)
        
        # Login first
        print("\n→ Logging in...")
        store.login()
        print("  ✓ Logged in")
        
        # Go to a known product page
        print("\n→ Navigating to product page...")
        driver.get("https://commerce.bagisto.com/casual-wear-female")
        
        # Wait for products
        wait = WebDriverWait(driver, 10)
        products = wait.until(
            EC.presence_of_all_elements_located((
                By.XPATH,
                "//a[contains(@href, 'commerce.bagisto.com/') and @aria-label and .//img[@alt]]"
            ))
        )
        print(f"  → Found {len(products)} products")
        
        # Click first product
        print("\n→ Clicking first product...")
        first_product = products[0]
        
        # CRITICAL: Use JavaScript click to avoid ChromeDriver crash
        print("  → Using JavaScript click...")
        driver.execute_script("arguments[0].click();", first_product)
        
        # Wait for page load
        wait.until(EC.url_contains("commerce.bagisto.com"))
        driver.implicitly_wait(3)
        
        # Find ALL buttons and print their text
        print("\n→ Finding all buttons on page...")
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"  → Found {len(all_buttons)} buttons total\n")
        
        for idx, btn in enumerate(all_buttons):
            try:
                text = btn.text
                inner_html = btn.get_attribute("innerHTML")
                classes = btn.get_attribute("class")
                
                if "cart" in text.lower() or "cart" in inner_html.lower():
                    print(f"Button #{idx}:")
                    print(f"  Text: '{text}'")
                    print(f"  Text length: {len(text)}")
                    print(f"  Text repr: {repr(text)}")
                    print(f"  Classes: {classes}")
                    print(f"  InnerHTML: {inner_html[:100]}...")
                    print()
            except:
                pass
        
        # Try multiple selector strategies
        print("\n→ Testing selector strategies...")
        
        # Strategy 1: contains text
        try:
            btn1 = driver.find_element(By.XPATH, "//button[contains(text(), 'Add To Cart')]")
            print(f"  ✓ Strategy 1 WORKS: //button[contains(text(), 'Add To Cart')]")
            print(f"    Button text: '{btn1.text}'")
        except Exception as e:
            print(f"  ✗ Strategy 1 FAILED: {type(e).__name__}")
        
        # Strategy 2: exact text
        try:
            btn2 = driver.find_element(By.XPATH, "//button[text()='Add To Cart']")
            print(f"  ✓ Strategy 2 WORKS: //button[text()='Add To Cart']")
            print(f"    Button text: '{btn2.text}'")
        except Exception as e:
            print(f"  ✗ Strategy 2 FAILED: {type(e).__name__}")
        
        # Strategy 3: normalize-space
        try:
            btn3 = driver.find_element(By.XPATH, "//button[normalize-space(text())='Add To Cart']")
            print(f"  ✓ Strategy 3 WORKS: normalize-space")
            print(f"    Button text: '{btn3.text}'")
        except Exception as e:
            print(f"  ✗ Strategy 3 FAILED: {type(e).__name__}")
        
        # Strategy 4: case-insensitive contains
        try:
            btn4 = driver.find_element(By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')]")
            print(f"  ✓ Strategy 4 WORKS: case-insensitive contains")
            print(f"    Button text: '{btn4.text}'")
        except Exception as e:
            print(f"  ✗ Strategy 4 FAILED: {type(e).__name__}")
        
        # Strategy 5: CSS Selector
        try:
            btn5 = driver.find_element(By.CSS_SELECTOR, "button")
            # Find button by checking text in Python
            cart_buttons = [b for b in driver.find_elements(By.TAG_NAME, "button") if "add to cart" in b.text.lower()]
            if cart_buttons:
                print(f"  ✓ Strategy 5 WORKS: CSS + Python filter")
                print(f"    Found {len(cart_buttons)} cart button(s)")
                print(f"    First button text: '{cart_buttons[0].text}'")
            else:
                print(f"  ✗ Strategy 5 FAILED: No buttons with 'add to cart'")
        except Exception as e:
            print(f"  ✗ Strategy 5 FAILED: {type(e).__name__}")
        
        print("\n" + "="*80)
        print("DEBUG COMPLETE - Check output above")
        print("="*80)
