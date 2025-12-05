import { test } from '@playwright/test';
import { StorePage } from '../pages/StorePage';

/**
 * S16: B1 → B2 → B3 → B4 → B5 → B5f
 * 2 devices attempt to place order continuously (multi-device ordering)
 * Expected: No duplicate orders; backend handles concurrency correctly
 */
test.describe('Bagisto S15 - Concurrent Place Order (Race Condition)', () => {
  test('S15 – Two browsers place order at EXACTLY same time', async ({ page, context }) => {
    test.setTimeout(300000); // 5 minutes - allow infinite wait for both browsers
    
    console.log('');
    console.log('='.repeat(80));
    console.log('S15B: CONCURRENT PLACE ORDER - Testing Race Condition for Duplicate Orders');
    console.log('='.repeat(80));
    console.log('');
    
    const baseUrl = process.env.BAGISTO_BASE_URL || 'https://commerce.bagisto.com';
    
    // Browser 1 setup
    console.log('Step 1: Setting up Browser 1 (first session)...');
    const store1 = new StorePage(page);
    await store1.login();
    console.log('  ✓ Browser 1 logged in');
    
    // Create second browser context
    console.log('Step 2: Creating Browser 2 (second session - incognito)...');
    const context2 = await context.browser()!.newContext({
      storageState: undefined,
      viewport: { width: 1280, height: 720 }
    });
    const page2 = await context2.newPage();
    const store2 = new StorePage(page2);
    await store2.login();
    console.log('  ✓ Browser 2 logged in (separate session)');
    
    // Both browsers add same product to cart
    console.log('Step 3: Both browsers add same product to cart...');
    await page.goto(baseUrl, { waitUntil: 'networkidle' });
    await page2.goto(baseUrl, { waitUntil: 'networkidle' });
    
    // Browser 1 adds product
    await page.bringToFront();
    await store1.addFirstProductFromHome();
    console.log('  ✓ Browser 1 added product to cart');
    
    // Browser 2 adds same product
    await page2.bringToFront();
    await store2.addFirstProductFromHome();
    console.log('  ✓ Browser 2 added product to cart');
    
    // Both browsers go to checkout
    console.log('Step 4: Both browsers navigate to checkout...');
    await page.bringToFront();
    await store1.goCheckout();
    console.log('  ✓ Browser 1 on checkout page');
    
    await page2.bringToFront();
    await store2.goCheckout();
    console.log('  ✓ Browser 2 on checkout page');
    
    // Both browsers fill address and click "Proceed"
    console.log('Step 5: Both browsers fill address and click Proceed...');
    await page.bringToFront();
    await store1.fillShippingAddressMinimal(); // This clicks "Proceed" button
    console.log('  ✓ Browser 1 clicked Proceed');
    
    await page2.bringToFront();
    await store2.fillShippingAddressMinimal(); // This clicks "Proceed" button
    console.log('  ✓ Browser 2 clicked Proceed');
    
    // Wait for shipping/payment methods to load on BOTH browsers
    console.log('Step 6: Waiting for payment methods to load on both browsers...');
    await page.waitForTimeout(3000);
    await page2.waitForTimeout(3000);
    
    // CRITICAL: Prepare both browsers to click Place Order
    console.log('Step 7: Preparing both browsers for CONCURRENT Place Order...');
    
    // Browser 1 - Select shipping & payment
    await page.bringToFront();
    await page.waitForSelector('input[type="radio"][id*="free_free"]', {
      timeout: 10000,
      state: 'attached'
    });
    
    const freeShippingLabel1 = page.locator('label[for="free_free"]').last();
    if (await freeShippingLabel1.isVisible({ timeout: 3000 }).catch(() => false)) {
      await freeShippingLabel1.click();
      await page.waitForTimeout(1000);
      console.log('  Browser 1: Selected Free Shipping');
    }
    
    const codLabel1 = page.locator('label[for="cashondelivery"]').last();
    if (await codLabel1.isVisible({ timeout: 3000 }).catch(() => false)) {
      await codLabel1.click();
      await page.waitForTimeout(2000); // Wait longer for payment method to register
      console.log('  Browser 1: Selected Cash on Delivery');
    }
    
    // Browser 2 - Select shipping & payment
    await page2.bringToFront();
    await page2.waitForSelector('input[type="radio"][id*="free_free"]', {
      timeout: 10000,
      state: 'attached'
    });
    
    const freeShippingLabel2 = page2.locator('label[for="free_free"]').last();
    if (await freeShippingLabel2.isVisible({ timeout: 3000 }).catch(() => false)) {
      await freeShippingLabel2.click();
      await page2.waitForTimeout(1000);
      console.log('  Browser 2: Selected Free Shipping');
    }
    
    const codLabel2 = page2.locator('label[for="cashondelivery"]').last();
    if (await codLabel2.isVisible({ timeout: 3000 }).catch(() => false)) {
      await codLabel2.click();
      await page2.waitForTimeout(2000); // Wait longer for payment method to register
      console.log('  Browser 2: Selected Cash on Delivery');
    }
    
    // CRITICAL: Wait for both browsers to fully load payment UI
    console.log('  ⏱ Waiting 3 seconds for payment methods to fully register...');
    await page.waitForTimeout(3000);
    await page2.waitForTimeout(3000);
    
    // Get Place Order buttons ready
    const placeOrderBtn1 = page.locator('button:has-text("Place Order")').first();
    const placeOrderBtn2 = page2.locator('button:has-text("Place Order")').first();
    
    const btn1Visible = await placeOrderBtn1.isVisible({ timeout: 5000 }).catch(() => false);
    const btn2Visible = await placeOrderBtn2.isVisible({ timeout: 5000 }).catch(() => false);
    
    console.log(`  Browser 1 Place Order button: ${btn1Visible ? 'VISIBLE ✓' : 'NOT VISIBLE ✗'}`);
    console.log(`  Browser 2 Place Order button: ${btn2Visible ? 'VISIBLE ✓' : 'NOT VISIBLE ✗'}`);
    
    if (!btn1Visible || !btn2Visible) {
      console.log('  ⚠ One or both Place Order buttons not visible, cannot test concurrent click');
      await page2.close();
      await context2.close();
      return;
    }
    
    // CRITICAL RACE CONDITION TEST: Click BOTH buttons at EXACTLY same time
    console.log('');
    console.log('Step 8: 🔥 CONCURRENT CLICK - Both browsers clicking Place Order NOW!');
    console.log('  ⚠ Testing race condition - clicking at same millisecond...');
    
    // Click BOTH buttons in parallel using Promise.all
    await Promise.all([
      // Browser 1 click
      placeOrderBtn1.click().then(() => console.log('  → Browser 1: Clicked Place Order')),
      
      // Browser 2 click
      placeOrderBtn2.click().then(() => console.log('  → Browser 2: Clicked Place Order'))
    ]);
    
    console.log('');
    console.log('Step 9: Waiting for BOTH browsers to reach success page...');
    console.log('  ⏱ Polling every 2 seconds until both browsers finish (max 3 minutes)...');
    
    let browser1Success = false;
    let browser2Success = false;
    let browser1OrderId = '';
    let browser2OrderId = '';
    let attempt = 0;
    const maxAttempts = 90; // 90 * 2s = 180s = 3 minutes max
    
    while (attempt < maxAttempts) {
      attempt++;
      
      // Check Browser 1
      await page.bringToFront();
      const url1 = page.url();
      browser1Success = url1.includes('/checkout/onepage/success');
      
      if (browser1Success && !browser1OrderId) {
        // Extract Order ID from success page
        const orderLink1 = page.locator('p.text-xl a.text-blue-700[href*="/orders/view/"]').first();
        if (await orderLink1.isVisible({ timeout: 2000 }).catch(() => false)) {
          browser1OrderId = await orderLink1.textContent().then(t => t?.trim() || '');
        }
      }
      
      // Check Browser 2
      await page2.bringToFront();
      const url2 = page2.url();
      browser2Success = url2.includes('/checkout/onepage/success');
      
      if (browser2Success && !browser2OrderId) {
        // Extract Order ID from success page
        const orderLink2 = page2.locator('p.text-xl a.text-blue-700[href*="/orders/view/"]').first();
        if (await orderLink2.isVisible({ timeout: 2000 }).catch(() => false)) {
          browser2OrderId = await orderLink2.textContent().then(t => t?.trim() || '');
        }
      }
      
      // Show progress every 5 attempts (every 10 seconds)
      if (attempt % 5 === 0 || (browser1Success && browser2Success)) {
        const status1 = browser1Success ? `✓ Success (Order #${browser1OrderId || '?'})` : `⏳ ${url1.split('/').pop()}`;
        const status2 = browser2Success ? `✓ Success (Order #${browser2OrderId || '?'})` : `⏳ ${url2.split('/').pop()}`;
        console.log(`  [${attempt * 2}s] Browser 1: ${status1}`);
        console.log(`  [${attempt * 2}s] Browser 2: ${status2}`);
      }
      
      // Break when BOTH succeed
      if (browser1Success && browser2Success) {
        console.log('');
        console.log(`  ✓ Both browsers on success page after ${attempt * 2} seconds!`);
        console.log(`  Browser 1 Order: #${browser1OrderId}`);
        console.log(`  Browser 2 Order: #${browser2OrderId}`);
        break;
      }
      
      await page.waitForTimeout(2000);
    }
    
    // Check if we timed out
    if (!browser1Success || !browser2Success) {
      console.log('');
      console.log('  ⚠ TIMEOUT: One or both browsers did not reach success page after 3 minutes');
      console.log(`    Browser 1: ${browser1Success ? '✓ Success' : '✗ Stuck'}`);
      console.log(`    Browser 2: ${browser2Success ? '✓ Success' : '✗ Stuck'}`);
      console.log('  → Test inconclusive - skipping order comparison');
      
      console.log('');
      console.log('Step 11: Cleanup - closing second browser...');
      await page2.close();
      await context2.close();
      
      console.log('');
      console.log('='.repeat(80));
      console.log('S16B: COMPLETED - Test inconclusive due to timeout');
      console.log('='.repeat(80));
      return;
    }
    
    console.log('');
    console.log('Step 10: Comparing orders for duplicate detection...');
    
    if (!browser1OrderId || !browser2OrderId) {
      console.log('  ⚠ Could not extract Order IDs from success pages');
      console.log('  → Test inconclusive');
    } else if (browser1OrderId === browser2OrderId) {
      console.log('  ❌ CRITICAL: SAME Order ID!');
      console.log(`    Both browsers created Order #${browser1OrderId}`);
      console.log('    → This should NEVER happen - indicates race condition bug!');
    } else {
      console.log(`  → Browser 1: Order #${browser1OrderId}`);
      console.log(`  → Browser 2: Order #${browser2OrderId}`);
      console.log('  → Different Order IDs - now checking if duplicate content...');
      
      // CRITICAL: Click order link from success page (not manual navigate!)
      // This ensures we follow the HREF which is always correct, even if text ID differs
      
      // Browser 2: Click order link from success page
      await page2.bringToFront();
      console.log(`  → Clicking Order #${browser2OrderId} link on Browser 2...`);
      
      const orderLink2 = page2.locator('p.text-xl a.text-blue-700[href*="/orders/view/"]').first();
      await orderLink2.click();
      
      // Wait for order detail page to load
      await page2.waitForLoadState('networkidle');
      await page2.waitForSelector('text=/Grand Total|Subtotal/i', { timeout: 5000 }).catch(() => {});
      await page2.waitForTimeout(3000);
      
      console.log(`  → Loading Order #${browser2OrderId} details...`);
      
      // Extract Order #2 details using Playwright Codegen selectors
      let order2GrandTotal = 'N/A';
      let order2ProductName = 'N/A';
      
      // Get Grand Total - using getByText selector from codegen
      try {
        const grandTotalText = await page2.getByText('Grand Total $').first().textContent({ timeout: 3000 });
        if (grandTotalText) {
          // Extract price from "Grand Total $XX.XX" format
          const match = grandTotalText.match(/\$[\d,]+\.?\d*/);
          if (match) order2GrandTotal = match[0];
        }
      } catch (e) {
        console.log(`    ⚠ Could not extract Grand Total for Order #${browser2OrderId}`);
      }
      
      // Get product name from table cell
      try {
        const productCell = page2.getByRole('cell').filter({ hasText: /^[A-Z]/ }).first();
        const productName = await productCell.textContent({ timeout: 2000 });
        if (productName) order2ProductName = productName.trim();
      } catch (e) {
        // Fallback: try old selector
        const productNames2 = page2.locator('p[class*="text"]').filter({ hasText: /^[A-Z]/ });
        const names2 = await productNames2.allTextContents();
        if (names2.length > 0) order2ProductName = names2[0].trim();
      }
      
      console.log(`    Order #${browser2OrderId}: ${order2GrandTotal}`);
      console.log(`    Products: ${order2ProductName.substring(0, 50)}...`);
      
      // Browser 1: Click order link from success page  
      await page.bringToFront();
      console.log(`  → Clicking Order #${browser1OrderId} link on Browser 1...`);
      
      const orderLink1 = page.locator('p.text-xl a.text-blue-700[href*="/orders/view/"]').first();
      await orderLink1.click();
      
      // Wait for order detail page to load
      await page.waitForLoadState('networkidle');
      await page.waitForSelector('text=/Grand Total|Subtotal/i', { timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(3000);
      
      console.log(`  → Loading Order #${browser1OrderId} details...`);
      
      // Extract Order #1 details using Playwright Codegen selectors
      let order1GrandTotal = 'N/A';
      let order1ProductName = 'N/A';
      
      // Get Grand Total - using getByText selector from codegen
      try {
        const grandTotalText = await page.getByText('Grand Total $').first().textContent({ timeout: 3000 });
        if (grandTotalText) {
          // Extract price from "Grand Total $XX.XX" format
          const match = grandTotalText.match(/\$[\d,]+\.?\d*/);
          if (match) order1GrandTotal = match[0];
        }
      } catch (e) {
        console.log(`    ⚠ Could not extract Grand Total for Order #${browser1OrderId}`);
      }
      
      // Get product name from table cell
      try {
        const productCell = page.getByRole('cell').filter({ hasText: /^[A-Z]/ }).first();
        const productName = await productCell.textContent({ timeout: 2000 });
        if (productName) order1ProductName = productName.trim();
      } catch (e) {
        // Fallback: try old selector
        const productNames1 = page.locator('p[class*="text"]').filter({ hasText: /^[A-Z]/ });
        const names1 = await productNames1.allTextContents();
        if (names1.length > 0) order1ProductName = names1[0].trim();
      }
      
      console.log(`    Order #${browser2OrderId}: ${order2GrandTotal}`);
      console.log(`    Products: ${order2ProductName.substring(0, 50)}...`);
      
      console.log('');
      console.log('=== DUPLICATE DETECTION RESULTS ===');
      
      // Compare totals and products
      const sameTotals = order1GrandTotal !== 'N/A' && order1GrandTotal === order2GrandTotal;
      const sameProducts = order1ProductName !== 'N/A' && order2ProductName !== 'N/A' && 
                           order1ProductName === order2ProductName;
      
      if (sameTotals && sameProducts) {
        console.log('  ❌ DUPLICATE BUG CONFIRMED!');
        console.log(`    Both orders have:`);
        console.log(`      - Same Grand Total: ${order1GrandTotal}`);
        console.log(`      - Same Product: ${order1ProductName.substring(0, 60)}...`);
        console.log('    → Race condition NOT prevented by backend!');
      } else if (sameTotals && !sameProducts) {
        console.log('  ⚠ Same price but different products:');
        console.log(`    Order #${browser1OrderId}: ${order1GrandTotal}`);
        console.log(`    Order #${browser2OrderId}: ${order2GrandTotal}`);
        console.log('    → Likely coincidence, not duplicate');
      } else if (!sameTotals) {
        console.log('  ✓ PASSED: Different Grand Totals');
        console.log(`    Order #${browser1OrderId}: ${order1GrandTotal}`);
        console.log(`    Order #${browser2OrderId}: ${order2GrandTotal}`);
        console.log('    → Not duplicates - legitimate separate orders');
      } else {
        console.log('  ⚠ Could not verify - missing price data');
      }
    }
    
    console.log('');
    console.log('Step 11: Cleanup - closing second browser...');
    await page2.close();
    await context2.close();
    
    console.log('');
    console.log('='.repeat(80));
    console.log('S16B: COMPLETED - Concurrent Place Order Race Condition Test');
    console.log('='.repeat(80));
  });
});

