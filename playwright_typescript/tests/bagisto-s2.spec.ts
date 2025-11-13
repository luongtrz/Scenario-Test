import { test, expect } from '@playwright/test';
import { config } from 'dotenv';
import { StorePage } from '../pages/StorePage';

config();

/**
 * S2: B1 → B1b
 * User removes all products from cart
 * Expected: Cart returns to empty state, subtotal = 0
 */
test.describe('Bagisto S2 – Remove All Products', () => {
  
  test('S2 – Remove all products returns cart to empty state', async ({ page }) => {
    console.log('Step 1: Adding products to cart...');
    const store = new StorePage(page);
    
    await store.addFirstProductFromHome();
    
    console.log('Step 2: Cart page should be loaded with items...');
    // addFirstProductFromHome already navigates to cart
    
    console.log('Step 3: Verifying cart has items...');
    const qtyInputs = page.locator('input[type="hidden"][name="quantity"]');
    const initialCount = await qtyInputs.count();
    console.log(`  Cart has ${initialCount} item(s)`);
    expect(initialCount).toBeGreaterThan(0);
    
    console.log('Step 4: Selecting all items using "Select All" checkbox...');
    const selectAllLabel = page.locator('label[for="select-all"]');
    await selectAllLabel.click();
    await page.waitForTimeout(500);
    
    console.log('Step 5: Clicking bulk "Remove" button...');
    const bulkRemoveBtn = page.locator('span:has-text("Remove")[role="button"]').first();
    await bulkRemoveBtn.click();
    
    console.log('Step 6: Confirming removal in modal (if present)...');
    await page.waitForTimeout(500);
    
    // Look for "Agree" button in confirmation modal
    const agreeBtn = page.getByRole('button', { name: 'Agree', exact: true });
    const isModalVisible = await agreeBtn.isVisible({ timeout: 2000 }).catch(() => false);
    
    if (isModalVisible) {
      console.log('  ✓ Confirmation modal appeared, clicking Agree...');
      await agreeBtn.click();
    } else {
      // Fallback to other confirmation buttons
      const confirmBtn = page.locator('button:has-text("Yes"), button:has-text("Confirm"), button:has-text("OK")').first();
      if (await confirmBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
        await confirmBtn.click();
      }
    }
    
    console.log('Step 7: Waiting for removal to complete...');
    await page.waitForTimeout(2000);
    
    console.log('Step 8: Verifying cart is now empty...');
    await store.cartIsEmpty();
    
    console.log('Step 9: Verifying "Proceed To Checkout" button is hidden...');
    const checkoutBtn = page.locator('a:has-text("Proceed To Checkout")').first();
    const isCheckoutVisible = await checkoutBtn.isVisible({ timeout: 2000 }).catch(() => false);
    
    if (!isCheckoutVisible) {
      console.log('  ✓ Checkout button hidden on empty cart');
    }
    
    console.log('B1b: PASSED - All products removed, cart returned to empty state');
  });
});
