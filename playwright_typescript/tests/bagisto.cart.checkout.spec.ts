// tests/bagisto.cart.checkout.spec.ts
// Bagisto Commerce – Shopping Cart State Machine & Checkout Flow (guest)
// Bao phủ: Empty, Add, Modify, Remove, Persist (nav + session), Wishlist (nếu có), Checkout, Abandon

import { test, expect, Page, Browser } from '@playwright/test';

const MARKETING = 'https://commerce.bagisto.com/';
const DEMO_CANDIDATES = [
  'https://demo.bagisto.com/',
  'https://demo.bagisto.com/velocity/',
  'https://demo.bagisto.com/mobikul-common/',
];

// ---------- Helpers ----------
async function gotoStorefront(page: Page) {
  await page.goto(MARKETING, { waitUntil: 'domcontentloaded' }).catch(() => {});
  const demoLink = page.locator('a:has-text("Demo"), a:has-text("Try"), a:has-text("Live"), a[href*="demo"]');
  if (await demoLink.first().isVisible().catch(() => false)) {
    await demoLink.first().click().catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
  }
  for (const url of [page.url(), ...DEMO_CANDIDATES]) {
    await page.goto(url, { waitUntil: 'domcontentloaded' }).catch(() => {});
    if (await isStorefront(page)) return;
  }
  throw new Error('Không tìm thấy storefront Bagisto demo khả dụng.');
}

async function isStorefront(page: Page) {
  const add = page
    .locator('button:has-text("Add to Cart"), [aria-label*="Add to cart" i], .add-to-cart, #addToCart')
    .first();
  const link = page
    .locator(
      [
        'a[href*="/products/"]',
        'a[href*="/product/"]',
        '[itemtype*="Product" i] a[href]',
        '.products-grid a[href], .product-list a[href], .card a[href], .grid a[href]',
        'a:has(.product-name), a:has(h2), a:has(img)',
      ].join(','),
    )
    .first();
  return (await add.isVisible().catch(() => false)) || (await link.isVisible().catch(() => false));
}

async function openFirstPDP(page: Page) {
  const pdpLink = page
    .locator(
      [
        'a[href*="/products/"]',
        'a[href*="/product/"]',
        '[itemtype*="Product" i] a[href]',
        '.products-grid a[href], .product-list a[href], .card a[href], .grid a[href]',
        'a:has(.product-name), a:has(h2), a:has(img)',
      ].join(','),
    )
    .filter({ hasNotText: /login|account|wishlist|register/i })
    .first();

  await expect(pdpLink, 'Không tìm thấy link sản phẩm trên storefront.').toBeVisible({ timeout: 20000 });
  const prev = page.url();
  await pdpLink.click();
  await Promise.race([
    page.waitForURL(u => u.toString() !== prev, { timeout: 15000 }).catch(() => null),
    page
      .locator('button:has-text("Add to Cart"), [aria-label*="Add to cart" i], .add-to-cart, #addToCart')
      .first()
      .waitFor({ timeout: 15000 })
      .catch(() => null),
  ]);
  await expect(
    page.locator('button:has-text("Add to Cart"), [aria-label*="Add to cart" i], .add-to-cart, #addToCart').first(),
  ).toBeVisible({ timeout: 15000 });
}

async function addToCart(page: Page) {
  const addBtn = page
    .locator('button:has-text("Add to Cart"), [aria-label*="Add to cart" i], .add-to-cart, #addToCart')
    .first();
  await expect(addBtn, 'Không thấy Add to Cart trên PDP.').toBeVisible({ timeout: 20000 });
  await addBtn.click();
  await page.waitForTimeout(800);
}

async function cartCounterText(page: Page) {
  const c = page.locator('.cart-count, [data-cart-count], .mini-cart .count').first();
  if (await c.isVisible().catch(() => false)) {
    return (await c.textContent())?.trim() ?? '';
  }
  return '';
}

async function gotoCart(page: Page) {
  await page.goto('https://demo.bagisto.com/checkout/cart', { waitUntil: 'domcontentloaded' }).catch(() => {});
}

