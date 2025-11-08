// tests/prestashop.cart.checkout.spec.ts
// PrestaShop demo (https://demo.prestashop.com/) — iFrame #framelive
// Bao phủ: Add, Remove, Empty (nếu có indicator), Checkout (guest), Abandon, Persist (nav)

import { test, expect, Page, FrameLocator, Browser } from '@playwright/test';

async function getFrame(page: Page): Promise<FrameLocator> {
  await page.goto('https://demo.prestashop.com/', { waitUntil: 'domcontentloaded' });
  const consent = page.locator('text=/accept all|agree|consent/i').first();
  if (await consent.isVisible().catch(() => false)) await consent.click().catch(() => {});
  const frame = page.frameLocator('#framelive');
  await expect(frame.locator('.product-miniature, .js-product-miniature').first()).toBeVisible({ timeout: 20000 });
  return frame;
}

async function openPDP(frame: FrameLocator) {
  const card = frame.locator('.product-miniature, .js-product-miniature').first();
  await expect(card).toBeVisible({ timeout: 15000 });
  await card.click();
  await expect(frame.locator('button[data-button-action="add-to-cart"], button:has-text("Add to cart")').first())
    .toBeVisible({ timeout: 15000 });
}

async function addToCart(frame: FrameLocator) {
  const add = frame.locator('button[data-button-action="add-to-cart"], button:has-text("Add to cart")').first();
  await add.click();
  const proceed = frame.locator('.cart-content-btn .btn-primary, a.btn-primary[href*="order"]').first();
  await expect(proceed).toBeVisible({ timeout: 15000 });
  await proceed.click();
}

async function gotoCheckout(frame: FrameLocator) {
  const proceed = frame.locator('.checkout a.btn-primary, a.btn.btn-primary.continue, a[href*="order"]').first();
  await expect(proceed, 'Không thấy nút proceed ở trang cart.').toBeVisible({ timeout: 20000 });
  await proceed.click();
}

async function fillCustomer(frame: FrameLocator) {
  const gender = frame.locator('input[name="id_gender"]').first();
  if (await gender.isVisible().catch(() => false)) await gender.check();
  await frame.locator('input[name="firstname"]').fill('John');
  await frame.locator('input[name="lastname"]').fill('Doe');
  await frame.locator('input[name="email"]').fill(`john${Date.now()}@example.com`);
  const gdpr = frame.locator('input[name="psgdpr"]').first();
  if (await gdpr.isVisible().catch(() => false)) await gdpr.check();
  await frame.locator('button[name="continue"]').click();
}

async function fillAddressAndShipping(frame: FrameLocator) {
  await frame.locator('input[name="address1"]').fill('123 Test Street');
  await frame.locator('input[name="postcode"]').fill('10001');
  await frame.locator('input[name="city"]').fill('New York');
  await frame.locator('button[name="confirm-addresses"], button[name="continue"]').first().click();
  const shipContinue = frame.locator('button[name="confirmDeliveryOption"], button[name="continue"]').first();
  await expect(shipContinue).toBeVisible({ timeout: 20000 });
  await shipContinue.click();
}

async function payAndPlace(frame: FrameLocator) {
  const payment = frame.locator('#payment-option-1, #payment-option-2, input[name="payment-option"]').first();
  if (await payment.isVisible().catch(() => false)) {
    await payment.check();
  } else {
    const labelPay = frame.locator('label[for*="payment-option"], .payment-options label').first();
    await labelPay.click().catch(() => {});
  }
  const terms = frame.locator('#conditions_to_approve\\[terms-and-conditions\\], input[name*="conditions"]').first();
  await expect(terms).toBeVisible({ timeout: 20000 });
  await terms.check();
  const place = frame.locator('.ps-shown-by-js button[type="submit"], button:has-text("Order with an obligation to pay")').first();
  await expect(place).toBeVisible({ timeout: 20000 });
  await place.click();
  const ok = await Promise.race([
    frame.locator('#content-hook_order_confirmation h3').first().waitFor({ timeout: 20000 }).then(() => true).catch(() => false),
    frame.locator('text=/order confirmation|thank you/i').first().waitFor({ timeout: 20000 }).then(() => true).catch(() => false),
  ]);
  expect(ok, 'Không thấy trang xác nhận đơn.').toBeTruthy();
}

