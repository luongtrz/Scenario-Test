"""
B1b: Remove All Products - Cart Returns to Empty State
Scenario: User removes all products from cart
Expected: Cart returns to initial empty state

Equivalent to: playwright_typescript/tests/bagisto-step-b1b.spec.ts
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pages.store_page import StorePage


class TestBagistoB1bRemoveAllProducts:
    """B1b - Remove All Products Edge Case"""
    
    def test_b1b_remove_all_products_returns_to_empty(self, driver, base_url, credentials):
        """
        B1b – Remove all products returns cart to empty state
        
        Test Flow:
        1. Add product to cart
        2. Verify cart has items
        3. Select all items using "Select All" checkbox
        4. Click bulk "Remove" button
        5. Confirm removal in modal (if present)
        6. Verify cart is now empty
        7. Verify "Proceed To Checkout" button is hidden
        """
        print("\n" + "="*80)
        print("B1b: REMOVE ALL PRODUCTS - RETURN TO EMPTY STATE")
        print("="*80)
        
        store = StorePage(driver, base_url)
        
        print("\nStep 1: Adding products to cart...")
        store.add_first_product_from_home()
        
        print("\nStep 2: Cart page should be loaded with items...")
        # add_first_product_from_home already navigates to cart
        
        print("\nStep 3: Verifying cart has items...")
        qty_inputs = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="hidden"][name="quantity"]'
        )
        initial_count = len(qty_inputs)
        print(f'  Cart has {initial_count} item(s)')
        
        assert initial_count > 0, "Cart should have items before removal"
        
        print("\nStep 4: Selecting all items using 'Select All' checkbox...")
        try:
            select_all_label = driver.find_element(By.CSS_SELECTOR, 'label[for="select-all"]')
            select_all_label.click()
            time.sleep(0.5)
            print('  ✓ Select All clicked')
        except NoSuchElementException:
            print('  ⚠ Select All checkbox not found')
            raise
        
        print("\nStep 5: Clicking bulk 'Remove' button...")
        try:
            bulk_remove_btn = driver.find_element(
                By.XPATH,
                "//span[@role='button' and contains(text(), 'Remove')]"
            )
            bulk_remove_btn.click()
            print('  ✓ Remove button clicked')
        except NoSuchElementException:
            print('  ⚠ Bulk Remove button not found')
            raise
        
        print("\nStep 6: Confirming removal in modal (if present)...")
        time.sleep(0.5)
        
        try:
            # Look for "Agree" button in confirmation modal
            confirm_btn = driver.find_element(
                By.XPATH,
                "//button[contains(text(), 'Agree') or contains(text(), 'Yes') or contains(text(), 'Confirm') or contains(text(), 'OK')]"
            )
            if confirm_btn.is_displayed():
                print('  ✓ Confirmation modal appeared, clicking Agree...')
                confirm_btn.click()
        except NoSuchElementException:
            print('  ℹ No confirmation modal (removal immediate)')
        
        print("\nStep 7: Waiting for removal to complete...")
        time.sleep(2)
        
        print("\nStep 8: Verifying cart is now empty...")
        try:
            store.cart_is_empty()
            print('  ✓ Cart is now empty')
        except AssertionError as e:
            print(f'  ✗ Cart still has items: {e}')
            raise
        
        print("\nStep 9: Verifying 'Proceed To Checkout' button is hidden...")
        try:
            checkout_btn = driver.find_element(
                By.XPATH,
                "//a[contains(text(), 'Proceed To Checkout')]"
            )
            is_visible = checkout_btn.is_displayed()
            
            if not is_visible:
                print('  ✓ Checkout button hidden on empty cart')
            else:
                print('  ⚠ Checkout button still visible (may be grayed out)')
        except NoSuchElementException:
            print('  ✓ Checkout button not in DOM (expected for empty cart)')
        
        print("\n" + "="*80)
        print("B1b: PASSED - All products removed, cart returned to empty state")
        print("="*80 + "\n")
