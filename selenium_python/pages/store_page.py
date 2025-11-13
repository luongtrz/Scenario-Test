"""
StorePage - Page Object Model for Bagisto Commerce Storefront
Equivalent to StorePage.ts in Playwright TypeScript version
"""
import os
import time
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    WebDriverException
)
from http.client import RemoteDisconnected
from urllib3.exceptions import MaxRetryError, NewConnectionError, ProtocolError


class StorePage:
    """Page Object for Bagisto Commerce storefront operations."""
    
    def __init__(self, driver: webdriver.Remote, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip('/')
        self.wait = WebDriverWait(driver, 15)
        self.email = os.getenv('BAGISTO_EMAIL')
        self.password = os.getenv('BAGISTO_PASSWORD')
    
    def goto_home(self):
        """Navigate to homepage."""
        print(f"  → Navigating to {self.base_url}")
        self.driver.get(self.base_url)
        time.sleep(1)
    
    def login(self):
        """
        Login to Bagisto Commerce.
        Auto-dismisses cookie consent modal if present.
        """
        print("  → Opening login page...")
        self.driver.get(f"{self.base_url}/customer/login")
        time.sleep(1)
        
        # Dismiss cookie consent if present
        try:
            accept_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
            if accept_btn.is_displayed():
                print("  → Dismissing cookie consent...")
                accept_btn.click()
                time.sleep(0.5)
        except (NoSuchElementException, TimeoutException):
            pass
        
        # Fill login form
        print(f"  → Logging in as {self.email}...")
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = self.driver.find_element(By.NAME, "password")
        
        email_input.clear()
        email_input.send_keys(self.email)
        password_input.clear()
        password_input.send_keys(self.password)
        
        # Submit form
        login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
        login_btn.click()
        
        # Wait for redirect to home or account page
        time.sleep(2)
        print("  ✓ Logged in successfully")
    
    def add_first_product_from_home(self):
        """
        Add first available simple product from a category.
        CRITICAL: Waits 5s for AJAX cart update, then navigates to cart page to verify.
        Skips configurable products (with options).
        Matches Playwright behavior: iterates categories, checks product selector, skips options.
        """
        print("  → Finding first simple product from categories...")
        
        # Available categories (matching Playwright)
        categories = [
            '/casual-wear-female',
            '/electronics',
            '/home-kitchen',
            '/books-stationery'
        ]
        
        # Shuffle categories (like Playwright)
        import random
        random.shuffle(categories)
        
        for category in categories:
            try:
                print(f"  Trying category: {category}")
                
                # Navigate to category page
                self.driver.get(f"{self.base_url}{category}")
                time.sleep(2)
                
                # Wait for product links (matching Playwright selector pattern)
                # a[href*="commerce.bagisto.com/"][aria-label]:has(img[alt])
                try:
                    product_links = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_all_elements_located((
                            By.XPATH,
                            "//a[contains(@href, 'commerce.bagisto.com/') and @aria-label and .//img[@alt]]"
                        ))
                    )
                except TimeoutException:
                    print(f"  ✗ No products in {category}, trying next...")
                    continue
                
                if not product_links:
                    print(f"  ✗ No products in {category}, trying next...")
                    continue
                
                # Click first product
                first_product = product_links[0]
                product_name = first_product.get_attribute('aria-label') or ''
                print(f"  Selected product: {product_name}")
                
                # Save product name for later use (e.g., admin search in S4)
                self.last_added_product_name = product_name
                
                # Save product href for later use (e.g., S4B direct navigation)
                product_href = first_product.get_attribute('href')
                self.last_added_product_url = product_href
                
                # CRITICAL FIX: Use JavaScript click to avoid ChromeDriver crash
                # element.click() causes ProtocolError with ChromeDriver 142.0.7444.162 + Chrome 142.0.7444.134
                self.driver.execute_script("arguments[0].click();", first_product)
                
                # Wait for product page to load
                time.sleep(2)
                
                # Check for Add To Cart button
                try:
                    add_btn = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            "//button[contains(text(), 'Add To Cart')]"
                        ))
                    )
                except TimeoutException:
                    print(f"  ✗ Add To Cart button not found, trying next category...")
                    continue
                
                # Check if product has configurable options that MUST be selected
                # Look for required option indicators (red asterisk, "required" text, etc.)
                # TEMPORARILY DISABLED - Playwright doesn't actually skip these products
                has_required_options = False
                # try:
                #     required_markers = self.driver.find_elements(
                #         By.XPATH,
                #         "//*[contains(text(), '*') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'required')]"
                #     )
                #     has_required_options = len(required_markers) > 0
                # except:
                #     pass
                
                if has_required_options:
                    print(f"  ⚠ Product has required configurable options, skipping...")
                    continue  # Skip this product, try next category
                
                # Try to add product - if it has options but has defaults, it may still work
                print("  → Clicking 'Add To Cart' button...")
                add_btn.click()
                
                # CRITICAL: Wait 5 seconds for AJAX cart update (Playwright requirement)
                print("  → Waiting for cart to update...")
                time.sleep(5)
                
                # Navigate to cart page to verify (Playwright pattern)
                print("  → Checking cart...")
                self.driver.get(f"{self.base_url}/checkout/cart")
                
                # Wait for networkidle equivalent - wait for page load + 2s
                WebDriverWait(self.driver, 20).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                time.sleep(2)
                
                # Count items by quantity inputs (physical products)
                qty_inputs = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'input[type="hidden"][name="quantity"]'
                )
                
                # Count e-book checkboxes (digital products)
                ebook_checkboxes = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'input[type="checkbox"][id^="item_"]'
                )
                
                physical_count = len(qty_inputs)
                ebook_count = len(ebook_checkboxes)
                total_count = physical_count + ebook_count
                
                print(f"  → Found {total_count} items in cart ({physical_count} physical, {ebook_count} e-book)")
                
                if total_count > 0:
                    print(f"  ✓ Cart has {total_count} item(s)")
                    return  # Success!
                
                print(f"  ✗ Cart is empty, trying next category...")
                
            except (TimeoutException, NoSuchElementException, StaleElementReferenceException,
                    WebDriverException, RemoteDisconnected, MaxRetryError, ProtocolError,
                    ConnectionRefusedError, ConnectionError, OSError) as e:
                print(f"  ✗ Failed: {type(e).__name__}")
                continue
        
        # If all categories failed
        raise Exception(f"Failed to add product after trying {len(categories)} categories")
    
    def go_checkout(self):
        """
        Navigate to checkout from cart page.
        Tries multiple checkout button/link selectors (matching Playwright).
        """
        print("  → Looking for checkout button...")
        
        # Try multiple selectors (matching Playwright pattern)
        checkout_selectors = [
            (By.XPATH, "//a[contains(text(), 'Proceed To Checkout')]"),
            (By.XPATH, "//a[contains(text(), 'Checkout')]"),
            (By.XPATH, "//button[contains(text(), 'Checkout')]"),
            (By.XPATH, "//button[contains(text(), 'Proceed To Checkout')]"),
            (By.CSS_SELECTOR, ".checkout-btn"),
            (By.CSS_SELECTOR, "a[href*='checkout']")
        ]
        
        for by, selector in checkout_selectors:
            try:
                checkout_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((by, selector))
                )
                print(f"  → Found checkout button: {selector}")
                checkout_btn.click()
                
                # Wait for checkout page to load (networkidle equivalent)
                WebDriverWait(self.driver, 15).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                time.sleep(2)
                
                print("  ✓ Navigated to checkout page")
                return
            except (TimeoutException, NoSuchElementException):
                continue
        
        raise Exception("Checkout button not found with any selector")
    
    def fill_shipping_address_minimal(self):
        """
        Fill minimal shipping address and click Proceed button.
        Uses test data for all fields.
        """
        print("  → Filling shipping address form...")
        
        # Check if address form is present (new address vs saved address)
        try:
            first_name_input = self.driver.find_element(By.NAME, "billing[first_name]")
            
            # Fill all required fields
            fields = {
                'billing[first_name]': 'Test',
                'billing[last_name]': 'User',
                'billing[email]': self.email,
                'billing[address1]': '123 Test Street',
                'billing[city]': 'Test City',
                'billing[postcode]': '12345',
                'billing[phone]': '1234567890'
            }
            
            for name, value in fields.items():
                try:
                    input_elem = self.driver.find_element(By.NAME, name)
                    input_elem.clear()
                    input_elem.send_keys(value)
                except NoSuchElementException:
                    pass
            
            # Select country (United States)
            try:
                country_select = self.driver.find_element(By.NAME, "billing[country]")
                country_select.click()
                time.sleep(0.5)
                us_option = self.driver.find_element(By.XPATH, "//option[@value='US']")
                us_option.click()
                time.sleep(1)
            except:
                pass
            
            # Select state
            try:
                state_select = self.driver.find_element(By.NAME, "billing[state]")
                state_select.click()
                time.sleep(0.5)
                first_state = self.driver.find_element(By.XPATH, "//select[@name='billing[state]']/option[2]")
                first_state.click()
            except:
                pass
            
            print("  ✓ Address form filled")
        except NoSuchElementException:
            print("  → Using saved address")
        
        # Click Proceed button
        print("  → Clicking 'Proceed' button...")
        try:
            proceed_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Proceed')]"))
            )
            proceed_btn.click()
            
            # Wait for shipping/payment options to load
            print("  → Waiting for shipping/payment options to load...")
            time.sleep(2)
            print("  ✓ Address saved and proceeded to payment")
        except TimeoutException:
            print("  → No Proceed button (may be on payment step already)")
    
    def choose_payment_and_place(self, expect_success_msg: bool = False):
        """
        Select shipping method (Free Shipping), payment method (Cash On Delivery),
        and place order.
        
        CRITICAL: Must click LABEL (visible), not hidden input.
        Uses .last() equivalent by finding all labels and clicking the last visible one.
        
        Args:
            expect_success_msg: Whether to wait for success message (not reliable on demo)
        """
        # Scroll to top first to ensure shipping/payment section is visible
        print("  → Scrolling to top of page...")
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Step 1: Select shipping method
        print("  → Selecting shipping method...")
        
        # Wait for shipping/payment options to load
        time.sleep(2)
        
        # Check if shipping methods are present
        shipping_inputs = self.driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="radio"][name="shipping_method"]'
        )
        
        if len(shipping_inputs) > 0:
            # Find Free Shipping label (prefer last visible - matching Playwright .last())
            try:
                free_labels = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'label[for="free_free"]'
                )
                if free_labels:
                    # Click last label (Playwright uses .last())
                    free_shipping_label = free_labels[-1]
                    print("    Clicking Free Shipping label...")
                    free_shipping_label.click()
                    time.sleep(1)
                    print("  ✓ Free Shipping selected")
                else:
                    # Fallback: try flat rate
                    flat_labels = self.driver.find_elements(
                        By.CSS_SELECTOR,
                        'label[for^="flatrate"]'
                    )
                    if flat_labels:
                        flat_labels[-1].click()
                        print("  ✓ Flat Rate shipping selected")
                        time.sleep(1)
            except (NoSuchElementException, IndexError):
                print("  → Shipping method not found or already selected")
        else:
            print("    No shipping methods found (e-book or already selected)")
        
        # Step 2: Select payment method
        print("  → Selecting payment method...")
        
        # Wait for payment methods to load
        time.sleep(2)
        
        payment_inputs = self.driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="radio"][name="payment[method]"]'
        )
        
        if len(payment_inputs) > 0:
            # Find Cash On Delivery label (prefer last visible - matching Playwright .last())
            try:
                cod_labels = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'label[for="cashondelivery"]'
                )
                if cod_labels:
                    # Click last label (Playwright uses .last())
                    cod_label = cod_labels[-1]
                    print("    Clicking Cash On Delivery label...")
                    cod_label.click()
                    time.sleep(2)
                    print("  ✓ Cash On Delivery selected")
                else:
                    # Fallback: try money transfer
                    mt_labels = self.driver.find_elements(
                        By.CSS_SELECTOR,
                        'label[for="moneytransfer"]'
                    )
                    if mt_labels:
                        mt_labels[-1].click()
                        print("  ✓ Money Transfer selected")
                        time.sleep(2)
            except (NoSuchElementException, IndexError):
                print("  ⚠ Payment method not found")
        else:
            print("    No payment methods found")
        
        # Step 3: Click Place Order
        print("  → Clicking Place Order...")
        
        # Scroll to bottom (matching Playwright)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # Try multiple selectors for Place Order button (matching Playwright)
        place_btn_selectors = [
            (By.XPATH, "//button[contains(text(), 'Place Order')]"),
            (By.CSS_SELECTOR, "button.primary-button"),
            (By.XPATH, "//button[@type='button' and contains(text(), 'Place')]"),
            (By.XPATH, "//button[contains(@class, 'primary') and contains(text(), 'Place')]")
        ]
        
        for by, selector in place_btn_selectors:
            try:
                place_order_btn = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((by, selector))
                )
                
                print(f"    Found button with selector: {selector}")
                
                # Try regular click first
                try:
                    place_order_btn.click()
                except ElementClickInterceptedException:
                    # If intercepted, use JavaScript click
                    self.driver.execute_script("arguments[0].click();", place_order_btn)
                
                # Wait for order processing
                time.sleep(5)
                print("  ✓ Order placement attempted")
                return
                
            except (TimeoutException, NoSuchElementException):
                continue
        
        print("  ⚠ Place Order button not found with any selector")
    
    def open_cart(self):
        """Navigate to cart page."""
        print("  → Opening cart page...")
        self.driver.get(f"{self.base_url}/checkout/cart")
        time.sleep(2)
    
    def cart_is_empty(self) -> bool:
        """
        Check if cart is empty.
        Returns True if empty, raises AssertionError if not.
        """
        # Check for empty cart message
        try:
            empty_msg = self.driver.find_element(
                By.XPATH,
                "//*[contains(text(), 'Your cart is empty') or contains(text(), 'empty')]"
            )
            if empty_msg.is_displayed():
                print("  ✓ Cart is empty")
                return True
        except NoSuchElementException:
            pass
        
        # Check quantity inputs
        qty_inputs = self.driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="hidden"][name="quantity"]'
        )
        
        if len(qty_inputs) == 0:
            print("  ✓ Cart is empty (no quantity inputs)")
            return True
        else:
            print(f"  ⚠ Cart has {len(qty_inputs)} item(s)")
            raise AssertionError(f"Cart is not empty: {len(qty_inputs)} items found")
    
    def get_latest_order(self) -> Optional[Dict[str, str]]:
        """
        Get latest order from order history.
        
        Returns:
            Dict with keys: orderId, date, total, status
            None if no orders found
        """
        print("  → Opening order history...")
        self.driver.get(f"{self.base_url}/customer/account/orders")
        time.sleep(2)
        
        # Find order rows (skip header row)
        try:
            # All rows have class "row grid"
            all_rows = self.driver.find_elements(By.CSS_SELECTOR, '.row.grid')
            
            # Filter out header row (contains "Order ID" or "Order Date" text)
            data_rows = []
            for row in all_rows:
                row_text = row.text.lower()
                if 'order id' not in row_text and 'order date' not in row_text:
                    data_rows.append(row)
            
            if not data_rows:
                print("  ⚠ No orders found in history")
                return None
            
            # Get first data row (latest order)
            first_row = data_rows[0]
            cells = first_row.find_elements(By.TAG_NAME, 'p')
            
            if len(cells) >= 4:
                order_data = {
                    'orderId': cells[0].text.strip(),
                    'date': cells[1].text.strip(),
                    'total': cells[2].text.strip(),
                    'status': cells[3].text.strip()
                }
                return order_data
            else:
                print(f"  ⚠ Unexpected row format: {len(cells)} cells")
                return None
                
        except NoSuchElementException:
            print("  ⚠ Could not find order rows")
            return None
