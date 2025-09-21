import time
import base64
import io
import random
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import ddddocr
from PIL import Image
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# --- 1. 使用者設定區 (請修改以下設定) ---

# 高鐵查詢設定
START_STATION = '2'         # 起始站 (台北)
END_STATION = '9'          # 終點站 (雲林)
SEARCH_DATE = '2025/09/26'  # 查詢日期 (格式：YYYY/MM/DD)
SEARCH_TIME = '600A'        # 查詢時間 (網站格式：600P = 18:00)

# 程式執行設定
CHECK_INTERVAL_SECONDS = 90  # 查無票時的冷卻間隔 (秒)
MAX_CAPTCHA_RETRIES = 99      # 驗證碼最大重試次數
CAPTCHA_RETRY_DELAY = 1      # 驗證碼重試間隔 (秒)

# LINE Bot API 設定 (從環境變數載入)
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', "")  # 從 .env 檔案讀取
LINE_USER_ID = os.getenv('LINE_USER_ID', "")                           # 從 .env 檔案讀取

# --- 2. LINE Bot API 通知函式 ---

def send_line_message(message):
    """使用 LINE Bot API 發送訊息"""
    if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_USER_ID:
        print("(LINE Bot API 權杖或 User ID 未設定，跳過訊息發送)")
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
                    "text": message
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✓ LINE 訊息發送成功")
            return True
        else:
            print(f"❌ LINE 訊息發送失敗: {response.status_code}")
            print(f"回應內容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ LINE 訊息發送錯誤: {e}")
        return False

# --- 2. 人類行為模擬函式 ---

