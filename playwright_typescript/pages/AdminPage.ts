import { Page, expect } from '@playwright/test';

export class AdminPage {
  constructor(
    public page: Page, 
    private adminUrl = process.env.BAGISTO_ADMIN_URL!
  ) {}

  /**
   * Auto-login to Bagisto admin demo (no credentials needed)
   * Just navigate to admin login page and click "Sign In"
   */
  async login() {
    console.log('Logging in to Bagisto admin demo...');
    // BAGISTO_ADMIN_URL already includes /admin/login
    await this.page.goto(this.adminUrl, { 
      waitUntil: 'networkidle',
      timeout: 45000 
    });
    
    // Click sign in button (auto-login for demo)
    // Try multiple selectors for the button
    const signInSelectors = [
      'button[type="submit"]:has-text("Sign In")',
      'button:has-text("Sign In")',
      'button[type="submit"]',
      'input[type="submit"]'
    ];
    
    let signInBtn = null;
    for (const selector of signInSelectors) {
      const btn = this.page.locator(selector).first();
      if (await btn.isVisible({ timeout: 3000 }).catch(() => false)) {
        signInBtn = btn;
        console.log(`  ✓ Found sign in button: ${selector}`);
        break;
      }
    }
    
    if (signInBtn) {
      await signInBtn.click();
      await this.page.waitForTimeout(3000); // Wait for dashboard to load
      console.log('  ✓ Admin logged in successfully');
    } else {
      throw new Error('Admin sign in button not found');
    }
  }
  
  /**
   * Login with credentials (for non-demo environments)
   */
  async loginWithCredentials(email: string, password: string) {
    await this.page.goto(this.adminUrl, { waitUntil: 'networkidle' });
    
    // Fill email
    const emailInput = this.page.locator('input[type="email"], input[name="email"]').first();
    await emailInput.fill(email);
    
    // Fill password
    const passwordInput = this.page.locator('input[type="password"], input[name="password"]').first();
    await passwordInput.fill(password);
    
    // Click sign in
    const signInBtn = this.page.locator('button:has-text("Sign In"), button[type="submit"]').first();
    await signInBtn.click();
    
    // Wait for dashboard
    await expect(this.page.locator('text=/dashboard/i')).toBeVisible({ timeout: 10000 });
  }

  /**
   * Navigate directly to product edit page by ID
   * More reliable than searching by name
   */
  async openProductById(productId: number) {
    console.log(`  Opening product ${productId} in admin...`);
    // adminUrl is "https://commerce.bagisto.com/admin/login", need to remove "/login"
    const adminBase = this.adminUrl.replace('/login', '');
    await this.page.goto(`${adminBase}/catalog/products/edit/${productId}`, {
      waitUntil: 'networkidle',
      timeout: 45000
    });
    await this.page.waitForTimeout(2000);
  }
  
  async openProductByName(name: string) {
    // Navigate to Catalog > Products
    const catalogLink = this.page.locator('a:has-text("Catalog"), a[href*="catalog"]').first();
    if (await catalogLink.isVisible({ timeout: 3000 }).catch(() => false)) {
      await catalogLink.click();
    }
    
    const productsLink = this.page.locator('a:has-text("Products"), a[href*="product"]').first();
    await productsLink.click();
    await this.page.waitForLoadState('networkidle');
    
    // Search for product
    const searchInput = this.page.locator('input[type="search"], input[name="search"]').first();
    if (await searchInput.isVisible({ timeout: 3000 }).catch(() => false)) {
      await searchInput.fill(name);
      await this.page.keyboard.press('Enter');
      await this.page.waitForLoadState('networkidle');
    }
    
    // Open product edit page
    const productLink = this.page.getByRole('link', { name, exact: false }).first();
    await productLink.click();
    await this.page.waitForLoadState('networkidle');
  }

  async setStockQty(qty: number) {
    const qtySelectors = [
      'input[name*="inventories"][type="number"]',
      'input[name="inventory"]',
      'input[name*="qty"]'
    ];
    
    for (const selector of qtySelectors) {
      const input = this.page.locator(selector).first();
      if (await input.isVisible({ timeout: 2000 }).catch(() => false)) {
        await input.fill(String(qty));
        return;
      }
    }
  }

  async setPrice(price: number) {
    const priceSelectors = [
      'input[name="price"]',
      'input[name*="[price]"]'
    ];
    
    for (const selector of priceSelectors) {
      const input = this.page.locator(selector).first();
      if (await input.isVisible({ timeout: 2000 }).catch(() => false)) {
        await input.fill(String(price));
        return;
      }
    }
  }

  async saveProduct() {
    const saveBtn = this.page.locator('button:has-text("Save"), button:has-text("Update")').first();
    await saveBtn.click();
    
    // Wait for success message
    await expect(this.page.locator('text=/success|updated/i')).toBeVisible({ timeout: 8000 });
  }
}
