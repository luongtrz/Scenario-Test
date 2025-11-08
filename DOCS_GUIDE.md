# 📚 Hướng Dẫn Đọc Documentation

Project này có nhiều tài liệu - đây là guide giúp bạn biết nên đọc file nào trước!

## 🎯 Bạn Là Ai?

### 👨‍💻 Tôi muốn chạy tests nhanh nhất!

**→ Đọc:** [GETTING_STARTED.md](GETTING_STARTED.md)

Có tất cả commands cần thiết, troubleshooting, và quick start guide.

### 📖 Tôi muốn hiểu project này làm gì?

**→ Đọc theo thứ tự:**
1. [README.md](README.md) - Overview và test case summary
2. [GETTING_STARTED.md](GETTING_STARTED.md) - Cài đặt và chạy
3. [TEST_CASE_DOCUMENTATION.md](TEST_CASE_DOCUMENTATION.md) - Chi tiết test design

### 🏗️ Tôi muốn hiểu kiến trúc và design patterns?

**→ Đọc:** [ARCHITECTURE.md](ARCHITECTURE.md)

Deep dive vào:
- Iframe handling patterns
- Element interaction strategies  
- Selector priorities
- Wait strategies
- Cross-framework comparison

### 🤖 Tôi là AI coding agent muốn contribute code?

**→ Đọc:** [.github/copilot-instructions.md](.github/copilot-instructions.md)

Có tất cả:
- Critical workflows
- Project-specific conventions
- Known quirks và workarounds
- Cross-framework parity rules

### 👨‍🏫 Tôi muốn học Selenium và Playwright?

**→ Đọc theo thứ tự:**
1. [ARCHITECTURE.md](ARCHITECTURE.md) - Patterns và best practices
2. Source code với comments:
   - `selenium_python/test_e2e_purchase.py`
   - `playwright_typescript/test-e2e-purchase.spec.ts`
3. [TEST_CASE_DOCUMENTATION.md](TEST_CASE_DOCUMENTATION.md) - Test design theory

### 📝 Tôi muốn viết test case mới?

**→ Đọc:**
1. [TEST_CASE_DOCUMENTATION.md](TEST_CASE_DOCUMENTATION.md) - Template IEEE 29119
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Design patterns phải follow
3. [.github/copilot-instructions.md](.github/copilot-instructions.md) - Section "Adding New Test Cases"

## 📄 File Descriptions

| File | Purpose | For Who |
|------|---------|---------|
| **README.md** | Project overview, test summary | Everyone (start here) |
| **GETTING_STARTED.md** | Quick start, installation, troubleshooting | Beginners, first-time users |
| **ARCHITECTURE.md** | Design patterns, technical decisions | Developers, learners |
| **TEST_CASE_DOCUMENTATION.md** | Detailed test design (IEEE 29119) | QA, test designers |
| **.github/copilot-instructions.md** | AI coding agent guidelines | AI assistants, contributors |
| **run-tests.sh** | CLI test runner script | CI/CD, automation |

## 🔄 Typical Reading Flows

### Flow 1: Người Mới (30 phút)
1. README.md (5 phút) - Hiểu project làm gì
2. GETTING_STARTED.md (10 phút) - Cài đặt và chạy
3. Chạy `./run-tests.sh` (5 phút)
4. Xem test results (5 phút)
5. Đọc source code (5 phút)

### Flow 2: Developer Muốn Contribute (1-2 giờ)
1. README.md (5 phút)
2. GETTING_STARTED.md (10 phút)
3. ARCHITECTURE.md (30 phút) - **Quan trọng!**
4. .github/copilot-instructions.md (15 phút)
5. Source code với debugging (30 phút)

### Flow 3: QA Engineer (2-3 giờ)
1. README.md (5 phút)
2. TEST_CASE_DOCUMENTATION.md (45 phút) - **Core reading**
3. ARCHITECTURE.md (30 phút)
4. GETTING_STARTED.md + run tests (30 phút)
5. Analyze test results (30 phút)

### Flow 4: Học Framework So Sánh (3-4 giờ)
1. README.md (5 phút) - Overview
2. GETTING_STARTED.md (10 phút) - Setup
3. ARCHITECTURE.md (1 giờ) - **Key reading!**
4. Source code side-by-side:
   - Selenium test (30 phút)
   - Playwright test (30 phút)
5. Compare patterns (30 phút)
6. Run và experiment (1 giờ)

## 💡 Quick Tips

### Muốn Hiểu Nhanh?
```bash
# Read này trước:
cat README.md | head -50        # First 50 lines đủ hiểu overview
cat GETTING_STARTED.md | less   # Scan qua commands
```

### Muốn Chạy Ngay?
```bash
./run-tests.sh
# Xong! Script tự handle mọi thứ
```

### Muốn So Sánh Selenium vs Playwright?
```bash
# Mở 2 files cạnh nhau:
code selenium_python/test_e2e_purchase.py playwright_typescript/test-e2e-purchase.spec.ts

# Đọc ARCHITECTURE.md section "Wait Strategy Differences"
```

### Muốn Contribute?
```bash
# Read required docs:
cat .github/copilot-instructions.md
cat ARCHITECTURE.md | grep -A 5 "Cross-Framework"

# Check existing patterns:
grep -r "Step [0-9]" selenium_python/ playwright_typescript/
```

## 🎓 Learning Path Recommendations

### Beginner Path (Learn Testing)
```
README → GETTING_STARTED → Run Tests → Experiment
```

### Intermediate Path (Learn Frameworks)
```
README → ARCHITECTURE → Source Code → Modify Tests → Debug
```

### Advanced Path (Contribute/Design)
```
All Docs → Source Code → .github/copilot-instructions → Create New Tests
```

## ❓ Common Questions

**Q: Tại sao có nhiều docs?**  
A: Mỗi audience khác nhau cần info khác nhau. Beginner không cần ARCHITECTURE, developer không cần GETTING_STARTED chi tiết.

**Q: File nào quan trọng nhất?**  
A: Depends on goal:
- Chạy test → GETTING_STARTED.md
- Hiểu project → README.md
- Viết code → ARCHITECTURE.md
- Design tests → TEST_CASE_DOCUMENTATION.md

**Q: Có thể skip docs không?**  
A: Có thể! Nhưng:
- Skip docs → chạy test → ✅ works
- Đọc docs → hiểu why → 💡 better developer

**Q: Docs có outdated không?**  
A: Updated: 2025-11-08. Check git log để verify.

## 🔗 External Resources

**Selenium:**
- [Official Docs](https://selenium-python.readthedocs.io/)
- [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager)

**Playwright:**
- [Official Docs](https://playwright.dev/)
- [API Reference](https://playwright.dev/docs/api/class-playwright)

**PrestaShop:**
- [Demo Site](https://demo.prestashop.com/)
- [Official Docs](https://devdocs.prestashop.com/)

---

**💡 Pro Tip:** Nếu bạn chỉ có 10 phút:
1. Run `./run-tests.sh` (5 phút)
2. Đọc ARCHITECTURE.md section "Iframe Handling Patterns" (5 phút)

Bạn sẽ hiểu 80% của project!