def human_like_delay(min_seconds=1, max_seconds=3):
    """模擬人類操作的隨機延遲"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def human_like_click(driver, element):
    """模擬人類點擊行為"""
    # 隨機移動滑鼠到元素
    actions = ActionChains(driver)
    actions.move_to_element(element)
    human_like_delay(0.5, 1.5)
    actions.click(element)
    actions.perform()
    human_like_delay(0.5, 1.0)

def human_like_type(element, text):
    """模擬人類打字行為"""
    element.clear()
    human_like_delay(0.3, 0.8)
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))  # 隨機打字速度
    human_like_delay(0.3, 0.8)

# --- 3. 驗證碼識別函式 ---

def solve_captcha(driver, ocr_engine):
    """
    識別並輸入驗證碼
    :param driver: Selenium WebDriver
    :param ocr_engine: ddddocr 引擎
    :return: 是否成功識別並輸入驗證碼
    """
    try:
        # 找到驗證碼圖片
        captcha_img = driver.find_element(By.CSS_SELECTOR, 'img.captcha-img')
        
        # 獲取驗證碼圖片的 base64 數據
        captcha_base64 = driver.execute_script("""
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            var img = arguments[0];
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL('image/png').substring(22);
        """, captcha_img)
        
        # 解碼 base64 圖片
        captcha_data = base64.b64decode(captcha_base64)
        
        # 使用 ddddocr 識別驗證碼
        captcha_text_raw = ocr_engine.classification(captcha_data)
        captcha_text = captcha_text_raw.upper()  # 轉換為大寫
        print(f"識別的驗證碼 (原始): {captcha_text_raw}")
        print(f"識別的驗證碼 (大寫): {captcha_text}")
        
        # 輸入驗證碼
        captcha_input = driver.find_element(By.ID, 'securityCode')
        human_like_click(driver, captcha_input)
        human_like_type(captcha_input, captcha_text)
        
        return True, captcha_text
        
    except Exception as e:
        print(f"驗證碼識別過程中發生錯誤: {e}")
        return False, ""

def refresh_captcha(driver):
    """刷新驗證碼"""
    try:
        refresh_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-reload')
        refresh_button.click()
        time.sleep(1)  # 等待新驗證碼載入
        return True
    except Exception as e:
        print(f"刷新驗證碼失敗: {e}")
        return False

# --- 3. 高鐵票券檢查函式 ---

def check_thsr_tickets():
    """啟動瀏覽器並檢查高鐵是否有票 - 無限監控版本"""
    
    # 初始化 ddddocr
    ocr = ddddocr.DdddOcr()
    
    # 設定 Selenium WebDriver - 使用 webdriver-manager 自動管理 ChromeDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    # 強化反偵測設定
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # 設定更真實的 User-Agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    # 隱藏 Chrome 正在被自動化軟件控制的通知
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    
    # 設定一些額外的 prefs 來模擬真實瀏覽器
    prefs = {
        "profile.default_content_setting_values": {
            "notifications": 2,
            "media_stream": 2,
        },
        "profile.managed_default_content_settings": {
            "images": 1
        }
    }
    options.add_experimental_option("prefs", prefs)
    
    options.add_argument('--log-level=3') # 減少不必要的日誌輸出
    
    driver = webdriver.Chrome(service=service, options=options)
    
    # 執行多個 JavaScript 來進一步隱藏自動化痕跡
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['zh-TW', 'zh', 'en']})")
    driver.execute_script("window.navigator.chrome = {runtime: {}}")
    driver.execute_script("Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})})")
    
    wait = WebDriverWait(driver, 15)

    try:
        # 初始化頁面和表單
        print("正在開啟高鐵訂票網站...")
        driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')
        time.sleep(3)
        
        # 處理 Cookie 同意頁面
        try:
            agree_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我同意')]")))
            print("發現 Cookie 同意頁面，正在點擊「我同意」...")
            human_like_click(driver, agree_button)
            human_like_delay(2, 4)
        except:
            print("沒有發現 Cookie 同意頁面，或已經同意過了")

        # 等待頁面完全載入
        human_like_delay(3, 5)
        
        # 檢查是否卡在「請稍後」
        page_source = driver.page_source.lower()
        if '請稍後' in page_source or '請稍后' in page_source or 'loading' in page_source or '載入中' in page_source:
            print("⚠️ 網站顯示「請稍後」，被偵測為自動化行為")
            print("但仍嘗試繼續執行...")
        else:
            print("✓ 沒有被阻擋，繼續執行")

        # 填寫表單
        print("正在填寫查詢表單...")
        
        # 選擇起始站
        start_station_select = wait.until(EC.element_to_be_clickable((By.NAME, 'selectStartStation')))
        human_like_click(driver, start_station_select)
        human_like_delay(0.5, 1.5)
        Select(start_station_select).select_by_value(START_STATION)
        print(f"已選擇起始站: {START_STATION}")
        human_like_delay(1, 2)
        
        # 選擇終點站
        end_station_select = driver.find_element(By.NAME, 'selectDestinationStation')
        human_like_click(driver, end_station_select)
        human_like_delay(0.5, 1.5)
        Select(end_station_select).select_by_value(END_STATION)
        print(f"已選擇終點站: {END_STATION}")
        human_like_delay(1, 2)
        
        # 設定日期
        print("正在設定日期...")
        driver.execute_script(f"""
            var element = document.getElementById('toTimeInputField');
            element.value = '{SEARCH_DATE}';
            element.dispatchEvent(new Event('change', {{ bubbles: true }}));
            element.dispatchEvent(new Event('input', {{ bubbles: true }}));
        """)
        print(f"已設定日期: {SEARCH_DATE}")
        
        # 選擇時間
        time_select = driver.find_element(By.NAME, 'toTimeTable')
        human_like_click(driver, time_select)
        human_like_delay(0.5, 1.5)
        Select(time_select).select_by_value(SEARCH_TIME)
        print(f"已選擇時間: {SEARCH_TIME}")
        human_like_delay(1, 2)

        print(f"查詢設定：{SEARCH_DATE} {SEARCH_TIME} 從車站{START_STATION}到車站{END_STATION}")
        
        # 開始票券監控循環
        captcha_retry_count = 0
        monitoring_round = 1
        
        while True:  # 無限循環直到找到票
            print(f"\n=== 第 {monitoring_round} 輪監控 ===")
            
            if captcha_retry_count >= MAX_CAPTCHA_RETRIES:
                print("❌ 驗證碼重試次數用盡，重置計數器並繼續監控...")
                captcha_retry_count = 0
                monitoring_round += 1
                
                # 重新載入頁面
                driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')
                time.sleep(3)
                
                # 重新處理 Cookie 和表單
                try:
                    agree_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我同意')]")))
                    agree_button.click()
                    time.sleep(3)
                except:
                    pass
                
                time.sleep(3)
                start_station = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'selectStartStation')))
                Select(start_station).select_by_value(START_STATION)
                
                end_station = driver.find_element(By.NAME, 'selectDestinationStation')
                Select(end_station).select_by_value(END_STATION)
                
                driver.execute_script(f"""
                    var element = document.getElementById('toTimeInputField');
                    element.value = '{SEARCH_DATE}';
                    element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                """)
                
                time_select = driver.find_element(By.NAME, 'toTimeTable')
                Select(time_select).select_by_value(SEARCH_TIME)
            
            print(f"驗證碼嘗試: {captcha_retry_count + 1}/{MAX_CAPTCHA_RETRIES}")
            
            # 自動識別並輸入驗證碼
            print("正在識別驗證碼...")
            human_like_delay(1, 2)
            captcha_success, captcha_text = solve_captcha(driver, ocr)
            
            if not captcha_success:
                print("驗證碼識別失敗，刷新重試...")
                refresh_captcha(driver)
                captcha_retry_count += 1
                human_like_delay(CAPTCHA_RETRY_DELAY, CAPTCHA_RETRY_DELAY + 2)
                continue
            
            print(f"✓ 驗證碼識別成功: {captcha_text}")
            
            # 模擬人類檢查表單的行為
            human_like_delay(1, 3)
            
            # 點擊查詢按鈕
            submit_button = driver.find_element(By.ID, 'SubmitButton')
            human_like_click(driver, submit_button)
            print("已點擊查詢按鈕")

            # 等待查詢結果載入
            time.sleep(8)

            # 檢查查詢結果
            result_source = driver.page_source
            print("正在分析查詢結果...")
            
            # 情況 1: 驗證碼錯誤 (檢測碼輸入錯誤)
            if '檢測碼輸入錯誤' in result_source or '驗證碼錯誤' in result_source or '安全碼錯誤' in result_source:
                print(f"❌ 驗證碼 '{captcha_text}' 錯誤，準備重試...")
                
                # 回到表單頁面重新開始
                print("正在重新載入頁面...")
                driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')
                time.sleep(3)
                
                # 重新處理 Cookie 同意
                try:
                    agree_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我同意')]")))
                    agree_button.click()
                    time.sleep(3)
                except:
                    pass
                
                # 重新填寫表單
                print("重新填寫表單...")
                time.sleep(3)
                
                start_station = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'selectStartStation')))
                Select(start_station).select_by_value(START_STATION)
                
                end_station = driver.find_element(By.NAME, 'selectDestinationStation')
                Select(end_station).select_by_value(END_STATION)
                
                driver.execute_script(f"""
                    var element = document.getElementById('toTimeInputField');
                    element.value = '{SEARCH_DATE}';
                    element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                """)
                
                time_select = driver.find_element(By.NAME, 'toTimeTable')
                Select(time_select).select_by_value(SEARCH_TIME)
                
                captcha_retry_count += 1
                print(f"表單重新填寫完成，準備第 {captcha_retry_count + 1} 次驗證碼嘗試...")
                time.sleep(2)
            
            # 情況 2: 查無可售車次 (需要等待後重試)
            elif '去程查無可售車次' in result_source or '選購的車票已售完' in result_source:
                print("⚠️ 查無可售車次或已售完，將等待後重新查詢...")
                
                # 冷卻時間倒數計時 - 每秒顯示
                for remaining in range(CHECK_INTERVAL_SECONDS, 0, -1):
                    print(f"等待中... 剩餘 {remaining} 秒", end='\r', flush=True)
                    time.sleep(1)
                
                print(f"\n冷卻時間結束，重新查詢...")
                
                # 回到表單頁面重新查詢
                driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')
                time.sleep(3)
                
                # 重新處理 Cookie 同意
                try:
                    agree_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我同意')]")))
                    agree_button.click()
                    time.sleep(3)
                except:
                    pass
                
                # 重新填寫表單
                print("重新填寫表單...")
                time.sleep(3)
                
                start_station = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'selectStartStation')))
                Select(start_station).select_by_value(START_STATION)
                
                end_station = driver.find_element(By.NAME, 'selectDestinationStation')
                Select(end_station).select_by_value(END_STATION)
                
                driver.execute_script(f"""
                    var element = document.getElementById('toTimeInputField');
                    element.value = '{SEARCH_DATE}';
                    element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                """)
                
                time_select = driver.find_element(By.NAME, 'toTimeTable')
                Select(time_select).select_by_value(SEARCH_TIME)
                
                print("表單重新填寫完成，準備重新識別驗證碼...")
                # 重置驗證碼計數器，因為這不是驗證碼問題
                captcha_retry_count = 0
                monitoring_round += 1
            
            # 情況 3: 查詢成功，有可預訂班次
            elif 'uk-alert-danger' not in result_source and ('班次' in result_source or 'train' in result_source or '車次' in result_source):
                # 進一步檢查是否真的有可訂票班次
                if '訂票' in result_source and '額滿' not in result_source:
                    print("\n" + "*"*60)
                    print("🎉 查詢有票！趕快訂購！")
                    print("*"*60)
                    print(f"查詢目標：{SEARCH_DATE} 從 {START_STATION} 到 {END_STATION}")
                    print("請儘速前往高鐵網站訂票：https://irs.thsrc.com.tw/")
                    print("*"*60 + "\n")
                    
                    # 發送 LINE 通知 - 找到車票
                    success_message = f"🎉 高鐵有票了！\n{SEARCH_DATE} {SEARCH_TIME}\n{START_STATION} → {END_STATION}\n請儘速前往訂票：https://irs.thsrc.com.tw/"
                    send_line_message(success_message)
                    
                    return True, ["找到可預訂班次"]  # 返回成功結果
                else:
                    print("⚠️ 有班次資訊但無可預訂座位，等待後重試...")
                    # 按照查無可預訂的邏輯處理
                    for remaining in range(CHECK_INTERVAL_SECONDS, 0, -1):
                        print(f"等待中... 剩餘 {remaining} 秒", end='\r', flush=True)
                        time.sleep(1)
                    print(f"\n冷卻時間結束，重新查詢...")
                    captcha_retry_count = 0
                    monitoring_round += 1
                    continue
            
            # 情況 4: 其他未知結果
            else:
                print("⚠️ 查詢結果不明確，保存頁面供分析...")
                with open('unknown_result.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("已保存結果頁面至 unknown_result.html")
                
                # 檢查是否有任何錯誤訊息
                if 'uk-alert-danger' in result_source:
                    print("發現錯誤訊息，但無法識別具體類型")
                    try:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        error_msgs = soup.select('.feedbackPanelERROR')
                        for msg in error_msgs:
                            print(f"錯誤訊息: {msg.get_text().strip()}")
                    except:
                        pass
                
                return False, ["未知錯誤"]  # 返回失敗結果
        
    except Exception as e:
        print(f"查詢過程中發生錯誤: {e}")
        return False, [f"錯誤: {e}"]
        
    finally:
        driver.quit()

# --- 4. 主程式執行迴圈 ---

if __name__ == "__main__":
    print("高鐵票券自動偵測程式已啟動...")
    print(f"監控設定：{SEARCH_DATE} {SEARCH_TIME} 從車站{START_STATION}到車站{END_STATION}")
    print(f"查無票時冷卻間隔：{CHECK_INTERVAL_SECONDS} 秒")
    print(f"驗證碼最大重試：{MAX_CAPTCHA_RETRIES} 次")
    print("=" * 60)
    
    # 發送 LINE 通知 - 程式啟動
    startup_message = f"🚀 高鐵監控程式已啟動\n目標日期：{SEARCH_DATE} {SEARCH_TIME}\n路線：{START_STATION} → {END_STATION}\n開始監控中..."
    send_line_message(startup_message)
    
    try:
        # 執行無限監控，直到找到票為止
        is_ticket_available, trains = check_thsr_tickets()
        
        if is_ticket_available:
            print("監控結束：已找到可預訂班次！")
        else:
            print("監控結束：發生錯誤或未知狀況")
            
    except KeyboardInterrupt:
        print("\n\n用戶中斷監控程式")
        # 發送 LINE 通知 - 用戶手動結束
        end_message = f"⏹️ 高鐵監控程式已手動停止\n監控目標：{SEARCH_DATE} {SEARCH_TIME}\n{START_STATION} → {END_STATION}"
        send_line_message(end_message)
    except Exception as e:
        print(f"\n\n主程式發生未預期錯誤: {e}")
        # 發送 LINE 通知 - 程式錯誤結束
        error_message = f"❌ 高鐵監控程式發生錯誤\n錯誤內容：{str(e)}\n監控目標：{SEARCH_DATE} {SEARCH_TIME}\n{START_STATION} → {END_STATION}"
        send_line_message(error_message)
    
    print("程式結束")