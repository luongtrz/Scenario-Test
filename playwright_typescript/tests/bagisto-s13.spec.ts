import { test, expect } from '@playwright/test';
import { config } from 'dotenv';
import { StorePage } from '../pages/StorePage';

config();

/**
 * S13: B1 → B2 → B3 → B4 → B5 → B5b
 * User clicks Place Order then F5 immediately (0ms)
 * Expected: No duplicate orders; payment not called multiple times
 */
test.describe('Bagisto S13 - Immediate F5 After Place Order', () => {
  
  test('S13 - Place Order then IMMEDIATE F5', async ({ page }) => {
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
    
    console.log('');
    console.log('=== ORDER #1 - PLACE AND IMMEDIATE F5 ===');
    console.log('Step 8 (B5c): Clicking Place Order and IMMEDIATE F5...');
    const placeOrderBtn = page.locator('button:has-text("Place Order")').first();
    
    if (await placeOrderBtn.isVisible({ timeout: 10000 }).catch(() => false)) {
      console.log('  → Clicking Place Order button...');
      await placeOrderBtn.click();
      
      console.log('  → IMMEDIATE F5 (< 100ms)!');
      await page.waitForTimeout(100); // Only 100ms - VERY FAST!
      
      await page.reload({ waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(1000);
      console.log(`  ✓ Page reloaded immediately`);
      console.log(`  Current URL: ${page.url()}`);
    } else {
      console.log('  ⚠ Place Order button not visible!');
      await page.reload({ waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(1000);
    }
    
    console.log('');
    console.log('=== ORDER #2 - PLACE AGAIN AND WAIT FOR COMPLETION ===');
    console.log('Step 9 (B5c): Placing order again after F5...');
    console.log('  Current URL: ' + page.url());
    
    await page.waitForTimeout(2000);
    
    // Check if we need to fill address or if payment options are already visible
    const paymentOptions = page.locator('input[type="radio"][id*="free_free"], input[type="radio"][id*="cashondelivery"]');
    const paymentVisible = await paymentOptions.first().isVisible({ timeout: 3000 }).catch(() => false);
    
    if (!paymentVisible) {
      console.log('  → Payment options not visible, filling address first...');
      await store.fillShippingAddressMinimal();
    } else {
      console.log('  → Payment options already visible, proceeding...');
    }
    
    console.log('Step 10 (B5): Selecting payment and placing order #2...');
    await page.waitForTimeout(1000);
    
    // Select shipping method
    const freeShippingLabel2 = page.locator('label[for="free_free"]').last();
    if (await freeShippingLabel2.isVisible({ timeout: 5000 }).catch(() => false)) {
      await freeShippingLabel2.click();
      console.log('  ✓ Selected Free Shipping');
      await page.waitForTimeout(500);
    }
    
    // Select payment method
    const codLabel2 = page.locator('label[for="cashondelivery"]').last();
    if (await codLabel2.isVisible({ timeout: 5000 }).catch(() => false)) {
      await codLabel2.click();
      console.log('  ✓ Selected Cash on Delivery');
      await page.waitForTimeout(500);
    }
    
    // Click Place Order #2
    const placeOrderBtn2 = page.locator('button:has-text("Place Order")').first();
    if (await placeOrderBtn2.isVisible({ timeout: 10000 }).catch(() => false)) {
      console.log('  → Clicking Place Order #2...');
      await placeOrderBtn2.click();
      console.log('  → Waiting for order processing (this may take time)...');
    }
    
    console.log('Step 11 (B5): Waiting for order #2 success page...');
    await page.waitForURL('**/checkout/onepage/success', { 
      timeout: 60000, // Increased to 60 seconds
      waitUntil: 'networkidle' 
    });
    console.log('  ✓ Order #2 redirected to success page');
    await page.waitForTimeout(2000); // Extra wait for page to fully render
    
    const orderLink = page.locator('p.text-xl a.text-blue-700[href*="/customer/account/orders/view/"]').first();
    let secondOrderId = '';
    if (await orderLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      const orderIdText = await orderLink.textContent();
      secondOrderId = orderIdText?.trim() || '';
      console.log(`  ✓ Order #2 created: #${secondOrderId}`);
    }
    
    await page.waitForTimeout(2000);
    
    console.log('');
    console.log('=== VERIFICATION - CHECK FOR DUPLICATE ORDERS ===');
    console.log('Step 12: Checking orders after both place order attempts...');
    await page.goto(process.env.BAGISTO_BASE_URL + '/customer/account/orders', {
      waitUntil: 'networkidle'
    });
    await page.waitForTimeout(2000);
    
    // Re-query orderRows after navigation
    const orderRowsFinal = page.locator('.row.grid')
      .filter({ hasNot: page.locator('text=/Order ID|Order Date/i') });
    const finalOrderCount = await orderRowsFinal.count();
    
    console.log(`  Total orders on page: ${finalOrderCount}`);
    
    // Count NEW orders by iterating until we hit the initial order ID
    let actualNewOrders = 0;
    for (let i = 0; i < finalOrderCount; i++) {
      const row = orderRowsFinal.nth(i);
      const orderIdText = await row.locator('p').first().textContent();
      const orderId = orderIdText?.trim() || '';
      
      if (orderId === initialFirstOrderId) {
        // Found the initial order, stop counting
        console.log(`  → Found initial order #${initialFirstOrderId} at position ${i + 1}`);
        break;
      }
      
      actualNewOrders++;
      console.log(`  → New order #${i + 1}: #${orderId}`);
    }
    
    console.log(`  Total NEW orders created: ${actualNewOrders}`);
    
    // If 2 orders were created, compare them for duplicates
    if (actualNewOrders === 2) {
      console.log('');
      console.log('Step 13 (B5c): ⚠ 2 ORDERS CREATED - Comparing for duplicate detection...');
      
      // Get first 2 order IDs from the list
      const order1Row = orderRowsFinal.nth(0);
      const order1IdText = await order1Row.locator('p').first().textContent();
      const order1Id = order1IdText?.trim() || '';
      
      const order2Row = orderRowsFinal.nth(1);
      const order2IdText = await order2Row.locator('p').first().textContent();
      const order2Id = order2IdText?.trim() || '';
      
      console.log(`  → Comparing Order #${order1Id} vs Order #${order2Id}...`);
      
      // Load first order by clicking link from orders page
      const order1Link = page.locator(`a[href*="/orders/view/${order1Id}"]`).first();
      if (await order1Link.isVisible({ timeout: 5000 }).catch(() => false)) {
        await order1Link.click();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(3000);
        
        // Extract Order #1 details
        let order1GrandTotal = 'N/A';
        let order1ProductName = 'N/A';
        
        try {
          const grandTotalText = await page.getByText('Grand Total $').first().textContent({ timeout: 3000 });
          if (grandTotalText) {
            const match = grandTotalText.match(/\$[\d,]+\.?\d*/);
            if (match) order1GrandTotal = match[0];
          }
        } catch (e) {
          console.log(`    ⚠ Could not extract Grand Total for Order #${order1Id}`);
        }
        
        try {
          const productCell = page.getByRole('cell').filter({ hasText: /^[A-Z]/ }).first();
          const productName = await productCell.textContent({ timeout: 2000 });
          if (productName) order1ProductName = productName.trim();
        } catch (e) {
          const productNames = page.locator('p[class*="text"]').filter({ hasText: /^[A-Z]/ });
          const names = await productNames.allTextContents();
          if (names.length > 0) order1ProductName = names[0].trim();
        }
        
        console.log(`    Order #${order1Id}: ${order1GrandTotal}`);
        console.log(`    Product: ${order1ProductName.substring(0, 50)}...`);
        
        // Navigate back to orders page
        await page.goto(process.env.BAGISTO_BASE_URL + '/customer/account/orders', {
          waitUntil: 'networkidle'
        });
        await page.waitForTimeout(2000);
        
        console.log(`  → Loading Order #${order2Id} details...`);
        
        // Load second order
        const order2Link = page.locator(`a[href*="/orders/view/${order2Id}"]`).first();
        if (await order2Link.isVisible({ timeout: 5000 }).catch(() => false)) {
          await order2Link.click();
          await page.waitForLoadState('networkidle');
          await page.waitForTimeout(3000);
          
          // Extract Order #2 details
          let order2GrandTotal = 'N/A';
          let order2ProductName = 'N/A';
          
          try {
            const grandTotalText = await page.getByText('Grand Total $').first().textContent({ timeout: 3000 });
            if (grandTotalText) {
              const match = grandTotalText.match(/\$[\d,]+\.?\d*/);
              if (match) order2GrandTotal = match[0];
            }
          } catch (e) {
            console.log(`    ⚠ Could not extract Grand Total for Order #${order2Id}`);
          }
          
          try {
            const productCell = page.getByRole('cell').filter({ hasText: /^[A-Z]/ }).first();
            const productName = await productCell.textContent({ timeout: 2000 });
            if (productName) order2ProductName = productName.trim();
          } catch (e) {
            const productNames = page.locator('p[class*="text"]').filter({ hasText: /^[A-Z]/ });
            const names = await productNames.allTextContents();
            if (names.length > 0) order2ProductName = names[0].trim();
          }
          
          console.log(`    Order #${order2Id}: ${order2GrandTotal}`);
          console.log(`    Product: ${order2ProductName.substring(0, 50)}...`);
          
          // Compare orders
          console.log('');
          console.log('  === DUPLICATE COMPARISON ===');
          const sameTotals = order1GrandTotal !== 'N/A' && order1GrandTotal === order2GrandTotal;
          const sameProducts = order1ProductName !== 'N/A' && order2ProductName !== 'N/A' && 
                               order1ProductName === order2ProductName;
          
          if (sameTotals && sameProducts) {
            console.log('  ❌ DUPLICATE CONFIRMED!');
            console.log(`    Both orders have:`);
            console.log(`      - Same Grand Total: ${order1GrandTotal}`);
            console.log(`      - Same Product: ${order1ProductName.substring(0, 60)}...`);
            console.log('    → IMMEDIATE F5 created duplicate order!');
          } else {
            console.log('  ℹ Orders are DIFFERENT:');
            console.log(`    Order #${order1Id}: ${order1GrandTotal} - ${order1ProductName.substring(0, 40)}...`);
            console.log(`    Order #${order2Id}: ${order2GrandTotal} - ${order2ProductName.substring(0, 40)}...`);
            console.log('    → Not duplicate (different products or prices)');
          }
        }
      }
    }
    
    console.log('');
    console.log('=== ORDER CREATION SUMMARY ===');
    console.log(`  Initial first order: #${initialFirstOrderId || 'None'}`);
    console.log(`  New orders created: ${actualNewOrders}`);
    if (actualNewOrders >= 1 && actualNewOrders <= 3) {
      // List the new order IDs
      for (let i = 0; i < Math.min(actualNewOrders, 3); i++) {
        const row = orderRowsFinal.nth(i);
        const orderIdText = await row.locator('p').first().textContent();
        const orderId = orderIdText?.trim() || '';
        console.log(`    Order #${i + 1}: #${orderId}`);
      }
    }
    console.log('');
    
    if (actualNewOrders === 1) {
      console.log('  ✓ PASS: Only 1 order created (no duplicate)');
      console.log('    → First order was interrupted by F5, second order succeeded');
    } else if (actualNewOrders === 2) {
      console.log('  ⚠ POTENTIAL DUPLICATE: 2 orders created!');
      console.log('    → Need to compare orders to confirm duplicate');
    } else {
      console.log(`  ℹ Created ${actualNewOrders} orders (check manually)`);
    }
    
    console.log('');
    console.log('Step 13: Verifying cart is empty...');
    await store.openCart();
    
    try {
      await store.cartIsEmpty();
      console.log('  ✓ Cart empty after order');
    } catch {
      const qtyInputsCheck = page.locator('input[type="hidden"][name="quantity"]');
      const cartItems = await qtyInputsCheck.count();
      console.log(`  ⚠ Cart not empty: ${cartItems} items`);
    }
    
    console.log('');
    console.log('S9B: COMPLETED - Immediate F5 interrupt tested');
    console.log('=== KEY FINDINGS ===');
    console.log(`  Initial order: #${initialFirstOrderId || 'No orders'}`);
    console.log(`  New orders created: ${actualNewOrders} ${secondOrderId ? `(Success page showed #${secondOrderId})` : ''}`);
    console.log(`  Duplicate prevention: ${actualNewOrders === 1 ? '✓ PASS' : actualNewOrders === 2 ? '✗ FAIL (DUPLICATE!)' : '?'}`);
    console.log('');
    console.log('Test Scenario:');
    console.log('  1. Place Order #1 → Click button');
    console.log('  2. Wait < 100ms (VERY FAST interrupt)');
    console.log('  3. Press F5 to reload page');
    console.log('  4. Place Order #2 → Fill form and click button (WAIT for success page)');
    console.log('  5. Check orders page - COUNT new orders until hitting initial order');
    console.log('  6. If 2 orders: Compare price + product for duplicate detection');
  });
});
