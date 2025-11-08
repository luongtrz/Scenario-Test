# 🚀 Hướng Dẫn Bắt Đầu Nhanh

## Yêu Cầu Hệ Thống

- **Linux/Mac:** Ubuntu 20.04+ hoặc macOS 11+
- **Python:** 3.8+ (để chạy Selenium tests)
- **Node.js:** 18+ (để chạy Playwright tests)
- **Chrome/Chromium:** Cài đặt trên hệ thống

## Cài Đặt Nhanh

### Bước 1: Clone Repository

```bash
git clone <repository-url>
cd test
```

### Bước 2: Chạy Tests

Cách đơn giản nhất - script sẽ tự động cài đặt dependencies:

```bash
chmod +x run-tests.sh
./run-tests.sh
```

Script sẽ tự động:
- ✅ Tạo Python virtual environment
- ✅ Cài đặt Python packages
- ✅ Cài đặt Node.js packages  
- ✅ Download Playwright browsers
- ✅ Chạy cả 2 test frameworks

## Các Lệnh Khác

```bash
# Chỉ chạy Selenium Python
./run-tests.sh selenium

# Chỉ chạy Playwright TypeScript
./run-tests.sh playwright
```

## Cài Đặt Thủ Công (Nếu Cần)

### Selenium Python

```bash
cd selenium_python

# Tạo virtual environment (bắt buộc trên Ubuntu 24.04+)
python3 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy test
python test_e2e_purchase.py
```

**Lưu ý:** Ubuntu 24.04+ requires virtual environment (PEP 668)

### Playwright TypeScript

```bash
cd playwright_typescript

# Cài đặt dependencies
npm install

# Download browser (chỉ cần 1 lần)
npx playwright install chromium
sudo npx playwright install-deps chromium  # Dependencies hệ thống

# Chạy test
npm test                 # Headless mode
npm run test:headed      # Visible browser
npm run test:debug       # Debug mode
```

## Kết Quả Mong Đợi

### Test Thành Công

```
✅ Selenium: Order placed successfully!
✅ Playwright: Order placed successfully!
```

### Test Thất Bại (Hiện Tại)

```
⚠️ Tests pass steps 1-5 but fail at step 6 (checkout modal)
```

Đây là issue đã biết với PrestaShop demo site - selector có thể đã thay đổi.

## Xem Kết Quả Test

### Selenium
- Screenshot lỗi: `selenium_python/selenium_failure.png`
- Console output real-time

### Playwright
- HTML Report: `playwright_typescript/playwright-report/index.html`
- Screenshots + videos trong `test-results/`

```bash
# Mở Playwright report
cd playwright_typescript
npx playwright show-report
```

## Troubleshooting

### Lỗi: "externally-managed-environment"
**Nguyên nhân:** Ubuntu 24.04+ yêu cầu virtual environment

**Giải pháp:**
```bash
cd selenium_python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Lỗi: "Chrome not found"
**Giải pháp:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install google-chrome-stable
```

### Lỗi: "SSL certificate"
**Giải pháp:** Đã được fix trong `playwright.config.ts` với `ignoreHTTPSErrors: true`

## Cấu Trúc Project

```
test/
├── .github/
│   └── copilot-instructions.md    # AI agent instructions
├── selenium_python/
│   ├── requirements.txt            # Python dependencies
│   └── test_e2e_purchase.py        # Selenium test
├── playwright_typescript/
│   ├── package.json                # Node dependencies
│   ├── playwright.config.ts        # Playwright config
│   └── test-e2e-purchase.spec.ts   # Playwright test
├── run-tests.sh                    # CLI test runner
├── README.md                       # Tài liệu đầy đủ
└── TEST_CASE_DOCUMENTATION.md      # Test case chi tiết
```

## Câu Hỏi Thường Gặp

**Q: Tại sao có 2 frameworks?**  
A: Để demo cross-framework testing patterns và so sánh approaches giữa Selenium vs Playwright.

**Q: Framework nào tốt hơn?**  
A: 
- **Selenium**: Mature, nhiều language support, community lớn
- **Playwright**: Modern, auto-wait tốt hơn, debugging tools mạnh hơn

**Q: Tests có chạy parallel không?**  
A: Không recommended - PrestaShop demo có thể throttle requests.

**Q: Làm sao debug khi test fail?**  
A:
- Selenium: Xem screenshot `selenium_failure.png`
- Playwright: `npm run test:debug` hoặc xem HTML report

## Tiếp Theo

- Đọc [README.md](README.md) để hiểu chi tiết project
- Xem [TEST_CASE_DOCUMENTATION.md](TEST_CASE_DOCUMENTATION.md) cho test design
- Check `.github/copilot-instructions.md` nếu làm việc với AI tools
