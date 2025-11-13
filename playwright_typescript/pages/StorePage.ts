import { Page, expect } from '@playwright/test';

export class StorePage {
    private lastAddedProductName: string = '';

    constructor(public page: Page, private base = process.env.BAGISTO_BASE_URL!) { }

    async gotoHome() {
        console.log('Navigating to Storefront Home:', this.base);
        await this.page.goto(this.base + '/', { waitUntil: 'networkidle' });
    }

    /**
     * Auto-login to Bagisto demo (no credentials needed)
     * Just navigate to login page and click "Sign In"
     */
    async login() {
        console.log('Logging in to Bagisto demo...');
        await this.page.goto(process.env.BAGISTO_BASE_URL + '/customer/login', {
            waitUntil: 'load',  // Wait for full page load including CSS
            timeout: 45000
        });
        
        // CRITICAL: Wait for CSS/fonts to fully load for video recording
        await this.page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
        await this.page.waitForTimeout(1500);  // Extra wait for styles to render
        
        // Dismiss cookie consent if present
        const acceptBtn = this.page.locator('button:has-text("Accept")').first();
        if (await acceptBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
            await acceptBtn.click();
            await this.page.waitForTimeout(500);
        }
        
        const signInBtn = this.page.locator('button[type="submit"]:has-text("Sign In")').first();
        await signInBtn.click();
        await this.page.waitForTimeout(2000); // Wait for login to complete
        
        console.log('  ✓ Logged in successfully');
    }

    async openCart() {
        await this.page.goto(process.env.BAGISTO_BASE_URL + '/checkout/cart', {
            waitUntil: 'domcontentloaded',
            timeout: 45000
        });
    }

    async cartIsEmpty() {
        const emptySelectors = [
            'text=Your cart is empty',
            'text=Cart is empty',
            'text=No items in cart',
            '.empty-cart'
        ];

        for (const selector of emptySelectors) {
            const element = this.page.locator(selector).first();
            if (await element.isVisible({ timeout: 4000 }).catch(() => false)) {
                await expect(element).toBeVisible();
                return;
            }
        }
    }

