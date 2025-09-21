# LINE Bot API 設定說明

## 🤖 LINE Bot API 與 LINE Notify 的差異

### LINE Bot API（目前使用）
- ✅ 可以自訂 Bot 名稱和頭像
- ✅ 訊息來自您的專屬 Bot
- ✅ 支援豐富的訊息格式（文字、圖片、按鈕等）
- ❌ 設定較複雜
- ❌ 需要驗證和可能的費用

### LINE Notify（之前版本）
- ✅ 設定簡單
- ✅ 完全免費
- ❌ 訊息只能來自「LINE Notify」官方帳號
- ❌ 只支援純文字訊息

## 📋 LINE Bot API 設定步驟

### 1. 建立 LINE Developers 帳號

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 使用您的 LINE 帳號登入
3. 建立新的 Provider（例如：「高鐵監控」）

### 2. 建立 Messaging API Channel

1. 在 Provider 中點選「Create a channel」
2. 選擇「Messaging API」
3. 填寫必要資訊：
   - **Channel name**: 高鐵票券監控機器人
   - **Channel description**: 監控高鐵票券並發送通知
   - **Category**: Technology
   - **Subcategory**: AI/Bot/Assistant
4. 同意服務條款並建立

### 3. 取得 Channel Access Token

1. 進入剛建立的 Channel
2. 前往「Messaging API」頁籤
3. 在「Channel access token」區域點選「Issue」
4. 複製產生的 Token（約 170 字元長度）

### 4. 取得您的 User ID

#### 方法一：透過官方工具
1. 加 LINE Official Account Manager 為好友
2. 查看 Basic settings → User ID

#### 方法二：透過 Bot 取得（推薦）
1. 首先在程式中填入 Channel Access Token（User ID 暫時留空）
2. 執行以下測試程式：

```python
import requests

def get_user_profile():
    # 暫時修改 send_line_message 函式來印出 User ID
    pass

# 或使用 LINE 提供的 User ID 查詢工具
```

#### 方法三：透過 Webhook（技術性較高）
1. 在 Channel 設定中啟用 Webhook
2. 設定接收訊息的 URL
3. 當使用者傳送訊息時記錄 User ID

### 5. 設定程式

在 `main.py` 中填入取得的資訊：

```python
# LINE Bot API 設定
LINE_CHANNEL_ACCESS_TOKEN = "你的Channel_Access_Token"
LINE_USER_ID = "你的User_ID"
```

### 6. 加入 Bot 為好友

1. 在 Channel 的「Messaging API」頁籤找到 QR Code
2. 用 LINE 掃描 QR Code 加入 Bot 為好友
3. 確認 Bot 可以正常傳送訊息

## 🔧 進階設定

### Webhook 設定（可選）
如果需要接收使用者訊息或取得 User ID：

1. 在「Messaging API」頁籤中設定 Webhook URL
2. 啟用「Use webhook」
3. 實作 Webhook 接收端點

### Rich Menu 設定（可選）
可以為 Bot 添加豐富選單：

1. 在 Channel 設定中前往「Rich menus」
2. 設計和上傳選單圖片
3. 設定選單按鈕功能

## 💰 費用說明

### 免費額度
- 每月可免費傳送 **1,000 則** 訊息
- 適用於個人使用的監控程式

### 付費方案
如果超過免費額度：
- Light Plan: 月費 $5 USD，可傳送 15,000 則訊息
- Standard Plan: 月費 $100 USD，可傳送 45,000 則訊息

對於票券監控程式，免費額度通常足夠使用。

## 🛠️ 疑難排解

### 1. 訊息發送失敗
```
❌ LINE 訊息發送失敗: 401
回應內容: {"message":"Invalid access token"}
```
**解決方案**: 檢查 Channel Access Token 是否正確

### 2. 找不到使用者
```
❌ LINE 訊息發送失敗: 400
回應內容: {"message":"The user hasn't added the LINE Official Account as a friend"}
```
**解決方案**: 確認已將 Bot 加為 LINE 好友

### 3. User ID 不正確
```
❌ LINE 訊息發送失敗: 400
回應內容: {"message":"Invalid user id"}
```
**解決方案**: 檢查 User ID 格式是否正確（通常以 U 開頭）

### 4. 配額用盡
```
❌ LINE 訊息發送失敗: 429
回應內容: {"message":"Too Many Requests"}
```
**解決方案**: 等待配額重置或升級付費方案

## 📱 測試 Bot

設定完成後，可以執行以下簡單測試：

```python
def test_line_bot():
    test_message = "🧪 測試訊息：LINE Bot API 設定成功！"
    result = send_line_message(test_message)
    if result:
        print("✅ LINE Bot 設定測試成功！")
    else:
        print("❌ LINE Bot 設定測試失敗，請檢查設定")

# 在主程式開始前執行測試
test_line_bot()
```

## 🔄 從 LINE Notify 遷移

如果您之前使用 LINE Notify，主要差異：

1. **權杖類型**: 從 LINE Notify Token 改為 Channel Access Token
2. **API 端點**: 從 `notify-api.line.me` 改為 `api.line.me`
3. **訊息格式**: 從表單格式改為 JSON 格式
4. **接收者**: 從自動發送改為需要指定 User ID

## 📞 技術支援

- [LINE Developers 文件](https://developers.line.biz/en/docs/)
- [Messaging API 參考](https://developers.line.biz/en/reference/messaging-api/)
- [LINE Developers Community](https://www.line-community.me/)

---

設定完成後，您的高鐵監控程式就會透過您專屬的 LINE Bot 發送通知了！🚄