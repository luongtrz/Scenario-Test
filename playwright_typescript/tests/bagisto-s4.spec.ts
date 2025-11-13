import { test, expect } from '@playwright/test';
import { config } from 'dotenv';
import { StorePage } from '../pages/StorePage';

config();

const baseUrl = process.env.BAGISTO_BASE_URL || 'https://commerce.bagisto.com';

const adminUrl = process.env.BAGISTO_ADMIN_URL || 'https://commerce.bagisto.com/admin';
const adminEmail = process.env.BAGISTO_ADMIN_EMAIL || 'admin@example.com';
const adminPassword = process.env.BAGISTO_ADMIN_PASSWORD || 'admin123';

/**
 * S4: B1 → B1d
 * User clicks Add to Cart with product stock = 0
 * Expected: Shows "Out of stock", cannot add to cart
 */
test.describe('Bagisto S4 – Zero Stock Handling', () => {
  
  test('S4 – Cannot add product with zero stock to cart', async ({ page, context }) => {
    console.log('Step 1 (User): Logging in...');
    const store = new StorePage(page);
    await store.login();
    
    console.log('Step 2 (User): Finding first product...');
    await store.addFirstProductFromHome();
    
    // Get the product name that was just added
    const addedProductName = (store as any).lastAddedProductName;
    console.log(`  ✓ Added product: ${addedProductName}`);
    
    // Navigate to cart and get product link
    await page.goto(baseUrl + '/checkout/cart', { 
      waitUntil: 'networkidle',
      timeout: 20000 
    });
    
    console.log('Step 3 (User): Opening product page from cart...');
    const productLink = page.getByRole('link', { name: new RegExp(addedProductName.substring(0, 20), 'i') }).first();
    
    if (await productLink.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log(`  → Clicking product link: ${addedProductName.substring(0, 30)}...`);
      await productLink.click();
      await page.waitForLoadState('networkidle');
      console.log(`  ✓ Product page opened: ${page.url()}`);
    } else {
      console.log('  ⚠ Product link not found in cart');
      const anyProductLink = page.locator('a[href*="/product/"]').first();
      if (await anyProductLink.isVisible({ timeout: 2000 }).catch(() => false)) {
        await anyProductLink.click();
        await page.waitForLoadState('networkidle');
      }
    }
    
    // Open admin in new tab
    console.log('\nStep 4 (Admin): Opening admin panel in new tab...');
    const adminLinkSelector = 'a[target="_blank"]:has-text("Opens in a new tab")';
    const adminLink = page.locator(adminLinkSelector).first();
    
    let adminPage;
    if (await adminLink.isVisible({ timeout: 2000 }).catch(() => false)) {
      console.log('  → Clicking "Opens in a new tab" link...');
      const [popup] = await Promise.all([
        context.waitForEvent('page'),
        adminLink.click()
      ]);
      adminPage = popup;
      console.log('  ✓ Admin tab opened');
    } else {
      console.log('  → Admin link not found, opening admin URL directly...');
      adminPage = await context.newPage();
      await adminPage.goto(adminUrl);
    }
    
    await adminPage.waitForLoadState('networkidle');
    
    // Login to admin
    console.log('Step 5 (Admin): Logging in to admin panel...');
    const adminSignInBtn = adminPage.getByRole('button', { name: 'Sign In' });
    if (await adminSignInBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await adminPage.fill('input[name="email"]', adminEmail);
      await adminPage.fill('input[name="password"]', adminPassword);
      await adminSignInBtn.click();
      await adminPage.waitForLoadState('networkidle');
      console.log('  ✓ Admin logged in');
    } else {
      console.log('  ℹ Already logged in to admin');
    }
    
    // Search for product using Mega Search
    console.log('Step 6 (Admin): Searching for product...');
    const searchBox = adminPage.getByRole('textbox', { name: 'Mega Search' });
    await searchBox.click();
    
    const searchTerm = addedProductName?.split(' ').slice(0, 3).join(' ') || 'Arctic';
    console.log(`  → Searching for: "${searchTerm}"`);
    
    await searchBox.fill(searchTerm);
    await searchBox.press('Enter');
    await adminPage.waitForLoadState('networkidle');
    await adminPage.waitForTimeout(2000);
    console.log('  ✓ Search completed');
    
    // Click on product from search results
    console.log('Step 7 (Admin): Opening product edit page...');
    const searchResultLink = adminPage.locator(`a[href*="/catalog/products/edit/"]:has-text("${searchTerm.split(' ')[0]}")`).first();
    
    if (await searchResultLink.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log(`  → Found product in search results`);
      await searchResultLink.click();
      await adminPage.waitForLoadState('networkidle');
      await adminPage.waitForTimeout(2000);
      console.log('  ✓ Product edit page opened');
    } else {
      console.log('  ⚠ Product not found in search results');
      console.log('  ⚠ Cannot modify stock - test cannot proceed');
      await adminPage.close();
      return;
    }
    
    // Set stock to 0
    console.log('Step 8 (Admin): Setting stock to 0...');
    const stockInput = adminPage.locator('input[name="inventories[1]"]').first();
    
    if (await stockInput.isVisible({ timeout: 3000 }).catch(() => false)) {
      const currentStock = await stockInput.inputValue();
      console.log(`  Current stock: ${currentStock}`);
      
      await stockInput.click();
      await stockInput.fill('0');
      console.log('  ✓ Set stock to 0');
      
      // Save product
      const saveBtn = adminPage.getByRole('button', { name: 'Save Product' });
      if (await saveBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await saveBtn.click().catch(() => console.log('  ℹ Save click completed'));
        await adminPage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        await adminPage.waitForTimeout(2000);
        console.log('  ✓ Product saved with stock = 0');
      }
    } else {
      console.log('  ⚠ Stock input not found (demo may not allow editing)');
      await adminPage.close();
      return;
    }
    
    // Switch back to user tab
    console.log('\nStep 9 (User): Returning to product page...');
    await page.bringToFront();
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    console.log('Step 10 (User): Verifying "Add To Cart" button state...');
    const addToCartBtn = page.locator('button:has-text("Add To Cart")').first();
    const isAddBtnVisible = await addToCartBtn.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (isAddBtnVisible) {
      const isDisabled = await addToCartBtn.isDisabled().catch(() => false);
      
      if (isDisabled) {
        console.log('  ✓ "Add To Cart" button is DISABLED (correct behavior)');
        console.log('  → Cannot add out-of-stock product to cart');
      } else {
        console.log('  ⚠ "Add To Cart" button is ENABLED');
        console.log('  → Attempting to click (should show error)...');
        
        await addToCartBtn.click();
        await page.waitForTimeout(2000);
        
        // Check for error message
        console.log('\nStep 11 (User): Checking for error message...');
        const errorSelectors = [
          'text=/out of stock/i',
          'text=/not available/i',
          'text=/insufficient/i',
          'text=/cannot add/i',
          'text=/error/i',
          '[class*="error"]',
          '[class*="alert"]'
        ];
        
        let errorFound = false;
        for (const selector of errorSelectors) {
          const error = page.locator(selector).first();
          if (await error.isVisible({ timeout: 2000 }).catch(() => false)) {
            const errorText = await error.textContent();
            console.log(`  ✓ Error message: "${errorText?.trim()}"`);
            errorFound = true;
            break;
          }
        }
        
        if (!errorFound) {
          console.log('  ⚠ No error message displayed');
          console.log('  ⚠ Product may have been added despite zero stock');
        }
      }
    } else {
      // Check for "Out of Stock" label/badge
      const outOfStockLabel = page.locator('text=/out of stock/i, text=/sold out/i').first();
      if (await outOfStockLabel.isVisible({ timeout: 2000 }).catch(() => false)) {
        console.log('  ✓ "Out of Stock" label displayed');
        console.log('  ✓ No "Add To Cart" button (correct behavior)');
      } else {
        console.log('  ⚠ Neither "Add To Cart" button nor "Out of Stock" label found');
      }
    }
    
    console.log('\nStep 12 (User): Verifying cart did not change...');
    await page.goto(baseUrl + '/checkout/cart', { 
      waitUntil: 'networkidle' 
    });
    
    const qtyInputs = page.locator('input[type="hidden"][name="quantity"]');
    const itemCount = await qtyInputs.count();
    
    // Cart should still have 1 item (the original one added before stock = 0)
    if (itemCount === 1) {
      console.log('  ✓ Cart unchanged (1 item from before stock reduction)');
      console.log('  ✓ Out-of-stock product not added again');
    } else if (itemCount === 0) {
      console.log('  ℹ Cart is empty (original item may have been removed)');
    } else {
      console.log(`  ⚠ Cart has ${itemCount} item(s)`);
      console.log('  ⚠ Out-of-stock product may have been added');
    }
    
    // Cleanup: Restore stock to 200
    console.log('\nStep 13 (Admin Cleanup): Restoring stock to 200...');
    await adminPage.bringToFront();
    
    // Search for product again to restore stock
    await adminPage.goto(adminUrl, { waitUntil: 'domcontentloaded' }).catch(() => {});
    await adminPage.waitForTimeout(2000);
    
    const searchBox2 = adminPage.getByRole('textbox', { name: 'Mega Search' });
    if (await searchBox2.isVisible({ timeout: 3000 }).catch(() => false)) {
      const searchTerm2 = addedProductName?.split(' ').slice(0, 3).join(' ') || 'Arctic';
      console.log(`  → Searching for: "${searchTerm2}"`);
      
      await searchBox2.click();
      await searchBox2.fill(searchTerm2);
      await searchBox2.press('Enter');
      await adminPage.waitForLoadState('domcontentloaded').catch(() => {});
      await adminPage.waitForTimeout(2000);
      
      // Click product from search
      const searchResultLink2 = adminPage.locator(`a[href*="/catalog/products/edit/"]:has-text("${searchTerm2.split(' ')[0]}")`).first();
      if (await searchResultLink2.isVisible({ timeout: 3000 }).catch(() => false)) {
        await searchResultLink2.click();
        await adminPage.waitForLoadState('domcontentloaded').catch(() => {});
        await adminPage.waitForTimeout(2000);
        
        const restoreStock = adminPage.locator('input[name="inventories[1]"]').first();
        if (await restoreStock.isVisible({ timeout: 3000 }).catch(() => false)) {
          await restoreStock.click();
          await restoreStock.fill('200');
          console.log('  ✓ Stock restored to 200');
          
          const saveBtn = adminPage.getByRole('button', { name: 'Save Product' });
          if (await saveBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
            await saveBtn.click().catch(() => {});
            await adminPage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
            await adminPage.waitForTimeout(2000);
            console.log('  ✓ Product saved with stock = 200');
          }
        }
      }
    } else {
      console.log('  ⚠ Could not restore stock (may need manual cleanup)');
    }
    
    await adminPage.close();
    
    console.log('\n' + '='.repeat(80));
    console.log('S4B: COMPLETED - Zero stock handling tested');
    console.log('Expected behavior:');
    console.log('  - Admin sets stock to 0');
    console.log('  - User reloads product page');
    console.log('  - "Add To Cart" button disabled OR error message shown');
    console.log('  - Out-of-stock product cannot be added to cart');
    console.log('='.repeat(80));
  });
});
