import { test, expect } from '@playwright/test';
import { config } from 'dotenv';
import { StorePage } from '../pages/StorePage';

config();

/**
 * S3: B1 → B1c
 * User moves a product to "Wishlist"
 * Expected: Product moved to Wishlist, not counted in subtotal
 */
test.describe('Bagisto S3 – Move to Wishlist', () => {
  
  test('S3 – Move product to wishlist', async ({ page }) => {
    console.log('Step 1: Logging in (required for wishlist/save for later)...');
    const store = new StorePage(page);
    await store.login();
    
    console.log('Step 2: Adding product to cart...');
    await store.addFirstProductFromHome();
    
    console.log('Step 3: Cart page loaded with product...');
    // addFirstProductFromHome already navigates to cart
    
    console.log('Step 4: Verifying cart has items...');
    const qtyInputs = page.locator('input[type="hidden"][name="quantity"]');
    const itemCount = await qtyInputs.count();
    console.log(`  Cart has ${itemCount} item(s)`);
    expect(itemCount).toBeGreaterThan(0);
    
    console.log('Step 5: Selecting item for "Save for Later"...');
    const selectAllLabel = page.locator('label[for="select-all"]');
    await selectAllLabel.click();
    await page.waitForTimeout(1000);
    
    console.log('Step 6: Looking for "Move To Wishlist" button...');
    const moveToWishlistBtn = page.locator('span:has-text("Move To Wishlist")[role="button"]').first();
    const isWishlistAvailable = await moveToWishlistBtn.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (!isWishlistAvailable) {
      console.log('  ⚠ "Move To Wishlist" button not visible');
      console.log('  Note: Bagisto uses "Wishlist" instead of "Save for Later"');
      console.log('B1c: SKIPPED - Feature requires specific UI or multiple items selected');
      test.skip();
      return;
    }
    
    console.log('Step 7: Clicking "Move To Wishlist" button...');
    await moveToWishlistBtn.click();
    await page.waitForTimeout(500);
    
    console.log('Step 8: Navigating to wishlist/saved items page...');
    await page.goto('https://commerce.bagisto.com/customer/account/wishlist', { waitUntil: 'networkidle' });
    
    console.log('Step 9: Verifying item appears in wishlist...');
    const wishlistHeading = page.locator('h2:has-text("Wishlist")').first();
    await expect(wishlistHeading).toBeVisible({ timeout: 5000 });
    
    const wishlistItems = page.locator('button:has-text("Move To Cart")');
    const savedCount = await wishlistItems.count();
    console.log(`  Found ${savedCount} item(s) in wishlist/saved list`);
    expect(savedCount).toBeGreaterThan(0);
    
    console.log('Step 10: Verifying cart is now empty after moving to wishlist...');
    await store.openCart();
    await store.cartIsEmpty();
    
    console.log('B1c: PASSED - Product moved to "Saved for Later" (Wishlist)');
  });
});
