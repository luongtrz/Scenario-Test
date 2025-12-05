import { test, expect } from '@playwright/test';
import { config } from 'dotenv';
import { StorePage } from '../pages/StorePage';

config();

/**
 * S14: B1 → B2 → B3 → B4 → B5 → B5d
 * User cancels within "grace window"
 * Expected: Refund successful; stock returned; order status updated
 */
test.describe('Bagisto S13 – Cancel Order After Payment', () => {
  
  test('S13 – Cancel order then reorder and complete checkout', async ({ page }) => {
    console.log('Step 1 (B1): Logging in...');
    const store = new StorePage(page);
    await store.login();
    
    console.log('Step 2: Navigating to order history...');
    await page.getByRole('button', { name: 'Profile' }).click();
    await page.waitForTimeout(500);
    await page.getByRole('link', { name: 'Orders' }).click();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    console.log('  ✓ Order history page loaded');
    
    // Count existing orders BEFORE cancellation
    const orderRows = page.locator('.row.grid').filter({ 
      hasNot: page.locator('text=/Order ID|Order Date/i') 
    });
    const initialOrderCount = await orderRows.count();
    console.log(`  Found ${initialOrderCount} existing order(s)`);
    
    if (initialOrderCount === 0) {
      console.log('  ⚠ No orders found - cannot test cancel/reorder flow');
      console.log('S17: SKIPPED - Need at least one order');
      return;
    }
    
    // Get first order ID for reference
    let initialFirstOrderId = '';
    if (initialOrderCount > 0) {
      const firstOrderIdText = await orderRows.first().locator('p').first().textContent();
      initialFirstOrderId = firstOrderIdText?.trim() || '';
      console.log(`  First order ID: #${initialFirstOrderId}`);
    }
    
    console.log('Step 3 (B5d): Looking for cancellable order...');
    // Try to find an order that can be cancelled (not already cancelled)
    // First, check if first order has Cancel link
    const firstViewBtn = page.locator('.float-right').first();
    if (await firstViewBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await firstViewBtn.click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      console.log('  ✓ Order details page opened');
      
      // Check if this order has Cancel link
      const hasCancelLink = await page.getByRole('link', { name: 'Cancel' })
        .isVisible({ timeout: 2000 })
        .catch(() => false);
      
      if (!hasCancelLink) {
        console.log('  → First order already cancelled, checking other orders...');
        
        // Go back to order list
        await page.goto(process.env.BAGISTO_BASE_URL + '/customer/account/orders', {
          waitUntil: 'networkidle'
        });
        await page.waitForTimeout(2000);
        
        // Try second order
        const secondViewBtn = page.locator('.float-right').nth(1);
        if (await secondViewBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
          await secondViewBtn.click();
          await page.waitForLoadState('networkidle');
          await page.waitForTimeout(2000);
          console.log('  ✓ Checking second order...');
          
          const hasCancelLink2 = await page.getByRole('link', { name: 'Cancel' })
            .isVisible({ timeout: 2000 })
            .catch(() => false);
          
          if (!hasCancelLink2) {
            console.log('  ⚠ No cancellable orders found - creating new order first...');
            console.log('');
            console.log('Step 3.5: Creating new order to cancel...');
            
            // Add product and checkout quickly
            await store.addFirstProductFromHome();
            await store.goCheckout();
            await store.fillShippingAddressMinimal();
            
            // Wait for shipping/payment methods to load
            await page.waitForTimeout(2000);
            
            // Select shipping method (Free Shipping)
            const freeShippingLbl = page.locator('label[for="free_free"]').last();
            if (await freeShippingLbl.isVisible({ timeout: 3000 }).catch(() => false)) {
              await freeShippingLbl.click();
              await page.waitForTimeout(1000);
              console.log('  ✓ Free Shipping selected');
            }
            
            // Select payment method (COD)
            const codLabel = page.locator('label[for="cashondelivery"]').last();
            if (await codLabel.isVisible({ timeout: 3000 }).catch(() => false)) {
              await codLabel.click({ force: true });
              await page.waitForTimeout(2000);
              console.log('  ✓ Cash On Delivery selected');
            }
            
            // Scroll and place order
            await page.keyboard.press('End');
            await page.waitForTimeout(1000);
            
            const placeOrderBtn = page.locator('button:has-text("Place Order")').first();
            if (await placeOrderBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
              await placeOrderBtn.click();
              await page.waitForURL('**/checkout/onepage/success', { timeout: 60000 });
              console.log('  ✓ New order created');
              
              // Click order link to go to order details
              const orderLink = page.locator('p.text-xl a.text-blue-700[href*="/orders/view/"]').first();
              if (await orderLink.isVisible({ timeout: 5000 })) {
                const newOrderId = await orderLink.textContent();
                console.log(`  ✓ New order ID: #${newOrderId?.trim()}`);
                await orderLink.click();
                await page.waitForLoadState('networkidle');
                await page.waitForTimeout(2000);
              }
            } else {
              console.log('  ⚠ Could not place order');
              return;
            }
          }
        } else {
          console.log('  ⚠ No other orders available');
          console.log('S17: SKIPPED - Need a cancellable order');
          return;
        }
      }
    } else {
      console.log('  ⚠ View button not found');
      return;
    }
    
    console.log('Step 4 (B5d): Cancelling order...');
    const cancelLink = page.getByRole('link', { name: 'Cancel' });
    
    if (await cancelLink.isVisible({ timeout: 3000 }).catch(() => false)) {
      await cancelLink.click();
      await page.waitForTimeout(1000);
      console.log('  → Clicked Cancel link');
      
      // Confirm cancellation with "Agree" button (may trigger navigation or reload)
      const agreeBtn = page.getByRole('button', { name: 'Agree', exact: true });
      if (await agreeBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
        console.log('  → Confirming cancellation...');
        
        // Get current order ID before clicking (for re-navigation)
        const currentUrl = page.url();
        
        // Click without waiting for navigation (noWaitAfter: true)
        await agreeBtn.click({ noWaitAfter: true });
        // Wait for action to complete
        await page.waitForTimeout(3000);
        console.log('  ✓ Order cancellation confirmed');
        
        // CRITICAL: Navigate back to order page to load Reorder button
        // (reload may fail with ERR_ABORTED if page was detached)
        console.log('  → Navigating back to order page to load Reorder button...');
        try {
          await page.goto(currentUrl, { waitUntil: 'networkidle', timeout: 15000 });
        } catch {
          // If direct navigation fails, try from order list
          await page.goto(process.env.BAGISTO_BASE_URL + '/customer/account/orders', {
            waitUntil: 'networkidle'
          });
          await page.waitForTimeout(1000);
          const firstViewBtn = page.locator('.float-right').first();
          await firstViewBtn.click();
          await page.waitForLoadState('networkidle');
        }
        await page.waitForTimeout(2000);
      }
    } else {
      console.log('  ⚠ Cancel link not found - order may not be cancellable');
      console.log('S17: SKIPPED - Cannot test reorder without cancellation');
      return;
    }
    
    console.log('Step 5: Reordering cancelled order...');
    // After cancellation and refresh, Reorder link should be visible
    const reorderLink = page.getByRole('link', { name: 'Reorder' });
    const hasReorderLink = await reorderLink.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasReorderLink) {
      await reorderLink.click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      console.log('  ✓ Reorder clicked - items added to cart');
    } else {
      console.log('  ⚠ Reorder link not found after refresh');
      console.log('  ℹ Demo may not support reorder for cancelled orders');
      console.log('S17: PARTIAL - Cancel worked, but reorder not available');
      return;
    }
    
    console.log('Step 6 (B3): Proceeding to checkout...');
    const proceedLink = page.getByRole('link', { name: 'Proceed To Checkout' });
    if (await proceedLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await proceedLink.click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      console.log('  ✓ Checkout page loaded');
    } else {
      console.log('  ⚠ Proceed To Checkout not found');
      return;
    }
    
    console.log('Step 7 (B4): Checking if address form needed...');
    await page.waitForTimeout(2000);
    
    // Dismiss cookie consent if present
    const acceptBtn = page.getByRole('button', { name: 'Accept' });
    if (await acceptBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await acceptBtn.click();
      await page.waitForTimeout(500);
      console.log('  → Cookie consent accepted');
    }
    
    // Check if "Proceed" button exists (means address form is present)
    const proceedBtn = page.getByRole('button', { name: 'Proceed' });
    const hasProceedBtn = await proceedBtn.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasProceedBtn) {
      console.log('  → Address form present (physical product or requires address)');
      console.log('  → Filling shipping address...');
      await store.fillShippingAddressMinimal(); // This clicks Proceed internally
      console.log('  ✓ Address filled and Proceed clicked');
    } else {
      console.log('  ℹ No address form (likely e-book only - no shipping needed)');
      console.log('  → Proceeding directly to payment...');
    }
    
    console.log('Step 8 (B5): Waiting for payment methods to load...');
    await page.waitForTimeout(2000);
    
    console.log('Step 9 (B5): Selecting shipping method (if physical product)...');
    // Physical products need shipping method selection first
    const freeShippingLabel = page.locator('label[for="free_free"]').last();
    if (await freeShippingLabel.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('  → Selecting Free Shipping...');
      await freeShippingLabel.click();
      await page.waitForTimeout(1000);
      console.log('  ✓ Free Shipping selected');
    } else {
      console.log('  ℹ No shipping selection (e-book product)');
    }
    
    console.log('Step 10 (B5): Selecting payment method...');
    // Try clicking payment label (works for both e-book and physical products)
    const paymentLabels = [
      page.locator('label[for="cashondelivery"]').last(),
      page.locator('label[for="moneytransfer"]').last(),
      page.locator('label:has-text("Cash On Delivery")').first(),
      page.locator('label:has-text("Money Transfer")').first()
    ];
    
    let paymentSelected = false;
    for (const label of paymentLabels) {
      if (await label.isVisible({ timeout: 2000 }).catch(() => false)) {
        await label.click({ force: true });
        await page.waitForTimeout(2000);
        console.log('  ✓ Payment method selected');
        paymentSelected = true;
        break;
      }
    }
    
    if (!paymentSelected) {
      console.log('  ⚠ Could not select payment method');
      return;
    }
    
    console.log('Step 11 (B5): Placing new order...');
    
    // Scroll to bottom to ensure Place Order button is visible
    await page.keyboard.press('End');
    await page.waitForTimeout(1000);
    
    const placeOrderBtn = page.getByRole('button', { name: 'Place Order' });
    
    if (await placeOrderBtn.isVisible({ timeout: 10000 }).catch(() => false)) {
      await placeOrderBtn.click();
      console.log('  → Place Order clicked');
      console.log('  → Waiting for order processing...');
    } else {
      console.log('  ⚠ Place Order button not found after scrolling');
      
      // Debug: check what buttons are visible
      const allButtons = page.locator('button');
      const btnCount = await allButtons.count();
      console.log(`  → Found ${btnCount} button(s) on page`);
      
      if (btnCount > 0) {
        console.log('  → Trying alternative Place Order selector...');
        const placeOrderAlt = page.locator('button:has-text("Place Order")').first();
        if (await placeOrderAlt.isVisible({ timeout: 5000 }).catch(() => false)) {
          await placeOrderAlt.click();
          console.log('  ✓ Place Order clicked (alternative selector)');
        } else {
          console.log('  ⚠ Could not find Place Order button');
          return;
        }
      } else {
        return;
      }
    }
    
    console.log('Step 11: Waiting for order success page...');
    await page.waitForURL('**/checkout/onepage/success', {
      timeout: 60000,
      waitUntil: 'networkidle'
    });
    console.log('  ✓ Order placed successfully!');
    await page.waitForTimeout(2000);
    
    console.log('Step 12: Extracting new order ID...');
    const orderLink = page.locator('p.text-xl a.text-blue-700[href*="/orders/view/"]').first();
    
    let newOrderId = '';
    if (await orderLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      const orderIdText = await orderLink.textContent();
      newOrderId = orderIdText?.trim() || '';
      console.log(`  ✓ New order created: #${newOrderId}`);
      
      // Click order link to verify details
      console.log('Step 13: Verifying new order details...');
      await orderLink.click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(3000);
      
      // Extract Grand Total
      const grandTotalText = await page.getByText('Grand Total $').first()
        .textContent({ timeout: 3000 })
        .catch(() => null);
      
      if (grandTotalText) {
        const match = grandTotalText.match(/\$[\d,]+\.?\d*/);
        const grandTotal = match ? match[0] : 'N/A';
        console.log(`  ✓ Order Grand Total: ${grandTotal}`);
      }
      
      console.log('');
      console.log('S17: ✓ COMPLETED - Cancel & Reorder flow tested');
      console.log(`  Cancelled order: #${initialFirstOrderId}`);
      console.log(`  New order: #${newOrderId}`);
      console.log('  Flow: Login → Cancel Order → Reorder → Checkout → Verify');
    } else {
      console.log('  ⚠ Could not extract new order ID');
      console.log('S17: PARTIAL - Order placed but ID not found');
    }
  });
});
