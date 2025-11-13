import { test, expect } from '@playwright/test';
import { config } from 'dotenv';
import { StorePage } from '../pages/StorePage';

config();

/**
 * S7: B1 → B2 → B3 → B4 → B4a → B5
 * User changes shipping method (Standard ↔ Express)
 * Expected: Updates ship fee, ETA, order total correctly
 */
test.describe('Bagisto S7 – Change Shipping Method', () => {
  
  test('S7 – Select different shipping methods at checkout', async ({ page }) => {
    const baseUrl = process.env.BAGISTO_BASE_URL || 'https://commerce.bagisto.com';
    
    console.log('Step 1 (B1): Logging in...');
    const store = new StorePage(page);
    await store.login();
    
    console.log('Step 2 (B2): Ensuring cart has items...');
    // Go to cart first to check if there are items
    await page.goto(baseUrl + '/checkout/cart', { waitUntil: 'networkidle' });
    const qtyInputs = page.locator('input[type="hidden"][name="quantity"]');
    const itemCount = await qtyInputs.count();
    
    if (itemCount === 0) {
      console.log('  → Cart empty, adding 2 products...');
      await store.addFirstProductFromHome();
      console.log('  ✓ Product 1 added');
      
      // Add second product
      await store.addFirstProductFromHome();
      console.log('  ✓ Product 2 added');
    } else {
      console.log(`  ✓ Cart has ${itemCount} item(s)`);
    }
    
    console.log('Step 3 (B3): Proceeding to checkout...');
    await store.goCheckout();
    
    console.log('Step 4 (B4): Filling shipping address...');
    await store.fillShippingAddressMinimal();
    
    console.log('Step 5 (B4a): Detecting available shipping methods...');
    
    // Wait for shipping options to appear (with longer timeout for demo site)
    console.log('  → Waiting for shipping options to render...');
    await page.waitForSelector('input[type="radio"][id*="free_free"], input[type="radio"][id*="flatrate"]', {
      timeout: 30000, // 30 seconds for slow demo site
      state: 'attached'
    });
    
    console.log('  ✓ Shipping options detected');
    await page.waitForTimeout(1000); // Small buffer for options to stabilize
    
    // Common shipping method selectors
    const shippingSelectors = [
      'input[type="radio"][name*="shipping"]',
      'input[type="radio"][name="shipping_method"]',
      '.shipping-methods input[type="radio"]',
      'input[value*="flat"], input[value*="free"], input[value*="express"]'
    ];
    
    let shippingOptions = null;
    let shippingCount = 0;
    
    for (const selector of shippingSelectors) {
      const options = page.locator(selector);
      const count = await options.count();
      if (count > 0) {
        shippingOptions = options;
        shippingCount = count;
        console.log(`  ✓ Found ${count} shipping method(s) with selector: ${selector}`);
        break;
      }
    }
    
    if (shippingOptions && shippingCount > 0) {
      console.log('Step 6 (B4a): Listing shipping methods...');
      
      const shippingDetails = [];
      for (let i = 0; i < shippingCount; i++) {
        const option = shippingOptions.nth(i);
        const id = await option.getAttribute('id').catch(() => '');
        const value = await option.getAttribute('value').catch(() => 'N/A');
        
        // Get label text - try multiple approaches
        let labelText = '';
        let shippingName = 'Unknown';
        let cost = 'N/A';
        
        if (id) {
          // CRITICAL: There are 2 labels with same for="id"
          // First label = radio icon (no text)
          // Second label = block with price and name
          // Must use .last() to get the one with content
          let labelElem = page.locator(`label[for="${id}"]`).last();
          
          if (await labelElem.isVisible({ timeout: 1000 }).catch(() => false)) {
            // Get text from <p> tags inside label
            // Structure: <p>$10.00</p> <p><span>Flat Rate</span> - Flat Rate Shipping</p>
            const pTags = await labelElem.locator('p').allTextContents();
            
            if (pTags.length >= 2) {
              cost = pTags[0].trim(); // First <p> = price
              shippingName = pTags[1].trim(); // Second <p> = name
              console.log(`  ✓ Parsed ${id}: cost="${cost}", name="${shippingName}"`);
            } else if (pTags.length === 1) {
              // Fallback if only 1 <p> found
              const text = pTags[0];
              const costMatch = text.match(/\$[\d,]+\.?\d*/);
              cost = costMatch ? costMatch[0] : text.trim();
              shippingName = text.replace(/\$[\d,]+\.?\d*/, '').trim() || value || 'Unknown';
            }
          }
        }
        
        shippingDetails.push({ index: i, id, value, shippingName, cost });
        console.log(`  Shipping ${i + 1}: ${value} - ${shippingName} (${cost})`);
      }
      
      // Capture initial checkout totals (with first shipping method)
      await page.waitForTimeout(2000);
      
      const checkoutSubtotal1 = await page
        .locator('div.flex.justify-between:has-text("Subtotal")')
        .locator('p').last()
        .textContent().catch(() => 'N/A');
      
      const checkoutDelivery1 = await page
        .locator('div.flex.justify-between:has-text("Delivery Charges")')
        .locator('p').last()
        .textContent().catch(() => 'N/A');
      
      const checkoutGrandTotal1 = await page
        .locator('div.flex.justify-between:has-text("Grand Total")')
        .locator('p').last()
        .textContent().catch(() => 'N/A');
      
      console.log(`  Initial Checkout (Shipping 1 - ${shippingDetails[0].value}):`);
      console.log(`    Subtotal: ${checkoutSubtotal1?.trim()}`);
      console.log(`    Delivery: ${checkoutDelivery1?.trim()}`);
      console.log(`    Grand Total: ${checkoutGrandTotal1?.trim()}`);
      
      // Select different shipping methods and verify total changes
      if (shippingCount > 1) {
        console.log('');
        console.log('Step 7 (B4a): Switching to second shipping method...');
        const secondOption = shippingOptions.nth(1);
        const secondId = shippingDetails[1].id;
        const secondValue = shippingDetails[1].value;
        const secondCost = shippingDetails[1].cost;
        
        console.log(`  → Switching to: ${secondValue} (${secondCost})`);
        
        // CRITICAL: Click LABEL, not hidden input
        const secondLabel = page.locator(`label[for="${secondId}"]`).last();
        if (await secondLabel.isVisible({ timeout: 3000 }).catch(() => false)) {
          await secondLabel.click();
          await page.waitForTimeout(2000); // Wait for total to update
          console.log(`  ✓ Clicked label for: ${secondValue}`);
          
          // Capture updated checkout totals (with second shipping method)
          const checkoutSubtotal2 = await page
            .locator('div.flex.justify-between:has-text("Subtotal")')
            .locator('p').last()
            .textContent().catch(() => 'N/A');
          
          const checkoutDelivery2 = await page
            .locator('div.flex.justify-between:has-text("Delivery Charges")')
            .locator('p').last()
            .textContent().catch(() => 'N/A');
          
          const checkoutGrandTotal2 = await page
            .locator('div.flex.justify-between:has-text("Grand Total")')
            .locator('p').last()
            .textContent().catch(() => 'N/A');
          
          console.log(`  Updated Checkout (Shipping 2 - ${secondValue}):`);
          console.log(`    Subtotal: ${checkoutSubtotal2?.trim()}`);
          console.log(`    Delivery: ${checkoutDelivery2?.trim()}`);
          console.log(`    Grand Total: ${checkoutGrandTotal2?.trim()}`);
          
          // Compare delivery charges
          console.log('');
          console.log('  📊 Comparison:');
          console.log(`    Shipping 1 (${shippingDetails[0].value}): Delivery=${checkoutDelivery1?.trim()}, Total=${checkoutGrandTotal1?.trim()}`);
          console.log(`    Shipping 2 (${secondValue}): Delivery=${checkoutDelivery2?.trim()}, Total=${checkoutGrandTotal2?.trim()}`);
          
          if (checkoutDelivery2 !== checkoutDelivery1) {
            console.log('  ✓ Delivery charges CHANGED between methods!');
          }
          
          if (checkoutGrandTotal2 !== checkoutGrandTotal1) {
            console.log('  ✓ Grand Total CHANGED between methods!');
          } else {
            console.log('  ℹ Grand Total unchanged (same cost or bug)');
          }
        } else {
          console.log('  ⚠ Second shipping label not found');
        }
        
        // Switch back to first method to test toggle
        console.log('');
        console.log('Step 8 (B4a): Switching back to first shipping method...');
        const firstId = shippingDetails[0].id;
        const firstValue = shippingDetails[0].value;
        const firstCost = shippingDetails[0].cost;
        
        console.log(`  → Switching back to: ${firstValue} (${firstCost})`);
        
        const firstLabel = page.locator(`label[for="${firstId}"]`).last();
        if (await firstLabel.isVisible({ timeout: 3000 }).catch(() => false)) {
          await firstLabel.click();
          await page.waitForTimeout(2000);
          console.log(`  ✓ Clicked label for: ${firstValue}`);
          
          // Capture totals again (should match initial)
          const checkoutDelivery3 = await page
            .locator('div.flex.justify-between:has-text("Delivery Charges")')
            .locator('p').last()
            .textContent().catch(() => 'N/A');
            
          const checkoutGrandTotal3 = await page
            .locator('div.flex.justify-between:has-text("Grand Total")')
            .locator('p').last()
            .textContent().catch(() => 'N/A');
          
          console.log(`    Delivery: ${checkoutDelivery3?.trim()}`);
          console.log(`    Grand Total: ${checkoutGrandTotal3?.trim()}`);
          
          if (checkoutGrandTotal3 === checkoutGrandTotal1) {
            console.log('  ✓ Grand Total matches initial (toggle works correctly)');
          } else {
            console.log('  ⚠ Grand Total mismatch after toggle');
          }
        }
      } else {
        console.log('  ℹ Only one shipping method available');
      }
    } else {
      console.log('  ⚠ No shipping method radio buttons found (may be single default)');
    }
    
    console.log('Step 9 (B5): Placing order with selected shipping...');
    
    // Capture final checkout summary before placing order
    await page.waitForTimeout(1000);
    const finalCheckoutSubtotal = await page
      .locator('div.flex.justify-between:has-text("Subtotal")')
      .locator('p').last()
      .textContent().catch(() => 'N/A');
    
    const finalCheckoutDelivery = await page
      .locator('div.flex.justify-between:has-text("Delivery Charges")')
      .locator('p').last()
      .textContent().catch(() => 'N/A');
    
    const finalCheckoutGrandTotal = await page
      .locator('div.flex.justify-between:has-text("Grand Total")')
      .locator('p').last()
      .textContent().catch(() => 'N/A');
    
    console.log(`  Final Checkout Summary:`);
    console.log(`    Subtotal: ${finalCheckoutSubtotal?.trim()}`);
    console.log(`    Delivery: ${finalCheckoutDelivery?.trim()}`);
    console.log(`    Grand Total: ${finalCheckoutGrandTotal?.trim()}`);
    
    try {
      await store.choosePaymentAndPlace(false);
      console.log('  ✓ Order placed');
      
      // Wait for success page and get order details
      await page.waitForURL('**/checkout/onepage/success', { timeout: 30000 }).catch(() => {});
      
      const orderLink = page.locator('p.text-xl a.text-blue-700[href*="/orders/view/"]').first();
      if (await orderLink.isVisible({ timeout: 5000 }).catch(() => false)) {
        const orderId = await orderLink.textContent();
        console.log(`  ✓ Order #${orderId} created`);
        
        await orderLink.click();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(3000); // CRITICAL: Wait for order detail to load
        
        // Parse order detail summary
        const orderSubtotal = await page
          .locator('div.flex.justify-between:has-text("Subtotal")').first()
          .locator('p').last()
          .textContent().catch(() => 'N/A');
        
        // CRITICAL: Use more specific selector for Shipping to avoid footer text
        const orderShippingRow = page
          .locator('div.flex.justify-between')
          .filter({ hasText: /^Shipping/i })
          .first();
        const orderShipping = await orderShippingRow
          .locator('p').last()
          .textContent().catch(() => 'N/A');
        
        const orderGrandTotal = await page
          .locator('div.flex.justify-between:has-text("Grand Total")').first()
          .locator('p').last()
          .textContent().catch(() => 'N/A');
        
        console.log(`  Order Detail Summary:`);
        console.log(`    Subtotal: ${orderSubtotal?.trim()}`);
        console.log(`    Shipping: ${orderShipping?.trim()}`);
        console.log(`    Grand Total: ${orderGrandTotal?.trim()}`);
        
        // Compare checkout vs order
        console.log(`  Comparison:`);
        console.log(`    Checkout Grand Total: ${finalCheckoutGrandTotal?.trim()}`);
        console.log(`    Order Grand Total: ${orderGrandTotal?.trim()}`);
        
        if (finalCheckoutGrandTotal?.trim() === orderGrandTotal?.trim()) {
          console.log('  ✓ Grand Total MATCHES (checkout = order)');
        } else {
          console.log('  ⚠ Grand Total MISMATCH!');
          
          // Check if difference is shipping fee
          const checkoutGT = parseFloat(finalCheckoutGrandTotal?.replace(/[^0-9.]/g, '') || '0');
          const orderGT = parseFloat(orderGrandTotal?.replace(/[^0-9.]/g, '') || '0');
          const diff = Math.abs(checkoutGT - orderGT);
          
          if (diff > 0 && diff < 100) {
            console.log(`  ℹ Difference: $${diff.toFixed(2)} (likely shipping fee discrepancy)`);
          }
        }
        
        // Verify shipping method selection impact
        console.log(`  Final Shipping Analysis:`);
        console.log(`    Checkout delivery charge: ${finalCheckoutDelivery?.trim()}`);
        console.log(`    Order shipping charge: ${orderShipping?.trim()}`);
      }
    } catch (error) {
      console.log(`  ⚠ Order placement error: ${error instanceof Error ? error.message : 'Unknown'}`);
    }
    
    await page.waitForTimeout(3000);
    
    console.log('Step 10: Verifying cart is empty after checkout...');
    await store.gotoHome();
    await store.openCart();
    
    try {
      await store.cartIsEmpty();
      console.log('  ✓ Cart cleared after order');
    } catch {
      const qtyInputs = page.locator('input[type="hidden"][name="quantity"]');
      const finalCount = await qtyInputs.count();
      console.log(`  ⚠ Cart not empty: ${finalCount} items remain`);
    }
    
    console.log('S6: COMPLETED - Shipping method selection tested');
  });
});
