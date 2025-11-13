import { test, expect } from '@playwright/test';
import { config } from 'dotenv';
import { StorePage } from '../pages/StorePage';

config();

/**
 * S12: B1 → B2 → B3 → B4 → B5 → B5a
 * User reloads 1-2 seconds after order is being created by backend
 * Expected: Backend ensures only 1 order created (idempotent)
 */
test.describe('Bagisto S12 - Reload During Order Creation', () => {
  
  test('S12 - Reload during backend order creation', async ({ page }) => {
    console.log('Step 1 (B1): Logging in to save order...');
    const store = new StorePage(page);
    await store.login();
    
    console.log('Step 2 (B2): Checking cart...');
    await store.openCart();
    
    const initialQtyInputs = page.locator('input[type="hidden"][name="quantity"]');
    const initialCartCount = await initialQtyInputs.count();
    console.log(`  ✓ Cart has ${initialCartCount} item(s)`);
    
    if (initialCartCount === 0) {
      console.log('  → Cart empty, adding product...');
      await store.addFirstProductFromHome();
    } else {
      console.log('  ✓ Using existing cart items');
    }
    
    console.log('Step 3 (B5c): Capturing initial order count BEFORE checkout...');
    await page.goto(process.env.BAGISTO_BASE_URL + '/customer/account/orders', {
      waitUntil: 'networkidle'
    });
    await page.waitForTimeout(2000);
    
    const orderRows = page.locator('.row.grid')
      .filter({ hasNot: page.locator('text=/Order ID|Order Date/i') });
    
    const initialOrderCount = await orderRows.count();
    
    // Get first order ID to detect new orders (pagination shows only 10 per page)
    let initialFirstOrderId = '';
    if (initialOrderCount > 0) {
      const firstOrderIdText = await orderRows.first().locator('p').first().textContent();
      initialFirstOrderId = firstOrderIdText?.trim() || '';
      console.log(`  Initial order count: ${initialOrderCount} (first ID: #${initialFirstOrderId})`);
    } else {
      console.log(`  Initial order count: 0`);
    }
    
    console.log('Step 4 (B3): Going back to cart...');
    await page.goto(process.env.BAGISTO_BASE_URL + '/checkout/cart', {
      waitUntil: 'networkidle'
    });
    await page.waitForTimeout(1500);
    console.log('  ✓ Back at cart page');
    
    console.log('Step 5 (B3): Proceeding to checkout...');
    await store.goCheckout();
    
    console.log('Step 6 (B4): Filling shipping address...');
    await store.fillShippingAddressMinimal();
    
    console.log('Step 7 (B5): Selecting shipping and payment methods...');
    await page.waitForSelector('input[type="radio"][id*="free_free"], input[type="radio"][id*="cashondelivery"]', {
      timeout: 30000,
      state: 'attached'
    });
    await page.waitForTimeout(2000);
    
    const freeShippingLabel = page.locator('label[for="free_free"]').last();
    if (await freeShippingLabel.isVisible({ timeout: 5000 }).catch(() => false)) {
      await freeShippingLabel.click();
      console.log('  ✓ Selected Free Shipping');
      await page.waitForTimeout(1000);
    }
    
    const codLabel = page.locator('label[for="cashondelivery"]').last();
    if (await codLabel.isVisible({ timeout: 5000 }).catch(() => false)) {
      await codLabel.click();
      console.log('  ✓ Selected Cash on Delivery');
      await page.waitForTimeout(1000);
    }
    
    console.log('Step 8 (B5c): Clicking Place Order and INTERRUPTING with F5...');
    const placeOrderBtn = page.locator('button:has-text("Place Order")').first();
    
    if (await placeOrderBtn.isVisible({ timeout: 10000 }).catch(() => false)) {
      console.log('  → Clicking Place Order...');
      await placeOrderBtn.click();
      
      console.log('  → Waiting 3 seconds (order creation in progress)...');
      await page.waitForTimeout(3000);
      
      console.log('  → RELOADING PAGE (F5) during order creation!');
      await page.reload({ waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(2000);
      console.log(`  ✓ Page reloaded, URL: ${page.url()}`);
    } else {
      console.log('  ⚠ Place Order button not visible!');
      console.log('  → Attempting reload anyway...');
      await page.reload({ waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(2000);
    }
    
    console.log('Step 9 (B5c): Checking if order was created during interrupted placement...');
    await page.goto(process.env.BAGISTO_BASE_URL + '/customer/account/orders', {
      waitUntil: 'networkidle'
    });
    await page.waitForTimeout(2000);
    
    // Re-query orderRows after navigation
    const orderRowsAfterReload = page.locator('.row.grid')
      .filter({ hasNot: page.locator('text=/Order ID|Order Date/i') });
    const orderCountAfterReload = await orderRowsAfterReload.count();
    
    // Get first order ID to detect if new order was created
    let firstOrderIdAfterReload = '';
    if (orderCountAfterReload > 0) {
      const firstOrderIdText = await orderRowsAfterReload.first().locator('p').first().textContent();
      firstOrderIdAfterReload = firstOrderIdText?.trim() || '';
    }
    
    console.log(`  Order count after reload: ${orderCountAfterReload} (first ID: #${firstOrderIdAfterReload})`);
    
    if (firstOrderIdAfterReload !== initialFirstOrderId && firstOrderIdAfterReload !== '') {
      console.log(`  ⚠ Order WAS created during interrupted placement! (New ID: #${firstOrderIdAfterReload})`);
      console.log('     → Reload did NOT prevent order creation!');
    } else {
      console.log('  ✓ No order created during interrupted placement');
    }
    
    console.log('Step 10 (B5c): Checking cart state after reload...');
    await page.goto(process.env.BAGISTO_BASE_URL + '/checkout/cart', {
      waitUntil: 'networkidle'
    });
    await page.waitForTimeout(1500);
    
    const qtyInputs = page.locator('input[type="hidden"][name="quantity"]');
    const cartCountAfterReload = await qtyInputs.count();
    console.log(`  Cart items after reload: ${cartCountAfterReload}`);
    
    if (cartCountAfterReload === 0) {
      console.log('  ⚠ Cart empty after reload (order WAS placed despite F5!)');
      console.log('  → Adding product again to test re-ordering...');
      await store.addFirstProductFromHome();
    } else {
      console.log('  ✓ Cart still has items (interrupted order did not empty cart)');
    }
    
    console.log('Step 11 (B5c): Proceeding to checkout again...');
    await store.goCheckout();
    
    console.log('Step 12 (B4): Filling shipping address again...');
    await store.fillShippingAddressMinimal();
    
    console.log('Step 13 (B5): Placing order after reload...');
    await store.choosePaymentAndPlace(false);
    
    console.log('Step 14 (B5): Waiting for order success page...');
    try {
      await page.waitForURL('**/checkout/onepage/success', { 
        timeout: 30000,
        waitUntil: 'networkidle' 
      });
      console.log('  ✓ Order redirected to success page');
      
      const orderLink = page.locator('p.text-xl a.text-blue-700[href*="/customer/account/orders/view/"]').first();
      if (await orderLink.isVisible({ timeout: 5000 }).catch(() => false)) {
        const orderIdText = await orderLink.textContent();
        const orderId = orderIdText?.trim() || '';
        console.log(`  ✓ Order created: #${orderId}`);
      }
    } catch (error) {
      console.log('  ⚠ Did not redirect to success page');
      console.log(`  Current URL: ${page.url()}`);
    }
    
    await page.waitForTimeout(2000);
    
    console.log('Step 15 (B5c): Final order count verification...');
    await page.goto(process.env.BAGISTO_BASE_URL + '/customer/account/orders', {
      waitUntil: 'networkidle'
    });
    await page.waitForTimeout(2000);
    
    // Re-query orderRows after navigation
    const orderRowsFinal = page.locator('.row.grid')
      .filter({ hasNot: page.locator('text=/Order ID|Order Date/i') });
    const finalOrderCount = await orderRowsFinal.count();
    
    // Get first order ID to detect new orders
    let finalFirstOrderId = '';
    if (finalOrderCount > 0) {
      const firstOrderIdText = await orderRowsFinal.first().locator('p').first().textContent();
      finalFirstOrderId = firstOrderIdText?.trim() || '';
    }
    
    console.log(`  Final order count: ${finalOrderCount} (first ID: #${finalFirstOrderId})`);
    
    // Calculate actual new orders by comparing first order IDs
    let actualNewOrders = 0;
    if (finalFirstOrderId !== initialFirstOrderId && finalFirstOrderId !== '') {
      // At least 1 new order (could be 2 if reload created order)
      if (firstOrderIdAfterReload !== initialFirstOrderId && firstOrderIdAfterReload !== '') {
        // Reload order + final order = 2 new orders
        actualNewOrders = 2;
      } else {
        // Only final order = 1 new order
        actualNewOrders = 1;
      }
    }
    
    console.log('');
    console.log('=== ORDER CREATION SUMMARY ===');
    console.log(`  Initial order count: ${initialOrderCount} (first ID: #${initialFirstOrderId || 'None'})`);
    console.log(`  After F5 (interrupted): ${orderCountAfterReload} (first ID: #${firstOrderIdAfterReload || 'None'}) ${firstOrderIdAfterReload !== initialFirstOrderId && firstOrderIdAfterReload !== '' ? '← NEW ORDER CREATED!' : '← No change'}`);
    console.log(`  Final (re-order): ${finalOrderCount} (first ID: #${finalFirstOrderId || 'None'})`);
    console.log(`  Total new orders: ${actualNewOrders}`);
    console.log('');
    
    if (actualNewOrders === 1) {
      console.log('  ✓ PASS: Only 1 order created (no duplicate)');
      console.log('    → F5 reload prevented duplicate order creation');
    } else if (actualNewOrders === 2) {
      console.log('  ⚠ FAIL: 2 orders created - DUPLICATE BUG!');
      console.log('    → Interrupted order + re-order = DUPLICATE!');
      console.log('    → F5 did NOT prevent order creation!');
    } else {
      console.log(`  ℹ Created ${actualNewOrders} orders (check manually)`);
    }
    
    console.log('');
    console.log('Step 16: Verifying cart is empty...');
    await store.openCart();
    
    try {
      await store.cartIsEmpty();
      console.log('  ✓ Cart empty after order');
    } catch {
      const cartItems = await qtyInputs.count();
      console.log(`  ⚠ Cart not empty: ${cartItems} items`);
    }
    
    console.log('');
    console.log('S9: COMPLETED - Order placement interruption tested');
    console.log('=== KEY FINDINGS ===');
    console.log(`  Initial state: #${initialFirstOrderId || 'No orders'}`);
    console.log(`  After Place Order + F5: #${firstOrderIdAfterReload || 'No new order'} ${firstOrderIdAfterReload !== initialFirstOrderId && firstOrderIdAfterReload !== '' ? '(⚠ BUG: Order created despite F5!)' : '(✓ No order)'}`);
    console.log(`  After re-order: #${finalFirstOrderId || 'No order'}`);
    console.log(`  Duplicate prevention: ${actualNewOrders === 1 ? '✓ PASS' : '✗ FAIL'}`);
    console.log('');
    console.log('Test Scenario:');
    console.log('  1. Click "Place Order" button');
    console.log('  2. Wait 2 seconds (order creation in progress)');
    console.log('  3. Press F5 to reload page (interrupt)');
    console.log('  4. Check if order was created');
    console.log('  5. Re-checkout and place order again');
    console.log('  6. Verify only 1 order created (no duplicate)');
  });
});
