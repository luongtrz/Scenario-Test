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
    test.setTimeout(90000);
    
    console.log('Starting Playwright test...');
    
    console.log('Step 1: Navigating to PrestaShop demo...');
    await page.goto('https://demo.prestashop.com/', { waitUntil: 'domcontentloaded' });
    
    console.log('Step 2: Switching to storefront iframe...');
    const frameLocator = page.frameLocator('#framelive');
    
    console.log('Step 3: Locating product on homepage...');
    const firstProduct = frameLocator.locator('.product article .thumbnail').first();
    await firstProduct.waitFor({ state: 'visible', timeout: 15000 });
    
    console.log('Step 4: Opening product details...');
    await firstProduct.click();
    await page.waitForTimeout(1000);
    
    console.log('Step 5: Adding product to cart...');
    const addToCartBtn = frameLocator.locator('button[data-button-action="add-to-cart"]');
    await addToCartBtn.waitFor({ state: 'visible' });
    await addToCartBtn.click();
    
    console.log('Step 6: Proceeding to checkout from modal...');
    const proceedCheckoutModal = frameLocator.locator('.cart-content-btn .btn-primary');
    await proceedCheckoutModal.waitFor({ state: 'visible', timeout: 10000 });
    await proceedCheckoutModal.click();
    await page.waitForTimeout(2000);
    
    console.log('Step 7: Confirming cart and proceeding to checkout...');
    const proceedCheckoutCart = frameLocator.locator('.checkout a.btn-primary');
    await proceedCheckoutCart.waitFor({ state: 'visible' });
    await proceedCheckoutCart.click();
    await page.waitForTimeout(2000);
    
    console.log('Step 8-9: Filling in customer details...');
    
    try {
      const socialTitle = frameLocator.locator('input[name="id_gender"][value="1"]');
      await socialTitle.check({ timeout: 5000 });
    } catch {
      console.log('  Social title not required or not found');
    }
    
    const firstName = frameLocator.locator('input[name="firstname"]');
    await firstName.waitFor({ state: 'visible' });
    await firstName.fill('John');
    
    const lastName = frameLocator.locator('input[name="lastname"]');
    await lastName.fill('Doe');
    
    const email = frameLocator.locator('input[name="email"]');
    await email.fill('john.doe.playwright@automation.com');
    
    try {
      const password = frameLocator.locator('input[name="password"]');
      await password.fill('TestPassword123!', { timeout: 3000 });
    } catch {
      console.log('  Password field not required (true guest checkout)');
    }
    
    try {
      const privacyCheckbox = frameLocator.locator('input[name="psgdpr"]');
      await privacyCheckbox.check({ timeout: 3000 });
    } catch {
      console.log('  Privacy checkbox not found');
    }
    
    const address1 = frameLocator.locator('input[name="address1"]');
    await address1.fill('123 Test Street');
    
    const postcode = frameLocator.locator('input[name="postcode"]');
    await postcode.fill('10001');
    
    const city = frameLocator.locator('input[name="city"]');
    await city.fill('New York');
    
    console.log('Step 10: Continuing to shipping method...');
    const continueBtn = frameLocator.locator('button[name="continue"]');
    await continueBtn.click();
    await page.waitForTimeout(2000);
    
    console.log('Step 11: Confirming shipping method...');
    
    console.log('Step 12: Continuing to payment method...');
    const continueShippingBtn = frameLocator.locator('button[name="confirmDeliveryOption"]');
    await continueShippingBtn.waitFor({ state: 'visible' });
    await continueShippingBtn.click();
    await page.waitForTimeout(2000);
    
    console.log('Step 13: Selecting payment method...');
    const paymentOption = frameLocator.locator('#payment-option-1');
    await paymentOption.waitFor({ state: 'visible' });
    await paymentOption.check();
    await page.waitForTimeout(1000);
    
    console.log('Step 14: Accepting terms and conditions...');
    const termsCheckbox = frameLocator.locator('#conditions_to_approve\\[terms-and-conditions\\]');
    await termsCheckbox.waitFor({ state: 'visible' });
    await termsCheckbox.check();
    
    console.log('Step 15: Placing order...');
    const placeOrderBtn = frameLocator.locator('.ps-shown-by-js button[type="submit"]');
    await placeOrderBtn.waitFor({ state: 'visible' });
    await placeOrderBtn.click();
    await page.waitForTimeout(3000);
    
    console.log('Step 16: Verifying order confirmation...');
    const confirmationHeading = frameLocator.locator('#content-hook_order_confirmation h3');
    await confirmationHeading.waitFor({ state: 'visible', timeout: 15000 });
    
    const confirmationText = await confirmationHeading.textContent();
    console.log(`  Confirmation message: ${confirmationText}`);
    
    const orderDetails = frameLocator.locator('#order-details ul li').first();
    const orderDetailsText = await orderDetails.textContent();
    console.log(`  Order details: ${orderDetailsText}`);
    
    expect(confirmationText?.toLowerCase()).toMatch(/confirm|thank|success/);
    expect(orderDetailsText).toBeTruthy();
    
    console.log('\nPLAYWRIGHT: Order placed successfully!');
  });
  
});
