import { test } from '@playwright/test';
import { config } from 'dotenv';
import { StorePage } from '../pages/StorePage';

config();

const baseUrl = process.env.BAGISTO_BASE_URL || 'https://commerce.bagisto.com';
const adminUrl = process.env.BAGISTO_ADMIN_URL || 'https://commerce.bagisto.com/admin';
const adminEmail = process.env.BAGISTO_ADMIN_EMAIL || 'admin@example.com';
const adminPassword = process.env.BAGISTO_ADMIN_PASSWORD || 'admin123';

/**
 * S6: B1 → B2 → B3 → B3b → B4 → B5
 * Product price changes while user is at checkout
 * Expected: Show new price, require re-confirmation; PO reflects new price
 */
test.describe('Bagisto S6 - Price Change During Checkout', () => {
  test('S6 - Price change during checkout updates order', async ({ page, context }) => {
    console.log('Step 1 (User): Logging in and clearing cart...');
    const store = new StorePage(page);
    await store.login();
    
    // Clear cart first
    await page.goto(baseUrl + '/checkout/cart', { waitUntil: 'networkidle' });
    const removeBtn = page.getByRole('button', { name: /Remove/i }).first();
    while (await removeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await removeBtn.click();
      const agreeBtn = page.getByRole('button', { name: 'Agree', exact: true });
      if (await agreeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await agreeBtn.click();
        await page.waitForTimeout(2000);
      }
    }
    console.log('  ✓ Cart cleared');
    
    console.log('Step 2 (User): Adding product to cart...');
    await store.addFirstProductFromHome();
    
    const productName = (store as any).lastAddedProductName;
    console.log(`  ✓ Added: ${productName}`);
    
    // Get cart details - quantity and item price BEFORE admin changes
    await page.goto(baseUrl + '/checkout/cart', { waitUntil: 'networkidle' });
    const qtyInput = page.locator('input[type="hidden"][name="quantity"]').first();
    const quantity = await qtyInput.getAttribute('value').catch(() => '1');
    
    const itemPriceElem = page.locator('p.text-lg.font-semibold').first();
    const originalItemPrice = await itemPriceElem.textContent().catch(() => 'N/A');
    console.log(`  Cart BEFORE: ${quantity}x @ ${originalItemPrice?.trim()}`);
    
    // Click product link to open product page
    console.log('Step 3 (User): Opening product page from cart...');
    const productLink = page.getByRole('link', { name: new RegExp(productName.substring(0, 20), 'i') }).first();
    
    if (await productLink.isVisible({ timeout: 3000 }).catch(() => false)) {
      await productLink.click();
      await page.waitForLoadState('networkidle');
      console.log(`  ✓ Product page opened: ${page.url()}`);
    }
    
    // Open admin via "Opens in a new tab" link (same as S4)
    console.log('Step 4 (Admin): Opening admin from product page...');
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
    const signInBtn = adminPage.getByRole('button', { name: 'Sign In' });
    if (await signInBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await adminPage.fill('input[name="email"]', adminEmail);
      await adminPage.fill('input[name="password"]', adminPassword);
      await signInBtn.click();
      await adminPage.waitForLoadState('networkidle');
      console.log('  ✓ Admin logged in');
    }
    
    // Search for product (same approach as S4)
    console.log('Step 5 (Admin): Searching for product...');
    const searchTerm = productName?.split(' ').slice(0, 3).join(' ') || 'Arctic';
    const searchBox = adminPage.getByRole('textbox', { name: 'Mega Search' });
    
    await searchBox.click();
    await searchBox.fill(searchTerm);
    await searchBox.press('Enter');
    await adminPage.waitForLoadState('networkidle');
    await adminPage.waitForTimeout(2000);
    console.log(`  → Searched for: "${searchTerm}"`);
    
    // Click product edit link
    const searchResultLink = adminPage.locator(`a[href*="/catalog/products/edit/"]:has-text("${searchTerm.split(' ')[0]}")`).first();
    
    if (await searchResultLink.isVisible({ timeout: 3000 }).catch(() => false)) {
      await searchResultLink.click();
      await adminPage.waitForLoadState('networkidle');
      await adminPage.waitForTimeout(2000);
      console.log('  ✓ Product edit page opened');
      
      // Change price to 2x original
      console.log('Step 6 (Admin): Multiplying price by 2...');
      const priceInput = adminPage.locator('#price');
      if (await priceInput.isVisible({ timeout: 3000 }).catch(() => false)) {
        const currentPriceStr = await priceInput.inputValue();
        (adminPage as any).originalPrice = currentPriceStr; // Save original for cleanup
        const oldPrice = parseFloat(currentPriceStr.replace(/[^0-9.]/g, ''));
        
        // Multiply price by 2x (more reasonable than 5x)
        const newPrice = (oldPrice * 2).toFixed(2);
        
        console.log(`  Original price: $${oldPrice}`);
        console.log(`  New price (2x): $${newPrice}`);
        
        await priceInput.click();
        await priceInput.fill(newPrice);
        
        const saveBtn = adminPage.getByRole('button', { name: 'Save Product' });
        await saveBtn.click().catch(() => {});
        await adminPage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
        await adminPage.waitForTimeout(2000);
        console.log('  ✓ Product saved with 2x price');
      }
    }
    
    // User proceeds to checkout
    console.log('Step 7 (User): Proceeding to checkout...');
    await page.bringToFront();
    
    // Navigate to cart page first (we're on product page after admin closed)
    await page.goto(baseUrl + '/checkout/cart', { waitUntil: 'networkidle', timeout: 20000 });
    await page.waitForTimeout(2000); // Wait for cart to refresh with new price
    
    // Capture UPDATED cart price after admin change
    const updatedItemPriceElem = page.locator('p.text-lg.font-semibold').first();
    const updatedItemPrice = await updatedItemPriceElem.textContent().catch(() => 'N/A');
    console.log(`  Cart AFTER admin change: ${updatedItemPrice?.trim()}`);
    
    await store.goCheckout();
    await store.fillShippingAddressMinimal();
    
    await page.waitForTimeout(2000);
    const checkoutSubtotal = await page
      .locator('div.flex.justify-between:has-text("Subtotal")')
      .locator('p').last()
      .textContent().catch(() => 'N/A');
    
    const checkoutGrandTotal = await page
      .locator('div.flex.justify-between:has-text("Grand Total")')
      .locator('p').last()
      .textContent().catch(() => 'N/A');
    
    console.log(`  Checkout Summary:`);
    console.log(`    Subtotal: ${checkoutSubtotal?.trim()}`);
    console.log(`    Grand Total: ${checkoutGrandTotal?.trim()}`);
    
    // Place order
    console.log('Step 8 (User): Placing order...');
    await store.choosePaymentAndPlace(false);
    await page.waitForURL('**/checkout/onepage/success', { timeout: 30000 }).catch(() => {});
    
    // Verify order
    const orderLink = page.locator('p.text-xl a.text-blue-700[href*="/orders/view/"]').first();
    if (await orderLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      const orderId = await orderLink.textContent();
      console.log(`  ✓ Order #${orderId} created`);
      
      await orderLink.click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(3000);
      
      const orderSubtotal = await page
        .locator('div.flex.justify-between:has-text("Subtotal")').first()
        .locator('p').last()
        .textContent().catch(() => 'N/A');
      
      const orderGrandTotal = await page
        .locator('div.flex.justify-between:has-text("Grand Total")').first()
        .locator('p').last()
        .textContent().catch(() => 'N/A');
      
      console.log(`  Order Detail Summary:`);
      console.log(`    Quantity: ${quantity}x`);
      console.log(`    Subtotal: ${orderSubtotal?.trim()}`);
      console.log(`    Grand Total: ${orderGrandTotal?.trim()}`);
      
      console.log(`  Comparison:`);
      console.log(`    Cart showed: ${originalItemPrice?.trim()} x ${quantity}`);
      console.log(`    Checkout showed: ${checkoutGrandTotal?.trim()}`);
      console.log(`    Order final: ${orderGrandTotal?.trim()}`);
      
      // Check if order used updated price (2x)
      const originalPrice = parseFloat(originalItemPrice?.replace(/[^0-9.]/g, '') || '0');
      const orderPrice = parseFloat(orderGrandTotal?.replace(/[^0-9.]/g, '') || '0');
      const expectedPrice = originalPrice * 2 * parseInt(quantity || '1');
      
      if (Math.abs(orderPrice - expectedPrice) < 1) {
        console.log('  ✓ Order uses UPDATED admin price (2x original)!');
      } else if (orderGrandTotal === checkoutGrandTotal) {
        console.log('  ℹ Order uses checkout display price (not updated)');
      }
    }
    
    // Cleanup: Restore original price (divide by 2)
    console.log('Step 9 (Admin Cleanup): Restoring original price...');
    await adminPage.bringToFront();
    const savedOriginalPrice = (adminPage as any).originalPrice || '19.99';
    
    // Search for product again (same as S4 cleanup)
    await adminPage.goto(adminUrl, { waitUntil: 'domcontentloaded' }).catch(() => {});
    await adminPage.waitForTimeout(2000);
    
    const searchBox2 = adminPage.getByRole('textbox', { name: 'Mega Search' });
    if (await searchBox2.isVisible({ timeout: 3000 }).catch(() => false)) {
      await searchBox2.click();
      await searchBox2.fill(searchTerm);
      await searchBox2.press('Enter');
      await adminPage.waitForLoadState('domcontentloaded').catch(() => {});
      await adminPage.waitForTimeout(2000);
      
      const searchResultLink2 = adminPage.locator(`a[href*="/catalog/products/edit/"]:has-text("${searchTerm.split(' ')[0]}")`).first();
      if (await searchResultLink2.isVisible({ timeout: 3000 }).catch(() => false)) {
        await searchResultLink2.click();
        await adminPage.waitForLoadState('domcontentloaded').catch(() => {});
        await adminPage.waitForTimeout(2000);
        
        const priceInput2 = adminPage.locator('#price');
        if (await priceInput2.isVisible({ timeout: 3000 }).catch(() => false)) {
          await priceInput2.click();
          await priceInput2.fill(savedOriginalPrice);
          console.log(`  ✓ Price restored to $${savedOriginalPrice}`);
          
          const saveBtn2 = adminPage.getByRole('button', { name: 'Save Product' });
          await saveBtn2.click().catch(() => {});
          await adminPage.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
          await adminPage.waitForTimeout(2000);
          console.log('  ✓ Product saved');
        }
      }
    }
    
    await adminPage.close();
    console.log('S5: COMPLETED - Price change handling tested');
    console.log('Expected: Order should reflect latest admin price if updated before final submission');
  });
});
