# GitHub 上傳指南

## 🚀 將專案上傳到 GitHub

### 方法一：使用 GitHub 網站建立倉庫

1. **前往 GitHub**
   - 打開 https://github.com
   - 登入您的帳號
   - 點擊右上角的 "+" 號，選擇 "New repository"

2. **建立新倉庫**
   - Repository name: `thsr-ticket-monitor`（或您喜歡的名稱）
   - Description: `高鐵票券自動監控系統 - 學術研究專案`
   - 選擇 **Public**（因為這是學術專案）
   - **不要**勾選 "Add a README file"（我們已經有了）
   - **不要**勾選 "Add .gitignore"（我們已經有了）
   - 點擊 "Create repository"

3. **上傳程式碼**
   複製 GitHub 提供的指令，應該類似這樣：

```bash
git remote add origin https://github.com/您的用戶名/thsr-ticket-monitor.git
git branch -M main
git push -u origin main
```

### 方法二：使用 GitHub CLI（如果已安裝）

```bash
gh repo create thsr-ticket-monitor --public --description "高鐵票券自動監控系統 - 學術研究專案"
git remote add origin https://github.com/您的用戶名/thsr-ticket-monitor.git
git branch -M main
git push -u origin main
```

## 📋 檢查清單

在上傳前，請確認：

- ✅ `.env` 檔案已被 `.gitignore` 忽略（包含您的 API tokens）
- ✅ `README.md` 包含完整的免責聲明
- ✅ 所有測試檔案都已包含
- ✅ `.env.example` 檔案可以幫助其他人了解設定方式

## 🔒 安全檢查

執行以下指令確認敏感資訊不會被上傳：

```bash
# 檢查 .env 是否被忽略
git check-ignore .env

# 檢查即將上傳的檔案
git ls-files

# 確認沒有包含 token 的檔案被追蹤
git ls-files | xargs grep -l "LINE_CHANNEL_ACCESS_TOKEN" || echo "安全：沒有發現包含 token 的檔案"
```

## 📝 倉庫描述建議

**Repository Description:**
```
高鐵票券自動監控系統 - 僅供學術研究和程式設計教學使用。整合 Selenium、AI 驗證碼識別、LINE Bot API 等技術。
```

**Topics 標籤建議:**
- `python`
- `selenium`
- `automation`
- `educational`
- `academic-research`
- `web-scraping`
- `taiwan-hsr`
- `captcha-recognition`
- `line-bot`

## 🌟 完成後的 GitHub 倉庫應該包含：

1. **完整的 README.md** - 包含免責聲明和使用說明
2. **主程式** - `main.py` 和相關測試檔案
3. **設定範例** - `.env.example` 
4. **文件** - 各種設定說明和使用指南
5. **安全配置** - `.gitignore` 確保敏感資訊不被上傳

---

**準備好上傳了！🚀**

請按照上述步驟建立 GitHub 倉庫並上傳您的專案。