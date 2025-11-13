import { defineConfig, devices } from '@playwright/test';
import { config } from 'dotenv';

// Load environment variables from .env file
config();

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Bagisto demo may have rate limiting
  reporter: 'html',
  timeout: 150000,
  use: {
    baseURL: process.env.BAGISTO_BASE_URL || 'https://commerce.bagisto.com/',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15000,
    navigationTimeout: 30000,
    ignoreHTTPSErrors: true,
    
    // Clear cookies/cache before each test for clean state
    storageState: undefined, // Don't persist auth state
  },

  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Fix CSS/JS loading in WSL/Ubuntu Chromium
        launchOptions: {
          args: [
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
          ]
        }
      },
    },
  ],
});
