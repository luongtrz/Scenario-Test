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
    
    print("Starting Selenium WebDriver...")
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    wait = WebDriverWait(driver, 20)
    
    try:
        print("Step 1: Navigating to PrestaShop demo...")
        driver.get("https://demo.prestashop.com/")
        time.sleep(2)
        
        print("Step 2: Switching to storefront iframe...")
        iframe = wait.until(EC.presence_of_element_located((By.ID, "framelive")))
        driver.switch_to.frame(iframe)
        
        print("Step 3: Locating product on homepage...")
        first_product = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".product article .thumbnail"))
        )
        
        print("Step 4: Opening product details...")
        first_product.click()
        time.sleep(1)
        
        print("Step 5: Adding product to cart...")
        add_to_cart_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-button-action='add-to-cart']"))
        )
        add_to_cart_btn.click()
        
        print("Step 6: Proceeding to checkout from modal...")
        proceed_checkout_modal = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".cart-content-btn .btn-primary"))
        )
        proceed_checkout_modal.click()
        time.sleep(2)
        
        print("Step 7: Confirming cart and proceeding to checkout...")
        proceed_checkout_cart = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".checkout a.btn-primary"))
        )
        proceed_checkout_cart.click()
        time.sleep(2)
        
        print("Step 8-9: Filling in customer details...")
        
        try:
            social_title = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='id_gender'][value='1']"))
            )
            driver.execute_script("arguments[0].click();", social_title)
        except:
            print("  Social title not required or not found")
        
        first_name = wait.until(EC.presence_of_element_located((By.NAME, "firstname")))
        first_name.clear()
        first_name.send_keys("John")
        
        last_name = driver.find_element(By.NAME, "lastname")
        last_name.clear()
        last_name.send_keys("Doe")
        
        email = driver.find_element(By.NAME, "email")
        email.clear()
        email.send_keys("john.doe.test@automation.com")
        
        try:
            password = driver.find_element(By.NAME, "password")
            password.clear()
            password.send_keys("TestPassword123!")
        except:
            print("  Password field not required (true guest checkout)")
        
        try:
            privacy_checkbox = driver.find_element(By.NAME, "psgdpr")
            if not privacy_checkbox.is_selected():
                driver.execute_script("arguments[0].click();", privacy_checkbox)
        except:
            print("  Privacy checkbox not found")
        
        address1 = driver.find_element(By.NAME, "address1")
        address1.clear()
        address1.send_keys("123 Test Street")
        
        postcode = driver.find_element(By.NAME, "postcode")
        postcode.clear()
        postcode.send_keys("10001")
        
        city = driver.find_element(By.NAME, "city")
        city.clear()
        city.send_keys("New York")
        
        print("Step 10: Continuing to shipping method...")
        continue_btn = wait.until(
            EC.element_to_be_clickable((By.NAME, "continue"))
        )
        continue_btn.click()
        time.sleep(2)
        
        print("Step 11: Confirming shipping method...")
        
        print("Step 12: Continuing to payment method...")
        continue_shipping_btn = wait.until(
            EC.element_to_be_clickable((By.NAME, "confirmDeliveryOption"))
        )
        continue_shipping_btn.click()
        time.sleep(2)
        
        print("Step 13: Selecting payment method...")
        payment_option = wait.until(
            EC.element_to_be_clickable((By.ID, "payment-option-1"))
        )
        driver.execute_script("arguments[0].click();", payment_option)
        time.sleep(1)
        
        print("Step 14: Accepting terms and conditions...")
        terms_checkbox = wait.until(
            EC.element_to_be_clickable((By.ID, "conditions_to_approve[terms-and-conditions]"))
        )
        driver.execute_script("arguments[0].click();", terms_checkbox)
        
        print("Step 15: Placing order...")
        place_order_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ps-shown-by-js button[type='submit']"))
        )
        place_order_btn.click()
        time.sleep(3)
        
        print("Step 16: Verifying order confirmation...")
        confirmation_text = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content-hook_order_confirmation h3"))
        ).text
        
        print(f"  Confirmation message: {confirmation_text}")
        
        order_reference = driver.find_element(By.CSS_SELECTOR, "#order-details ul li").text
        print(f"  Order details: {order_reference}")
        
        assert "confirm" in confirmation_text.lower() or "thank" in confirmation_text.lower(), \
            "Order confirmation message not found!"
        
        print("\nSELENIUM: Order placed successfully!")
        
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        driver.save_screenshot("selenium_failure.png")
        print("Screenshot saved as 'selenium_failure.png'")
        raise
        
    finally:
        print("\nCleaning up...")
        time.sleep(2)
        driver.quit()


if __name__ == "__main__":
    test_guest_checkout_e2e()
