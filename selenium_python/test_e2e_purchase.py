"""
TC-E2E-001: Guest Checkout - Happy Path (Selenium Python)
PrestaShop Demo - End-to-End Purchase Test

Author: QA Automation Team
Date: 2025-11-08
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def test_guest_checkout_e2e():
    """
    Test Case: TC-E2E-001
    Verify guest user can complete end-to-end purchase successfully
    """
    
    # Setup WebDriver with Chrome
    print("🚀 Starting Selenium WebDriver...")
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    wait = WebDriverWait(driver, 20)
    
    try:
        # Step 1: Navigate to PrestaShop demo
        print("📍 Step 1: Navigating to PrestaShop demo...")
        driver.get("https://demo.prestashop.com/")
        time.sleep(2)
        
        # Step 2: Switch to storefront iframe
        print("📍 Step 2: Switching to storefront iframe...")
        iframe = wait.until(EC.presence_of_element_located((By.ID, "framelive")))
        driver.switch_to.frame(iframe)
        print("   ✓ Switched to iframe successfully")
        
        # Step 3: Wait for homepage to load and find first product
        print("📍 Step 3: Locating product on homepage...")
        first_product = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".product article .thumbnail"))
        )
        
        # Step 4: Click on product to view details
        print("📍 Step 4: Opening product details...")
        first_product.click()
        time.sleep(1)
        
        # Step 5: Add product to cart
        print("📍 Step 5: Adding product to cart...")
        add_to_cart_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-button-action='add-to-cart']"))
        )
        add_to_cart_btn.click()
        print("   ✓ Product added to cart")
        
        # Step 6: Proceed to checkout from modal
        print("📍 Step 6: Proceeding to checkout from modal...")
        proceed_checkout_modal = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".cart-content-btn .btn-primary"))
        )
        proceed_checkout_modal.click()
        time.sleep(2)
        
        # Step 7: Proceed to checkout from cart page
        print("📍 Step 7: Confirming cart and proceeding to checkout...")
        proceed_checkout_cart = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".checkout a.btn-primary"))
        )
        proceed_checkout_cart.click()
        time.sleep(2)
        
        # Step 8-9: Fill in personal information
        print("📍 Step 8-9: Filling in customer details...")
        
        # Select "Mr." social title (radio button)
        try:
            social_title = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='id_gender'][value='1']"))
            )
            driver.execute_script("arguments[0].click();", social_title)
        except:
            print("   ⚠ Social title not required or not found")
        
        # First name
        first_name = wait.until(EC.presence_of_element_located((By.NAME, "firstname")))
        first_name.clear()
        first_name.send_keys("John")
        
        # Last name
        last_name = driver.find_element(By.NAME, "lastname")
        last_name.clear()
        last_name.send_keys("Doe")
        
        # Email
        email = driver.find_element(By.NAME, "email")
        email.clear()
        email.send_keys("john.doe.test@automation.com")
        
        # Password (if guest checkout requires it)
        try:
            password = driver.find_element(By.NAME, "password")
            password.clear()
            password.send_keys("TestPassword123!")
        except:
            print("   ℹ Password field not required (true guest checkout)")
        
        # Check "Customer data privacy" if present
        try:
            privacy_checkbox = driver.find_element(By.NAME, "psgdpr")
            if not privacy_checkbox.is_selected():
                driver.execute_script("arguments[0].click();", privacy_checkbox)
        except:
            print("   ℹ Privacy checkbox not found")
        
        # Address
        address1 = driver.find_element(By.NAME, "address1")
        address1.clear()
        address1.send_keys("123 Test Street")
        
        # Postal code
        postcode = driver.find_element(By.NAME, "postcode")
        postcode.clear()
        postcode.send_keys("10001")
        
        # City
        city = driver.find_element(By.NAME, "city")
        city.clear()
        city.send_keys("New York")
        
        print("   ✓ Customer details filled")
        
        # Step 10: Continue to shipping
        print("📍 Step 10: Continuing to shipping method...")
        continue_btn = wait.until(
            EC.element_to_be_clickable((By.NAME, "continue"))
        )
        continue_btn.click()
        time.sleep(2)
        
        # Step 11: Select shipping method (usually auto-selected)
        print("📍 Step 11: Confirming shipping method...")
        # Shipping is typically auto-selected; just continue
        
        # Step 12: Continue to payment
        print("📍 Step 12: Continuing to payment method...")
        continue_shipping_btn = wait.until(
            EC.element_to_be_clickable((By.NAME, "confirmDeliveryOption"))
        )
        continue_shipping_btn.click()
        time.sleep(2)
        
        # Step 13: Select payment method (e.g., "Pay by Check")
        print("📍 Step 13: Selecting payment method...")
        payment_option = wait.until(
            EC.element_to_be_clickable((By.ID, "payment-option-1"))
        )
        driver.execute_script("arguments[0].click();", payment_option)
        time.sleep(1)
        
        # Step 14: Accept terms and conditions
        print("📍 Step 14: Accepting terms and conditions...")
        terms_checkbox = wait.until(
            EC.element_to_be_clickable((By.ID, "conditions_to_approve[terms-and-conditions]"))
        )
        driver.execute_script("arguments[0].click();", terms_checkbox)
        print("   ✓ Terms accepted")
        
        # Step 15: Place order
        print("📍 Step 15: Placing order...")
        place_order_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ps-shown-by-js button[type='submit']"))
        )
        place_order_btn.click()
        time.sleep(3)
        
        # Step 16: Verify order confirmation
        print("📍 Step 16: Verifying order confirmation...")
        confirmation_text = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content-hook_order_confirmation h3"))
        ).text
        
        print(f"   ✓ Confirmation message: {confirmation_text}")
        
        # Check for order reference
        order_reference = driver.find_element(By.CSS_SELECTOR, "#order-details ul li").text
        print(f"   ✓ Order details: {order_reference}")
        
        # Final assertion
        assert "confirm" in confirmation_text.lower() or "thank" in confirmation_text.lower(), \
            "Order confirmation message not found!"
        
        print("\n" + "="*60)
        print("✅ Selenium: Order placed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        # Take screenshot on failure
        driver.save_screenshot("selenium_failure.png")
        print("📸 Screenshot saved as 'selenium_failure.png'")
        raise
        
    finally:
        print("\n🧹 Cleaning up...")
        time.sleep(2)
        driver.quit()
        print("✓ Browser closed")


if __name__ == "__main__":
    test_guest_checkout_e2e()
