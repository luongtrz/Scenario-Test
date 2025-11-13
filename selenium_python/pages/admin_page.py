import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AdminPage:
    def __init__(self, driver, admin_url=None):
        self.driver = driver
        self.admin_url = admin_url or os.getenv("BAGISTO_ADMIN_URL", "https://commerce.bagisto.com/admin")

    def login_with_credentials(self, email, password):
        print("Logging in to admin...")
        self.driver.get(self.admin_url)
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.NAME, "email")))
        self.driver.find_element(By.NAME, "email").send_keys(email)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.XPATH, "//button[contains(.,'Sign In')]").click()
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("  ✓ Admin logged in")

    def search_product(self, term):
        """Use Mega Search to find product."""
        print(f"Searching product: {term}")
        try:
            search_box = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='Mega Search']"))
            )
            search_box.clear()
            search_box.send_keys(term)
            search_box.submit()
            time.sleep(3)
        except Exception as e:
            print("⚠ Search box not found", e)

    def open_product_from_results(self, term):
        """Click first product link from search results."""
        try:
            link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, term.split(" ")[0]))
            )
            link.click()
            time.sleep(3)
            print("✓ Product edit page opened")
        except Exception:
            print("⚠ Product link not found")

    def set_stock(self, qty):
        """Set stock quantity if input is found."""
        print(f"Setting stock = {qty}")
        inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[name*="inventories"][type="number"]')
        if not inputs:
            print("⚠ Stock input not found")
            return
        inp = inputs[0]
        inp.clear()
        inp.send_keys(str(qty))
        try:
            btn = self.driver.find_element(By.XPATH, "//button[contains(.,'Save Product')]")
            btn.click()
            print("✓ Stock saved")
        except Exception:
            print("⚠ Save button not found")
        time.sleep(3)

    def restore_stock(self, term, qty=200):
        """Search and restore stock quantity."""
        print(f"Restoring {term} stock = {qty}")
        self.search_product(term)
        self.open_product_from_results(term)
        self.set_stock(qty)
