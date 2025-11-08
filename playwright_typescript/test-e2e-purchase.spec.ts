/**
 * TC-E2E-001: Guest Checkout - Happy Path (Playwright TypeScript)
 * PrestaShop Demo - End-to-End Purchase Test
 * 
 * Author: QA Automation Team
 * Date: 2025-11-08
 */

import { test, expect } from '@playwright/test';

test.describe('PrestaShop E2E Purchase Tests', () => {
  
  test('TC-E2E-001: Guest user completes end-to-end purchase', async ({ page }) => {
    // Configure test timeout for longer E2E flow
    test.setTimeout(90000);
    
    console.log('🚀 Starting Playwright test...');
    
    // Step 1: Navigate to PrestaShop demo
    console.log('📍 Step 1: Navigating to PrestaShop demo...');
    await page.goto('https://demo.prestashop.com/', { waitUntil: 'domcontentloaded' });
    
    // Step 2: Switch to storefront iframe
    console.log('📍 Step 2: Switching to storefront iframe...');
    const frameLocator = page.frameLocator('#framelive');
    console.log('   ✓ Frame locator created');
    
    // Step 3: Wait for homepage to load and locate first product
    console.log('📍 Step 3: Locating product on homepage...');
    const firstProduct = frameLocator.locator('.product article .thumbnail').first();
    await firstProduct.waitFor({ state: 'visible', timeout: 15000 });
    
    // Step 4: Click on product to view details
    console.log('📍 Step 4: Opening product details...');
    await firstProduct.click();
    await page.waitForTimeout(1000);
    
    // Step 5: Add product to cart
    console.log('📍 Step 5: Adding product to cart...');
    const addToCartBtn = frameLocator.locator('button[data-button-action="add-to-cart"]');
    await addToCartBtn.waitFor({ state: 'visible' });
    await addToCartBtn.click();
    console.log('   ✓ Product added to cart');
    
    // Step 6: Proceed to checkout from modal
    console.log('📍 Step 6: Proceeding to checkout from modal...');
    const proceedCheckoutModal = frameLocator.locator('.cart-content-btn .btn-primary');
    await proceedCheckoutModal.waitFor({ state: 'visible', timeout: 10000 });
    await proceedCheckoutModal.click();
    await page.waitForTimeout(2000);
    
    // Step 7: Proceed to checkout from cart page
    console.log('📍 Step 7: Confirming cart and proceeding to checkout...');
    const proceedCheckoutCart = frameLocator.locator('.checkout a.btn-primary');
    await proceedCheckoutCart.waitFor({ state: 'visible' });
    await proceedCheckoutCart.click();
    await page.waitForTimeout(2000);
    
    // Step 8-9: Fill in personal information
    console.log('📍 Step 8-9: Filling in customer details...');
    
    // Select social title (Mr.)
    try {
      const socialTitle = frameLocator.locator('input[name="id_gender"][value="1"]');
      await socialTitle.check({ timeout: 5000 });
    } catch {
      console.log('   ⚠ Social title not required or not found');
    }
    
    // First name
    const firstName = frameLocator.locator('input[name="firstname"]');
    await firstName.waitFor({ state: 'visible' });
    await firstName.fill('John');
    
    // Last name
    const lastName = frameLocator.locator('input[name="lastname"]');
    await lastName.fill('Doe');
    
    // Email
    const email = frameLocator.locator('input[name="email"]');
    await email.fill('john.doe.playwright@automation.com');
    
    // Password (if required)
    try {
      const password = frameLocator.locator('input[name="password"]');
      await password.fill('TestPassword123!', { timeout: 3000 });
    } catch {
      console.log('   ℹ Password field not required (true guest checkout)');
    }
    
    // Privacy checkbox (if present)
    try {
      const privacyCheckbox = frameLocator.locator('input[name="psgdpr"]');
      await privacyCheckbox.check({ timeout: 3000 });
    } catch {
      console.log('   ℹ Privacy checkbox not found');
    }
    
    // Address
    const address1 = frameLocator.locator('input[name="address1"]');
    await address1.fill('123 Test Street');
    
    // Postal code
    const postcode = frameLocator.locator('input[name="postcode"]');
    await postcode.fill('10001');
    
    // City
    const city = frameLocator.locator('input[name="city"]');
    await city.fill('New York');
    
    console.log('   ✓ Customer details filled');
    
    // Step 10: Continue to shipping
    console.log('📍 Step 10: Continuing to shipping method...');
    const continueBtn = frameLocator.locator('button[name="continue"]');
    await continueBtn.click();
    await page.waitForTimeout(2000);
    
    // Step 11: Shipping method (auto-selected)
    console.log('📍 Step 11: Confirming shipping method...');
    
    // Step 12: Continue to payment
    console.log('📍 Step 12: Continuing to payment method...');
    const continueShippingBtn = frameLocator.locator('button[name="confirmDeliveryOption"]');
    await continueShippingBtn.waitFor({ state: 'visible' });
    await continueShippingBtn.click();
    await page.waitForTimeout(2000);
    
    // Step 13: Select payment method
    console.log('📍 Step 13: Selecting payment method...');
    const paymentOption = frameLocator.locator('#payment-option-1');
    await paymentOption.waitFor({ state: 'visible' });
    await paymentOption.check();
    await page.waitForTimeout(1000);
    
    // Step 14: Accept terms and conditions
    console.log('📍 Step 14: Accepting terms and conditions...');
    const termsCheckbox = frameLocator.locator('#conditions_to_approve\\[terms-and-conditions\\]');
    await termsCheckbox.waitFor({ state: 'visible' });
    await termsCheckbox.check();
    console.log('   ✓ Terms accepted');
    
    // Step 15: Place order
    console.log('📍 Step 15: Placing order...');
    const placeOrderBtn = frameLocator.locator('.ps-shown-by-js button[type="submit"]');
    await placeOrderBtn.waitFor({ state: 'visible' });
    await placeOrderBtn.click();
    await page.waitForTimeout(3000);
    
    // Step 16: Verify order confirmation
    console.log('📍 Step 16: Verifying order confirmation...');
    const confirmationHeading = frameLocator.locator('#content-hook_order_confirmation h3');
    await confirmationHeading.waitFor({ state: 'visible', timeout: 15000 });
    
    const confirmationText = await confirmationHeading.textContent();
    console.log(`   ✓ Confirmation message: ${confirmationText}`);
    
    // Check for order reference
    const orderDetails = frameLocator.locator('#order-details ul li').first();
    const orderDetailsText = await orderDetails.textContent();
    console.log(`   ✓ Order details: ${orderDetailsText}`);
    
    // Final assertions
    expect(confirmationText?.toLowerCase()).toMatch(/confirm|thank|success/);
    expect(orderDetailsText).toBeTruthy();
    
    console.log('\n' + '='.repeat(60));
    console.log('✅ Playwright: Order placed successfully!');
    console.log('='.repeat(60));
  });
  
});
