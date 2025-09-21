"""
LINE Bot API 測試腳本
用於測試 LINE Bot 設定和取得 User ID

使用步驟：
1. 在 .env 檔案中設定 LINE_CHANNEL_ACCESS_TOKEN 和 LINE_USER_ID
2. 執行此腳本測試 Bot 基本功能
3. 如果需要取得 User ID，請參考說明文件中的方法
"""

import requests
import os
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# 從環境變數讀取設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', "")
LINE_USER_ID = os.getenv('LINE_USER_ID', "")

def test_line_bot_token():
    """測試 Channel Access Token 是否有效"""
    if not LINE_CHANNEL_ACCESS_TOKEN:
        print("❌ 請先設定 LINE_CHANNEL_ACCESS_TOKEN")
        return False
    
    try:
        # 測試 API 呼叫 - 取得 Bot 資訊
        url = "https://api.line.me/v2/bot/info"
        headers = {
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            print("✅ Channel Access Token 有效！")
            print(f"Bot 名稱: {bot_info.get('displayName', 'N/A')}")
            print(f"Bot ID: {bot_info.get('userId', 'N/A')}")
            return True
        else:
            print(f"❌ Token 驗證失敗: {response.status_code}")
            print(f"錯誤訊息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")
        return False

def send_test_message():
    """發送測試訊息"""
    if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_USER_ID:
        print("❌ 請確認已設定 LINE_CHANNEL_ACCESS_TOKEN 和 LINE_USER_ID")
        return False
    
    try:
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "to": LINE_USER_ID,
            "messages": [
                {
                    "type": "text",
                    "text": "🧪 LINE Bot API 測試成功！\n您的高鐵監控程式已準備就緒。"
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ 測試訊息發送成功！請檢查您的 LINE")
            return True
        else:
            print(f"❌ 訊息發送失敗: {response.status_code}")
            print(f"錯誤訊息: {response.text}")
            
            # 提供常見錯誤的解決建議
            if response.status_code == 400:
                error_data = response.json()
                if "The user hasn't added the LINE Official Account as a friend" in str(error_data):
                    print("💡 解決方案: 請先將 Bot 加為 LINE 好友")
                elif "Invalid user id" in str(error_data):
                    print("💡 解決方案: 請檢查 User ID 是否正確")
            elif response.status_code == 401:
                print("💡 解決方案: 請檢查 Channel Access Token 是否正確")
            
            return False
            
    except Exception as e:
        print(f"❌ 發送過程發生錯誤: {e}")
        return False

def get_user_id_instructions():
    """顯示取得 User ID 的說明"""
    print("\n📋 取得 User ID 的方法：")
    print("\n方法一：透過 LINE Developers Console")
    print("1. 前往 https://developers.line.biz/console/")
    print("2. 選擇您的 Channel")
    print("3. 前往 'Basic settings' 頁籤")
    print("4. 複製 'Your user ID' 欄位的值")
    
    print("\n方法二：透過 LINE Official Account Manager")
    print("1. 前往 https://manager.line.biz/")
    print("2. 選擇您的官方帳號")
    print("3. 前往 '設定' > '回應設定'")
    print("4. 查看基本資訊中的 User ID")
    
    print("\n方法三：使用 LINE Bot SDK（進階）")
    print("1. 設定 Webhook URL")
    print("2. 讓使用者傳送訊息給 Bot")
    print("3. 從 Webhook 事件中取得 User ID")
    
    print(f"\n💡 User ID 格式範例: U1234567890abcdef1234567890abcdef")

if __name__ == "__main__":
    print("=== LINE Bot API 測試工具 ===\n")
    
    # 1. 測試 Token 有效性
    print("1. 測試 Channel Access Token...")
    token_valid = test_line_bot_token()
    
    if not token_valid:
        print("\n❌ 請先確認 Channel Access Token 設定正確")
        print("參考設定說明: LINE_Bot_API_設定說明.md")
        exit(1)
    
    # 2. 測試訊息發送
    print("\n2. 測試訊息發送...")
    if LINE_USER_ID:
        message_sent = send_test_message()
        if message_sent:
            print("\n🎉 所有測試通過！LINE Bot API 設定完成")
        else:
            print("\n❌ 訊息發送失敗，請檢查設定")
    else:
        print("⚠️ User ID 未設定，跳過訊息發送測試")
        get_user_id_instructions()
    
    print("\n=== 測試完成 ===")