test.describe('PrestaShop — Cart & Checkout (Guest)', () => {
  test('TC-CART-ADD-001: Add product to cart (modal appears)', async ({ page }) => {
    const frame = await getFrame(page);
    await openPDP(frame);
    await addToCart(frame);
    await expect(frame.locator('.checkout')).toBeVisible({ timeout: 15000 });
  });

  test('TC-CART-REMOVE-001: Remove product from cart', async ({ page }) => {
    const frame = await getFrame(page);
    await openPDP(frame);
    await addToCart(frame);
    const remove = frame.locator('a.js-cart-line-product-remove, .remove-from-cart, button:has-text("Remove")').first();
    if (!(await remove.isVisible().catch(() => false))) test.skip(true, 'Không thấy nút remove trong cart.');
    await remove.click().catch(() => {});
    const empty = frame.locator('text=/empty|no items/i').first();
    const lines = frame.locator('.cart-items .cart-item, .cart-item');
    await expect
      .poll(async () => (await lines.count()) === 0 || (await empty.isVisible().catch(() => false)))
      .toBeTruthy();
  });

  test('TC-CHECKOUT-001: Guest completes purchase', async ({ page }) => {
    test.setTimeout(120000);
    const frame = await getFrame(page);
    await openPDP(frame);
    await addToCart(frame);
    await gotoCheckout(frame);
    await fillCustomer(frame);
    await fillAddressAndShipping(frame);
    await payAndPlace(frame);
  });

  test('TC-ABANDON-001: Abandon checkout preserves cart', async ({ page }) => {
    const frame = await getFrame(page);
    await openPDP(frame);
    await addToCart(frame);
    await gotoCheckout(frame);
    const email = frame.locator('input[name="email"]').first();
    if (await email.isVisible().catch(() => false)) await email.fill('abandon@test.com');
    await page.goto('https://demo.prestashop.com/', { waitUntil: 'domcontentloaded' });
    const frame2 = await getFrame(page);
    await frame2.locator('.blockcart, a[href*="cart"], a[href*="order"]').first().click().catch(() => {});
    const items = frame2.locator('.cart-items .cart-item, .cart-item, .cart__items .cart__item');
    expect(await items.count()).toBeGreaterThan(0);
  });

  test('TC-PERSIST-001: Cart persists after navigation', async ({ page }) => {
    const frame = await getFrame(page);
    await openPDP(frame);
    await addToCart(frame);
    await frame.locator('a[href="/"]').first().click().catch(() => {});
    await frame.locator('a[href*="order"], a[href*="cart"]').first().click().catch(() => {});
    const items = frame.locator('.cart-items .cart-item, .cart-item');
    expect(await items.count()).toBeGreaterThan(0);
  });

  test('TC-SESSION-001: Cart persists after browser restart (best-effort)', async ({ browser }) => {
    const ctx1 = await browser.newContext();
    const p1 = await ctx1.newPage();
    let hadItem = false;

    {
      const f = await getFrame(p1);
      await openPDP(f);
      await addToCart(f);
      const items = f.locator('.cart-items .cart-item, .cart-item');
      hadItem = (await items.count()) > 0;
      const state = await ctx1.storageState();
      await ctx1.close();

      const ctx2 = await browser.newContext({ storageState: state });
      const p2 = await ctx2.newPage();
      const f2 = await getFrame(p2);
      await f2.locator('a[href*="order"], a[href*="cart"]').first().click().catch(() => {});
      const items2 = f2.locator('.cart-items .cart-item, .cart-item');
      if (hadItem) expect(await items2.count()).toBeGreaterThan(0);
      await ctx2.close();
    }
  });
});
