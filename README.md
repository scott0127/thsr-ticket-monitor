# 高鐵票券自動監控系統

⚠️ **重要免責聲明** ⚠️

## 🎓 學術目的與免責聲明

**本專案僅供學術研究和教育目的使用，請注意以下重要事項：**

### 📚 學術用途
- 本專案是一個**程式設計學習練習**，用於展示 Python 自動化技術
- 目的是學習 Selenium、網頁爬蟲、AI 驗證碼識別等技術
- 適用於程式設計教學和技術研究

### ⚠️ 使用限制與責任
1. **僅供學習參考**：本程式碼僅作為技術學習範例，不建議用於實際票務查詢
2. **遵守服務條款**：使用者應遵守台灣高鐵官網的使用條款和 robots.txt 規範
3. **合理使用**：避免對高鐵網站造成過度負載或影響正常服務
4. **自負責任**：使用本程式碼所產生的任何後果，由使用者自行承擔
5. **無商業用途**：本專案不得用於任何商業目的或營利行為

### 🚫 不承擔責任
- 作者不對程式的功能性、準確性或可靠性提供任何保證
- 不對因使用本程式碼而導致的任何損失或法律問題負責
- 不對任何第三方服務（包括但不限於高鐵網站、LINE API）的變更負責

### 🤝 建議做法
- 如需實際購票，請直接前往台灣高鐵官方網站
- 尊重網站服務條款，適當控制查詢頻率
- 將此專案視為技術學習工具，而非實用工具

---

## 🚀 專案簡介

這是一個使用 Python 開發的高鐵票券監控系統，整合了多項現代 Web 自動化技術：

### ✨ 技術特色

- 🤖 **AI 驗證碼識別**：使用 ddddocr 進行自動驗證碼識別
- 🕵️ **智能反偵測**：多重反自動化偵測機制
- 🎯 **精準錯誤處理**：針對三種情境的智能處理邏輯
- 📱 **LINE Bot 通知**：即時推播重要事件到手機
- 🔄 **持續監控**：智能冷卻機制避免封鎖
- 🛡️ **安全設計**：使用環境變數管理敏感資訊

### 🛠️ 技術棧

- **Python 3.11+**
- **Selenium WebDriver** - 瀏覽器自動化
- **ddddocr** - AI 驗證碼識別
- **BeautifulSoup4** - HTML 解析
- **LINE Bot API** - 訊息推播
- **python-dotenv** - 環境變數管理
- **webdriver-manager** - 自動 ChromeDriver 管理

## 📋 安裝需求

### 系統需求
- Python 3.11 或更高版本
- Chrome 瀏覽器
- 穩定的網路連線

### 套件安裝

使用 uv（推薦）：
```bash
uv add selenium beautifulsoup4 ddddocr webdriver-manager requests pillow python-dotenv
```

或使用 pip：
```bash
pip install selenium beautifulsoup4 ddddocr webdriver-manager requests pillow python-dotenv
```

## ⚙️ 設定說明

### 1. 基本設定

編輯 `main.py` 中的設定區：

```python
# 高鐵查詢設定
START_STATION = '2'         # 起始站代碼
END_STATION = '9'           # 終點站代碼
SEARCH_DATE = '2025/09/26'  # 查詢日期
SEARCH_TIME = '600P'        # 查詢時間

# 程式執行設定
CHECK_INTERVAL_SECONDS = 90  # 冷卻間隔（秒）
MAX_CAPTCHA_RETRIES = 99     # 驗證碼重試次數
CAPTCHA_RETRY_DELAY = 1      # 驗證碼重試間隔（秒）
```

### 2. LINE Bot 設定（可選）

1. 建立 `.env` 檔案：
```env
LINE_CHANNEL_ACCESS_TOKEN=你的Channel_Access_Token
LINE_USER_ID=你的User_ID
```

2. 參考 `LINE_Bot_API_設定說明.md` 完成 LINE Bot 申請

### 3. 站點代碼對照

| 站名 | 代碼 | 站名 | 代碼 |
|------|------|------|------|
| 南港 | 1    | 彰化 | 9    |
| 台北 | 2    | 雲林 | 10   |
| 板橋 | 3    | 嘉義 | 11   |
| 桃園 | 4    | 台南 | 12   |
| 新竹 | 5    | 左營 | 13   |
| 苗栗 | 6    |      |      |
| 台中 | 7    |      |      |
| 烏日 | 8    |      |      |

## 🚀 使用方法

### 基本使用
```bash
python main.py
```

### 測試 LINE Bot
```bash
python test_line_bot.py
```

### 功能測試版本
```bash
python test_anti_detection.py
```

## 📁 專案結構

```
tttt/
├── main.py                      # 主程式
├── test_line_bot.py            # LINE Bot 測試
├── test_anti_detection.py      # 功能測試版本
├── .env                        # 環境變數（不上傳）
├── pyproject.toml              # 專案配置
├── 使用指南.md                  # 詳細使用說明
├── LINE_Bot_API_設定說明.md     # LINE Bot 設定指南
└── 設定完成通知.md              # 設定完成確認
```

## 🔧 進階功能

### 智能監控邏輯
程式會根據不同情況採取對應策略：

1. **驗證碼錯誤** → 重新嘗試（最多 99 次）
2. **查無車次** → 等待 90 秒後重新查詢
3. **找到車票** → 立即通知並結束監控

### 反偵測機制
- 隨機化操作時間間隔
- 模擬真實滑鼠移動
- 隱藏自動化特徵
- 真實瀏覽器 User-Agent

### LINE 通知時機
- 🚀 程式啟動確認
- 🎉 找到可預訂車票
- ⏹️ 程式手動停止
- ❌ 發生錯誤異常

## 🐛 疑難排解

### 常見問題

**Q: 程式無法啟動？**
A: 檢查 Chrome 瀏覽器是否已安裝，確認 Python 版本 ≥ 3.11

**Q: 驗證碼識別失敗？**
A: ddddocr 準確率約 80-90%，程式會自動重試

**Q: LINE 通知無法發送？**
A: 檢查 `.env` 檔案設定，執行 `python test_line_bot.py` 測試

**Q: 被網站封鎖？**
A: 調整 `CHECK_INTERVAL_SECONDS` 增加冷卻時間

## 📖 文件說明

- `使用指南.md` - 完整使用說明和操作指南
- `LINE_Bot_API_設定說明.md` - LINE Bot 設定詳細步驟
- `設定完成通知.md` - 設定完成確認和測試結果

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request，但請注意：
- 遵守專案的學術研究目的
- 不要提交可能違反服務條款的功能
- 保持程式碼的教育性和可讀性

## 📜 授權條款

本專案採用 MIT 授權條款，但請特別注意：
- 僅限學術研究和教育用途
- 禁止商業使用
- 使用者需自行承擔使用風險

## 🙏 致謝

感謝以下開源專案：
- [Selenium](https://selenium.dev/) - Web 自動化框架
- [ddddocr](https://github.com/sml2h3/ddddocr) - 驗證碼識別
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML 解析
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) - WebDriver 管理

---

**⚠️ 再次提醒：本專案僅供學術研究使用，請勿用於實際票務查詢，並遵守相關網站的使用條款。**