"""
Debug S1 - Check checkout page state when cart has mixed products
"""
import pytest
import time
from selenium.webdriver.common.by import By
from pages.store_page import StorePage


class TestDebugS1Checkout:
    """Debug checkout page to see why shipping/payment not found"""
    
    def test_debug_checkout_page(self, driver, base_url, credentials):
        """Add product and inspect checkout page HTML"""
        
        print("\n" + "="*80)
        print("DEBUG S1 CHECKOUT PAGE")
        print("="*80)
        
        store = StorePage(driver, base_url)
        
        # Login
        print("\nStep 1: Logging in...")
        store.login()
        
        # Add product
        print("\nStep 2: Adding product to cart...")
        store.add_first_product_from_home()
        
        # Go to checkout
        print("\nStep 3: Proceeding to checkout...")
        store.go_checkout()
        
        # Fill address
        print("\nStep 4: Filling shipping address...")
        store.fill_shipping_address_minimal()
        
        # Debug: Check page content
        print("\n" + "="*80)
        print("DEBUGGING CHECKOUT PAGE CONTENT")
        print("="*80)
        
        print(f"\nCurrent URL: {driver.current_url}")
        
        # Check for shipping method inputs
        print("\nChecking for shipping method inputs...")
        shipping_inputs = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="radio"][name="shipping_method"]'
        )
        print(f"  Found {len(shipping_inputs)} shipping method radio inputs")
        
        # Check for payment method inputs
        print("\nChecking for payment method inputs...")
        payment_inputs = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="radio"][name="payment[method]"]'
        )
        print(f"  Found {len(payment_inputs)} payment method radio inputs")
        
        # Check for all labels
        print("\nChecking for all labels on page...")
        all_labels = driver.find_elements(By.TAG_NAME, 'label')
        print(f"  Found {len(all_labels)} total labels")
        
        # Print first 10 label texts
        for i, label in enumerate(all_labels[:10]):
            label_for = label.get_attribute('for') or 'N/A'
            label_text = label.text.strip()[:50] if label.text else ''
            print(f"    Label {i+1}: for='{label_for}' text='{label_text}'")
        
        # Check for Place Order button
        print("\nChecking for Place Order button...")
        place_btns = driver.find_elements(
            By.XPATH,
            "//button[contains(text(), 'Place')]"
        )
        print(f"  Found {len(place_btns)} buttons with 'Place' text")
        
        for i, btn in enumerate(place_btns):
            btn_text = btn.text.strip()
            btn_class = btn.get_attribute('class') or 'N/A'
            print(f"    Button {i+1}: text='{btn_text}' class='{btn_class}'")
        
        # Check page title/heading
        print("\nPage headings:")
        h1_elems = driver.find_elements(By.TAG_NAME, 'h1')
        for h1 in h1_elems:
            print(f"  H1: {h1.text.strip()}")
        
        h2_elems = driver.find_elements(By.TAG_NAME, 'h2')
        for h2 in h2_elems[:5]:
            print(f"  H2: {h2.text.strip()}")
        
        # Scroll down to see if elements are below viewport
        print("\nScrolling to bottom...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Re-check after scroll
        print("\nRe-checking after scroll...")
        shipping_inputs_after = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="radio"][name="shipping_method"]'
        )
        print(f"  Shipping inputs after scroll: {len(shipping_inputs_after)}")
        
        payment_inputs_after = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="radio"][name="payment[method]"]'
        )
        print(f"  Payment inputs after scroll: {len(payment_inputs_after)}")
        
        # Check if there's a "Proceed" button we need to click first
        print("\nChecking for Proceed button...")
        proceed_btns = driver.find_elements(
            By.XPATH,
            "//button[contains(text(), 'Proceed')]"
        )
        print(f"  Found {len(proceed_btns)} Proceed buttons")
        
        if proceed_btns:
            print("  → Clicking Proceed button...")
            proceed_btns[0].click()
            time.sleep(3)
            
            # Re-check inputs after clicking Proceed
            print("\nRe-checking after Proceed...")
            shipping_inputs_final = driver.find_elements(
                By.CSS_SELECTOR,
                'input[type="radio"][name="shipping_method"]'
            )
            print(f"  Shipping inputs: {len(shipping_inputs_final)}")
            
            payment_inputs_final = driver.find_elements(
                By.CSS_SELECTOR,
                'input[type="radio"][name="payment[method]"]'
            )
            print(f"  Payment inputs: {len(payment_inputs_final)}")
            
            place_btns_final = driver.find_elements(
                By.XPATH,
                "//button[contains(text(), 'Place')]"
            )
            print(f"  Place Order buttons: {len(place_btns_final)}")
        
        print("\n" + "="*80)
        print("DEBUG COMPLETE - Check output above")
        print("="*80 + "\n")
        
        # Keep browser open for 10 seconds for manual inspection
        time.sleep(10)