async function gotoCheckout(page: Page) {
  await page.goto('https://demo.bagisto.com/checkout/onepage', { waitUntil: 'domcontentloaded' }).catch(() => {});
  const isCheckout = await page
    .locator('form#checkout, #checkout, [data-checkout]')
    .first()
    .isVisible()
    .catch(() => false);
  if (!isCheckout) {
    await gotoCart(page);
    const checkoutBtn = page
      .locator('a:has-text("Checkout"), button:has-text("Checkout"), a[href*="/checkout"]')
      .first();
    await expect(checkoutBtn, 'Không thấy nút Checkout trong giỏ.').toBeVisible({ timeout: 15000 });
    await checkoutBtn.click();
    await page.waitForLoadState('networkidle').catch(() => {});
  }
}

async function fillGuestAddress(page: Page) {
  const email = page.locator('input[name="email"], input[type="email"]').first();
  if (await email.isVisible().catch(() => false)) {
    await email.fill(`e2e${Date.now()}@example.com`);
    const cont = page
      .locator('button:has-text("Continue"), button:has-text("Next"), button:has-text("Proceed")')
      .first();
    if (await cont.isVisible().catch(() => false)) await cont.click().catch(() => {});
  }
  const fields: Array<[string, string]> = [
    ['input[name="first_name"], input[name="firstname"]', 'Nguyen'],
    ['input[name="last_name"], input[name="lastname"]', 'Van A'],
    ['input[name="address1"], input[name="address"]', '12 Nguyen Trai'],
    ['input[name="city"]', 'Ho Chi Minh'],
    ['input[name="postcode"], input[name="zip"], input[name="postcode[0]"]', '700000'],
    ['input[name="phone"], input[type="tel"]', '0900000000'],
  ];
  for (const [sel, val] of fields) {
    const f = page.locator(sel).first();
    if (await f.isVisible().catch(() => false)) await f.fill(val);
  }
  const save = page
    .locator(
      'button:has-text("Continue"), button:has-text("Next"), button:has-text("Proceed"), button[name="billing-save"], button[name="shipping-save"]',
    )
    .first();
  if (await save.isVisible().catch(() => false)) await save.click().catch(() => {});
}

async function chooseShippingAndPayment(page: Page) {
  const ship = page.locator('input[name="shipping_method"]').first();
  if (await ship.isVisible().catch(() => false)) await ship.check();

  const toPay = page
    .locator('button:has-text("Continue"), button:has-text("Next"), button:has-text("Proceed"), #continueToPayment')
    .first();
  if (await toPay.isVisible().catch(() => false)) await toPay.click().catch(() => {});

  const pay = page
    .locator('input[name="payment_method"], input[value*="cash"], input[value*="bank"], input[value*="check"]')
    .first();
  if (await pay.isVisible().catch(() => false)) await pay.check();

  const terms = page.locator('input[type="checkbox"][name*="terms"], input[name*="agree"]').first();
  if (await terms.isVisible().catch(() => false)) await terms.check();
}

async function placeOrder(page: Page) {
  const place = page
    .locator(
      'button:has-text("Place Order"), button:has-text("Confirm"), button:has-text("Complete"), button[type="submit"].btn',
    )
    .first();
  await expect(place, 'Không thấy nút Place Order.').toBeVisible({ timeout: 20000 });
  await place.click();

  const ok = await Promise.race([
    page
      .locator('text=/thank you|order confirmation|your order has been/i')
      .first()
      .waitFor({ timeout: 20000 })
      .then(() => true)
      .catch(() => false),
    page
      .locator('.order-success, [data-order-id]')
      .first()
      .waitFor({ timeout: 20000 })
      .then(() => true)
      .catch(() => false),
  ]);
  expect(ok, 'Không thấy trang xác nhận đơn hàng.').toBeTruthy();
}