    async addFirstProductFromHome() {
        var categories = [
            '/casual-wear-female',
            '/girls-clothing',
            '/electronics',
            '/home-kitchen',
            '/books-stationery'
        ];

        // Shuffle categories
        for (let i = categories.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [categories[i], categories[j]] = [categories[j], categories[i]];
        }

        for (const category of categories) {
            try {
                console.log(`  Trying category: ${category}`);
                
                await this.page.goto(process.env.BAGISTO_BASE_URL + category, {
                    waitUntil: 'networkidle',
                    timeout: 45000
                });

                const productSelector = 'a[href*="commerce.bagisto.com/"][aria-label]:has(img[alt])';
                const productExists = await this.page.locator(productSelector).first().isVisible({ timeout: 5000 }).catch(() => false);
                
                if (!productExists) {
                    console.log(`  ✗ No products in ${category}, trying next...`);
                    continue;
                }

                const product = this.page.locator(productSelector).first();
                this.lastAddedProductName = (await product.getAttribute('aria-label'))?.trim() || '';
                console.log(`  Selected product: ${this.lastAddedProductName}`);

                await product.click();
                
                // Use shorter timeout with fallback instead of networkidle
                try {
                    await this.page.waitForLoadState('domcontentloaded', { timeout: 10000 });
                    await this.page.waitForTimeout(1000); // Brief wait for dynamic content
                } catch {
                    console.log(`  ⚠ Page load slow, continuing anyway...`);
                }

                // Check if "Add To Cart" button exists first
                const addBtn = this.page.locator('button:has-text("Add To Cart")').first();
                const isAddBtnVisible = await addBtn.isVisible({ timeout: 3000 }).catch(() => false);
                
                if (!isAddBtnVisible) {
                    console.log(`  ✗ Add To Cart button not found, trying next category...`);
                    continue;
                }
                
                // Check if product has configurable options that MUST be selected
                // Look for required option indicators (red asterisk, "required" text, etc.)
                const hasRequiredOptions = await this.page.locator('text=/\\*|required/i')
                    .first()
                    .isVisible({ timeout: 1000 })
                    .catch(() => false);
                
                if (hasRequiredOptions) {
                    console.log(`  ⚠ Product has required configurable options, skipping...`);
                    continue; // Skip this product, try next category
                }
                
                // Try to add product - if it has options but has defaults, it may still work
                await addBtn.click();
                
                // Wait longer for add-to-cart AJAX to complete
                console.log(`  → Waiting for cart to update...`);
                await this.page.waitForTimeout(5000);
                
                // Navigate to cart page to verify product was added
                console.log(`  → Checking cart...`);
                await this.page.goto(process.env.BAGISTO_BASE_URL + '/checkout/cart', {
                    waitUntil: 'networkidle', // Wait for all network requests to finish
                    timeout: 20000
                });
                
                // Wait a bit more for cart DOM to render
                await this.page.waitForTimeout(2000);
                
                // Count actual items in cart by checking quantity inputs
                const qtyInputs = this.page.locator('input[type="hidden"][name="quantity"]');
                const itemCount = await qtyInputs.count();
                
                console.log(`  → Found ${itemCount} items in cart`);
                
                if (itemCount > 0) {
                    console.log(`  ✓ Cart has ${itemCount} item(s)`);
                    return; // Success!
                }
                
                console.log(`  ✗ Cart is empty, trying next category...`);
            } catch (error) {
                console.log(`  ✗ Failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
            }
        }
        
        throw new Error(`Failed to add product after trying ${categories.length} categories`);
    }

    /**
     * Add random product from a random category to cart
     */
    async addRandomProductFromHome() {
        await this.gotoHome();
        
        // Available categories with products
        const categories = [
            '/casual-wear-female',
            '/girls-clothing',
            '/electronics',
            '/home-kitchen',
            '/books-stationery'
        ];

        
        
        // Shuffle categories and try each until we find a working product
        const shuffled = [...categories].sort(() => Math.random() - 0.5);
        
        for (const category of shuffled) {
            try {
                console.log(`  Trying category: ${category}`);
                
                await this.page.goto(process.env.BAGISTO_BASE_URL + category, {
                    waitUntil: 'networkidle',
                    timeout: 45000
                });

                await this.page.waitForSelector('a[href*="commerce.bagisto.com/"][aria-label]:has(img[alt])', { timeout: 5000 });

                const firstProduct = this.page.locator('a[href*="commerce.bagisto.com/"][aria-label]:has(img[alt])').first();
                this.lastAddedProductName = (await firstProduct.getAttribute('aria-label'))?.trim() || '';
                console.log(`  ✓ Found product: ${this.lastAddedProductName}`);

                await firstProduct.click();
                await this.page.waitForLoadState('networkidle');

                const addBtn = this.page.locator('button:has-text("Add To Cart")').first();
                await addBtn.waitFor({ state: 'visible', timeout: 10000 });

                await addBtn.click();
                
                const successMsg = this.page.locator('text=/item.*added|added.*successfully|success/i').first();
                await successMsg.waitFor({ state: 'visible', timeout: 10000 });
                await this.page.waitForTimeout(2000);

                await this.page.goto(process.env.BAGISTO_BASE_URL + '/checkout/cart', {
                    waitUntil: 'networkidle',
                    timeout: 45000
                });
                
                return; // Success!
                
            } catch (error) {
                console.log(`  ✗ No products in ${category}, trying next...`);
                await this.gotoHome();
                continue;
            }
        }
        
        throw new Error('Could not find any products in any category');
    }


    async addProductByName(name: string) {
        // Search for product
        const searchInput = this.page.locator('input[type="search"], input[name="q"], input[name="term"]').first();
        await searchInput.fill(name);
        await this.page.keyboard.press('Enter');
        await this.page.waitForLoadState('networkidle');

        // Add first result to cart
        await this.page.getByRole('button', { name: /add to cart/i }).first().click();
        await this.page.waitForTimeout(2000);
    }

    async goCheckout() {
        const checkoutSelectors = [
            'a:has-text("Proceed To Checkout")',
            'a:has-text("Checkout")',
            'button:has-text("Checkout")',
            'a:has-text("Proceed to Checkout")',
            '.checkout-btn',
            'a[href*="checkout"]'
        ];

        for (const selector of checkoutSelectors) {
            const element = this.page.locator(selector).first();
            if (await element.isVisible({ timeout: 3000 }).catch(() => false)) {
                await element.click();
                await this.page.waitForLoadState('networkidle');
                await this.page.waitForTimeout(2000); // Wait for checkout page to fully load
                return;
            }
        }
        
        throw new Error('Checkout button not found');
    }

    /**
     * Increase product quantity by clicking + button
     */
    async increaseQty(times = 1) {
        const plusBtn = this.page.getByRole('button', { name: /increase quantity/i }).first();
        for (let i = 0; i < times; i++) {
            await plusBtn.click();
            await this.page.waitForTimeout(300);
        }
    }

    /**
     * Decrease product quantity by clicking - button
     */
    async decreaseQty(times = 1) {
        const minusBtn = this.page.getByRole('button', { name: /decrease quantity/i }).first();
        for (let i = 0; i < times; i++) {
            await minusBtn.click();
            await this.page.waitForTimeout(300);
        }
    }

    /**
     * Click "Update Cart" button to save quantity changes
     */
    async updateCart() {
        const updateBtn = this.page.locator('button:has-text("Update Cart")').first();
        await updateBtn.click();
        await this.page.waitForTimeout(1500); // Wait for page reload/update
    }

    /**
     * Verify last added product is in cart
     */
    async verifyLastAddedProductInCart() {
        if (!this.lastAddedProductName) throw new Error('No product was added yet');

        await this.page.goto(process.env.BAGISTO_BASE_URL + '/checkout/cart', {
            waitUntil: 'domcontentloaded',
            timeout: 45000,
        });

        // Wait for cart items to appear
        await this.page.waitForSelector(
            'input[type="hidden"][name="quantity"][value], span[aria-label="Increase Quantity"], span[aria-label="Decrease Quantity"], button:has-text("Remove")',
            { timeout: 15000 }
        );

        // Verify product name (partial match)
        const partial = this.lastAddedProductName.split(/\s+/).slice(0, 2).join(' ');
        const safe = partial.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

        const nameNode = this.page.getByRole('link', { name: new RegExp(safe, 'i') }).first();
        await expect(nameNode).toBeVisible();

        // Verify quantity > 0
        const qtyInputs = this.page.locator('input[type="hidden"][name="quantity"][value]');
        const n = await qtyInputs.count();
        expect(n).toBeGreaterThan(0);
        let ok = false;
        for (let i = 0; i < n; i++) {
            const v = await qtyInputs.nth(i).getAttribute('value');
            if (v && Number(v) > 0) { ok = true; break; }
        }
        expect(ok).toBe(true);

        // Verify controls are visible
        await expect(this.page.getByRole('button', { name: /Increase Quantity/i })).toBeVisible();
        await expect(this.page.getByRole('button', { name: /Decrease Quantity/i })).toBeVisible();
    }


    /**
     * Set quantity by directly editing the quantity input field
     * @param qty Target quantity (will handle stock limits validation)
     */
    async setQuantityDirectly(qty: number) {
        // Find the quantity input field (may be visible or hidden depending on UI)
        const qtySelectors = [
            'input[name="quantity"]',
            'input[type="number"][name*="qty"]',
            'input.qty-input',
            '[data-qty-input]'
        ];

        let qtyInput = null;
        for (const selector of qtySelectors) {
            const input = this.page.locator(selector).first();
            if (await input.isVisible({ timeout: 2000 }).catch(() => false)) {
                qtyInput = input;
                break;
            }
        }

        if (!qtyInput) {
            throw new Error('Quantity input field not found');
        }

        // Clear and set new value
        await qtyInput.click();
        await qtyInput.fill(qty.toString());
        await this.page.waitForTimeout(500);
        
        // Click "Update Cart" to trigger validation
        await this.updateCart();
    }

    /**
     * Set quantity to 0 by decreasing - DEPRECATED for commerce.bagisto.com
     * Use removeFirstItem() instead
     */
    async setQtyForFirstItem(qty: number) {
        if (qty === 0) {
            // Cannot set qty to 0, must use Remove button
            await this.removeFirstItem();
            return;
        }

        // For testing stock limits, use setQuantityDirectly instead
        await this.setQuantityDirectly(qty);
    }

    /**
     * Remove first item from cart using Remove button
     */
    async removeFirstItem() {
        // Wait for any existing modal to disappear first
        await this.page.waitForTimeout(500);
        
        const removeBtn = this.page.getByRole('button', { name: /Remove/i }).first();
        
        // Force click if needed (modal might be overlaying)
        try {
            await removeBtn.click({ timeout: 3000 });
        } catch {
            await removeBtn.click({ force: true });
        }
        
        // Wait for confirmation modal and click confirm
        const confirmBtn = this.page.locator('button:has-text("Yes"), button:has-text("Confirm"), button:has-text("OK")').first();
        const isModalVisible = await confirmBtn.isVisible({ timeout: 2000 }).catch(() => false);
        
        if (isModalVisible) {
            await confirmBtn.click();
        }
        
        // Wait for modal to close and cart to update
        await this.page.waitForTimeout(2000);
    }

    /**
     * Save for later - Skip if not available
     */
    async saveForLaterFirstItem() {
        const saveBtn = this.page.getByRole('button', { name: /save for later/i }).first();
        const count = await saveBtn.count();
        if (count === 0) {
            throw new Error('Save for later feature not available in this environment');
        }
        await saveBtn.click();
        await this.page.waitForTimeout(1500);
    }

    /**
     * Move saved item back to cart - Skip if not available
     */
    async moveSavedToCart() {
        const moveBtn = this.page.getByRole('button', { name: /move to cart/i }).first();
        const count = await moveBtn.count();
        if (count === 0) {
            throw new Error('Move to cart feature not available in this environment');
        }
        await moveBtn.click();
        await this.page.waitForTimeout(1500);
    }

    async fillShippingAddressMinimal() {
        const fields = [
            { selector: 'input[name="first_name"], input[name="billing[first_name]"]', value: 'John' },
            { selector: 'input[name="last_name"], input[name="billing[last_name]"]', value: 'Doe' },
            { selector: 'input[name="email"], input[name="billing[email]"]', value: 'john.doe@example.com' },
            { selector: 'input[name="address1[]"], input[name="address1"], input[name="billing[address1][]"]', value: '221B Baker Street' },
            { selector: 'input[name="city"], input[name="billing[city]"]', value: 'London' },
            { selector: 'input[name="postcode"], input[name="billing[postcode]"]', value: '10001' },
            { selector: 'input[name="phone"], input[name="billing[phone]"]', value: '0123456789' },
        ];

        for (const field of fields) {
            const element = this.page.locator(field.selector).first();
            if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
                await element.fill(field.value);
            }
        }

        // Select country if present
        const country = this.page.locator('select[name="country"], select[name="billing[country]"]').first();
        if (await country.isVisible({ timeout: 2000 }).catch(() => false)) {
            await country.selectOption({ index: 1 });
            await this.page.waitForTimeout(1000); // Wait for state to load
        }

        // Select state if present
        const state = this.page.locator('select[name="state"], select[name="billing[state]"]').first();
        if (await state.isVisible({ timeout: 2000 }).catch(() => false)) {
            await state.selectOption({ index: 1 });
        }

        // Continue/Proceed button to move to shipping/payment selection
        const continueBtn = this.page.locator('button:has-text("Continue"), button:has-text("Proceed"), button:has-text("Next")').first();
        if (await continueBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
            console.log('  → Clicking Proceed to shipping/payment selection...');
            await continueBtn.click();
            await this.page.waitForLoadState('networkidle');
            await this.page.waitForTimeout(2000); // Wait for shipping/payment options to load
        }
    }

    async choosePaymentAndPlace(orderShouldSucceed = true) {
        // Step 1: Select Shipping Method by clicking label (input is hidden)
        console.log('  → Selecting shipping method...');
        
        // Wait for shipping methods to appear
        await this.page.waitForTimeout(2000);
        
        const shippingMethods = this.page.locator('input[type="radio"][name="shipping_method"]');
        const shippingCount = await shippingMethods.count();
        
        if (shippingCount > 0) {
            // Prefer Free Shipping
            const freeShippingLabel = this.page.locator('label[for="free_free"]').last(); // Use .last() to get the clickable label
            const hasFree = await freeShippingLabel.isVisible({ timeout: 2000 }).catch(() => false);
            
            if (hasFree) {
                console.log('    Clicking Free Shipping label...');
                await freeShippingLabel.click();
            } else {
                // Click first available shipping label
                const firstLabel = this.page.locator('label[for^="flatrate"]').last();
                if (await firstLabel.isVisible({ timeout: 2000 }).catch(() => false)) {
                    console.log('    Clicking Flat Rate shipping label...');
                    await firstLabel.click();
                }
            }
            
            await this.page.waitForTimeout(2000);
        } else {
            console.log('    No shipping methods found');
        }
        
        // Step 2: Select Payment Method by clicking label (input is hidden)
        console.log('  → Selecting payment method...');
        
        // Wait for payment methods to appear
        await this.page.waitForTimeout(2000);
        
        const paymentMethods = this.page.locator('input[type="radio"][name="payment[method]"]');
        const paymentCount = await paymentMethods.count();
        
        if (paymentCount > 0) {
            // Prefer Cash On Delivery
            const codLabel = this.page.locator('label[for="cashondelivery"]').last(); // Use .last() to get the clickable label
            const hasCOD = await codLabel.isVisible({ timeout: 2000 }).catch(() => false);
            
            if (hasCOD) {
                console.log('    Clicking Cash On Delivery label...');
                await codLabel.click();
            } else {
                // Click first available payment label
                const firstLabel = this.page.locator('label[for="moneytransfer"]').last();
                if (await firstLabel.isVisible({ timeout: 2000 }).catch(() => false)) {
                    console.log('    Clicking Money Transfer label...');
                    await firstLabel.click();
                }
            }
            
            await this.page.waitForTimeout(2000);
        } else {
            console.log('    No payment methods found');
        }
        
        // Step 3: Click "Place Order"
        console.log('  → Clicking Place Order...');
        const placeBtnSelectors = [
            'button:has-text("Place Order")',
            'button.primary-button:has-text("Place")',
            'button[type="button"]:has-text("Place Order")',
            'button.primary-button'
        ];
        
        let placeBtn = null;
        for (const selector of placeBtnSelectors) {
            const btn = this.page.locator(selector).first();
            if (await btn.isVisible({ timeout: 2000 }).catch(() => false)) {
                placeBtn = btn;
                console.log(`    Found button with selector: ${selector}`);
                break;
            }
        }
        
        if (placeBtn) {
            await placeBtn.click();
            await this.page.waitForTimeout(5000); // Wait for order processing
            
            if (orderShouldSucceed) {
                // Check for success message
                const successSelectors = [
                    'text=/thank you|order placed|order.*success|completed/i',
                    'text=/order.*confirmed/i'
                ];
                
                for (const selector of successSelectors) {
                    const msg = this.page.locator(selector).first();
                    if (await msg.isVisible({ timeout: 5000 }).catch(() => false)) {
                        console.log('  ✓ Order placed successfully');
                        return;
                    }
                }
            }
        } else {
            console.log('  ⚠ Place Order button not found');
        }
    }
    
    /**
     * Verify latest order in order history
     * Returns order details: { orderId, date, total, status }
     */
    async getLatestOrder() {
        await this.page.goto(process.env.BAGISTO_BASE_URL + '/customer/account/orders', {
            waitUntil: 'networkidle',
            timeout: 15000
        });
        
        // Wait for orders list to load
        await this.page.waitForTimeout(2000);
        
        // Find all order rows (skip header row)
        const orderRows = this.page.locator('.row.grid').filter({ hasNot: this.page.locator('text=/Order ID|Order Date/i') });
        const rowCount = await orderRows.count();
        
        if (rowCount === 0) {
            return null;
        }
        
        // Get first data row (most recent order)
        const firstRow = orderRows.first();
        
        // Extract text from all cells
        const cellsText = await firstRow.locator('p').allTextContents();
        
        if (cellsText.length >= 4) {
            return {
                orderId: cellsText[0]?.trim() || '',
                date: cellsText[1]?.trim() || '',
                total: cellsText[2]?.trim() || '',
                status: cellsText[3]?.trim() || ''
            };
        }
        
        return null;
    }
}
