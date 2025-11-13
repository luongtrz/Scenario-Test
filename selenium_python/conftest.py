"""
Pytest configuration and fixtures for Bagisto Selenium tests.
"""
import os
import glob
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.fixture(scope="function")
def driver():
    """
    Create and configure WebDriver instance.
    Scope: function - new browser instance for each test.
    """
    browser = os.getenv('BROWSER', 'chrome').lower()
    headless = os.getenv('HEADLESS', 'false').lower() == 'true'
    
    print(f"\n🌐 Starting {browser} browser (headless={headless})...")
    
    if browser == 'chrome':
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        # Ignore HTTPS errors for demo sites
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        
        # Get chromedriver path and fix if needed
        driver_path = ChromeDriverManager().install()
        
        # Fix for webdriver-manager bug: find actual chromedriver binary
        if 'THIRD_PARTY_NOTICES' in driver_path or not os.path.isfile(driver_path):
            # Search for actual chromedriver binary in parent directory
            driver_dir = os.path.dirname(driver_path)
            possible_paths = glob.glob(os.path.join(driver_dir, '**/chromedriver'), recursive=True)
            if possible_paths:
                driver_path = possible_paths[0]
                print(f"  ✓ Found chromedriver at: {driver_path}")
        
        service = ChromeService(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
    elif browser == 'firefox':
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--width=1920')
        options.add_argument('--height=1080')
        # Ignore HTTPS errors
        options.set_preference('accept_insecure_certs', True)
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    
    # Configure timeouts
    implicit_wait = int(os.getenv('IMPLICIT_WAIT', '10'))
    page_load_timeout = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
    
    driver.implicitly_wait(implicit_wait)
    driver.set_page_load_timeout(page_load_timeout)
    
    # Maximize window
    driver.maximize_window()
    
    yield driver
    
    # Cleanup
    print("\n🔚 Closing browser...")
    driver.quit()


@pytest.fixture(scope="session")
def base_url():
    """Get base URL from environment."""
    return os.getenv('BAGISTO_BASE_URL', 'https://commerce.bagisto.com')


@pytest.fixture(scope="session")
def credentials():
    """Get login credentials from environment."""
    return {
        'email': os.getenv('BAGISTO_EMAIL'),
        'password': os.getenv('BAGISTO_PASSWORD')
    }