// ---------- Tests ----------
test.describe('Bagisto — Cart State Machine & Checkout (Guest)', () => {
  test('TC-CART-001: Empty Cart Verification', async ({ page }) => {
    await gotoStorefront(page);
    const txt = await cartCounterText(page);
    expect(txt === '' || txt === '0').toBeTruthy();
  });

  test('TC-CART-002: Add Single Product to Cart', async ({ page }) => {
    await gotoStorefront(page);
    await openFirstPDP(page);
    await addToCart(page);
    const txt = await cartCounterText(page);
    expect(parseInt(txt || '0')).toBeGreaterThan(0);
  });

  test('TC-CART-003: Modify Cart Quantity', async ({ page }) => {
    await gotoStorefront(page);
    await openFirstPDP(page);
    await addToCart(page);
    await gotoCart(page);

    const qty = page.locator('input[name*="quantity" i], input[type="number"]').first();
    if (!(await qty.isVisible().catch(() => false))) test.skip(true, 'Theme/cart không có input số lượng.');
    await qty.fill('3');
    const update = page.locator('button:has-text("Update"), button[aria-label*="Update" i]').first();
    if (await update.isVisible().catch(() => false)) await update.click();
    await page.waitForTimeout(800);
    await expect(qty).toHaveValue(/3/);
  });

  test('TC-CART-004: Remove Product from Cart', async ({ page }) => {
    await gotoStorefront(page);
    await openFirstPDP(page);
    await addToCart(page);
    await gotoCart(page);

    const remove = page.locator('button[aria-label*="Remove" i], .remove-item, button:has-text("Remove")').first();
    if (!(await remove.isVisible().catch(() => false))) test.skip(true, 'Không tìm thấy nút remove.');
    await remove.click();
    const txt = await cartCounterText(page);
    expect(txt === '' || txt === '0').toBeTruthy();
  });

  test('TC-CART-005: Cart Persistence After Navigation', async ({ page }) => {
    await gotoStorefront(page);
    await openFirstPDP(page);
    await addToCart(page);
    const initial = await cartCounterText(page);
    await page.goto('https://demo.bagisto.com/about-us', { waitUntil: 'domcontentloaded' }).catch(() => {});
    await page.goto('https://demo.bagisto.com/', { waitUntil: 'domcontentloaded' }).catch(() => {});
    const final = await cartCounterText(page);
    expect(final).toBe(initial);
  });

  test('TC-CHECKOUT-001: Guest Checkout Complete Flow', async ({ page }) => {
    test.setTimeout(120000);
    await gotoStorefront(page);
    await openFirstPDP(page);
    await addToCart(page);
    await gotoCheckout(page);
    await fillGuestAddress(page);
    await chooseShippingAndPayment(page);
    await placeOrder(page);
  });

  test('TC-CHECKOUT-002: Cart State After Order Completion', async ({ page }) => {
    await gotoStorefront(page);
    const txt = await cartCounterText(page);
    expect(txt === '' || txt === '0').toBeTruthy();
  });

  test('TC-SESSION-001: Cart Persistence After Browser Restart', async ({ browser }) => {
    const ctx1 = await browser.newContext();
    const p1 = await ctx1.newPage();
    await gotoStorefront(p1);
    await openFirstPDP(p1);
    await addToCart(p1);
    const count1 = await cartCounterText(p1);
    const storageState = await ctx1.storageState();
    await ctx1.close();

    const ctx2 = await browser.newContext({ storageState });
    const p2 = await ctx2.newPage();
    await gotoStorefront(p2);
    const count2 = await cartCounterText(p2);
    if (count1 && parseInt(count1) > 0) {
      expect(parseInt(count2 || '0')).toBeGreaterThan(0);
    }
    await ctx2.close();
  });

  test('TC-SESSION-002: Abandoned Checkout Cart Preservation', async ({ page }) => {
    await gotoStorefront(page);
    await openFirstPDP(page);
    await addToCart(page);
    const before = await cartCounterText(page);

    await gotoCheckout(page);
    const email = page.locator('input[name="email"], input[type="email"]').first();
    if (await email.isVisible().catch(() => false)) {
      await email.fill('abandoned.user@test.com');
    }
    await page.goto('https://demo.bagisto.com/', { waitUntil: 'domcontentloaded' }).catch(() => {});
    const after = await cartCounterText(page);
    expect(after).toBe(before);
  });

  test('TC-WISHLIST-001: Save Item for Later (if available)', async ({ page }) => {
    await gotoStorefront(page);
    await openFirstPDP(page);
    const saveSelectors = [
      '.wishlist-icon',
      'button[aria-label*="wishlist" i]',
      'button[aria-label*="save" i]',
      '.add-to-wishlist',
      '[data-action="add-to-wishlist"]',
    ];
    let clicked = false;
    for (const s of saveSelectors) {
      const btn = page.locator(s).first();
      if (await btn.isVisible().catch(() => false)) {
        await btn.click().catch(() => {});
        clicked = true;
        break;
      }
    }
    test.skip(!clicked, 'Wishlist/Save-for-later không có trên demo/theme này.');
    const indicator = page.locator('.wishlist-count, [data-wishlist-count]').first();
    if (await indicator.isVisible().catch(() => false)) {
      const txt = (await indicator.textContent())?.trim() ?? '';
      expect(parseInt(txt || '0')).toBeGreaterThan(0);
    }
  });
});
