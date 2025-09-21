import time
import base64
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import ddddocr
from PIL import Image

# 測試設定
START_STATION = '2'         # 起始站 (台北)
END_STATION = '10'          # 終點站 (嘉義)
SEARCH_DATE = '2025/09/26'  # 查詢日期
SEARCH_TIME = '600P'        # 查詢時間
MAX_CAPTCHA_RETRIES = 3     # 測試用較少重試次數

def solve_captcha(driver, ocr_engine):
    """識別並輸入驗證碼"""
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
        captcha_input.clear()
        captcha_input.send_keys(captcha_text)
        
        return True, captcha_text
        
    except Exception as e:
        print(f"驗證碼識別過程中發生錯誤: {e}")
        return False, ""

def refresh_captcha(driver):
    """刷新驗證碼"""
    try:
        refresh_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-reload')
        refresh_button.click()
        time.sleep(2)  # 等待新驗證碼載入
        return True
    except Exception as e:
        print(f"刷新驗證碼失敗: {e}")
        return False

def test_full_automation():
    """測試完整自動化流程"""
    
    # 初始化 ddddocr
    print("初始化 ddddocr...")
    ocr = ddddocr.DdddOcr()
    
    # 設定 Selenium WebDriver - 強化反偵測
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    # 核心反偵測設定
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 安全和隱私設定
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins-discovery')
    
    # 基本設定
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # 偽裝為真實瀏覽器
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    
    # 額外的偽裝設定
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
    options.add_argument('--log-level=3')
    
    driver = webdriver.Chrome(service=service, options=options)
    
    # 執行 JavaScript 隱藏自動化痕跡
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['zh-TW', 'zh', 'en']})")
    driver.execute_script("window.navigator.chrome = {runtime: {}}")
    driver.execute_script("Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})})")
    
    wait = WebDriverWait(driver, 15)

    captcha_retry_count = 0
    
    while captcha_retry_count < MAX_CAPTCHA_RETRIES:
        try:
            print(f"開始測試 (嘗試 {captcha_retry_count + 1}/{MAX_CAPTCHA_RETRIES})")
            driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')
            time.sleep(3)

            # 首先處理 Cookie 同意頁面
            try:
                agree_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我同意')]")))
                agree_button.click()
                time.sleep(3)
                print("✓ 已處理 Cookie 同意")
            except:
                print("沒有 Cookie 同意頁面")
            
            # 等待頁面完全載入後再檢查阻擋狀態
            time.sleep(5)
            
            # 檢查是否被阻擋
            page_source = driver.page_source.lower()
            if '請稍候' in page_source or '請稍后' in page_source or 'loading' in page_source or '載入中' in page_source:
                print("❌ 網站顯示「請稍候」，被偵測為自動化行為")
                print("   嘗試等待更長時間...")
                time.sleep(10)  # 等待更久
                
                # 重新檢查
                page_source = driver.page_source.lower()
                if '請稍候' in page_source or '請稍后' in page_source:
                    print("   仍然被阻擋，跳過此次嘗試")
                    captcha_retry_count += 1
                    continue
                else:
                    print("   ✓ 阻擋解除，繼續執行")

            # 填寫表單
            
            # 選擇車站
            start_station = wait.until(EC.element_to_be_clickable((By.NAME, 'selectStartStation')))
            Select(start_station).select_by_value(START_STATION)
            print("✓ 已選擇起始站")
            
            end_station = driver.find_element(By.NAME, 'selectDestinationStation')
            Select(end_station).select_by_value(END_STATION)
            print("✓ 已選擇終點站")
            
            # 設定日期
            driver.execute_script(f"""
                var element = document.getElementById('toTimeInputField');
                element.value = '{SEARCH_DATE}';
                element.dispatchEvent(new Event('change', {{ bubbles: true }}));
            """)
            print("✓ 已設定日期")
            
            # 選擇時間
            time_select = driver.find_element(By.NAME, 'toTimeTable')
            Select(time_select).select_by_value(SEARCH_TIME)
            print("✓ 已選擇時間")

            # 自動識別驗證碼
            print("開始識別驗證碼...")
            captcha_success, captcha_text = solve_captcha(driver, ocr)
            
            if not captcha_success:
                print("❌ 驗證碼識別失敗，刷新重試...")
                refresh_captcha(driver)
                captcha_retry_count += 1
                time.sleep(2)
                continue
            
            print(f"✓ 驗證碼識別成功: {captcha_text}")
            
            # 點擊查詢按鈕
            submit_button = driver.find_element(By.ID, 'SubmitButton')
            submit_button.click()
            print("✓ 已點擊查詢按鈕")

            # 等待結果
            time.sleep(8)

            # 檢查是否有驗證碼錯誤
            page_source = driver.page_source.lower()
            if '驗證碼錯誤' in page_source or 'captcha' in page_source or '驗證失敗' in page_source or '安全碼錯誤' in page_source:
                print(f"❌ 驗證碼 '{captcha_text}' 錯誤，重新嘗試...")
                captcha_retry_count += 1
                time.sleep(2)
                continue

            # 檢查查詢結果
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # 嘗試不同的選擇器找班次
            selectors_to_try = [
                'tr.trip-column',
                'tr[class*="trip"]',
                'table tr td',
                '.train-info'
            ]
            
            train_rows = []
            for selector in selectors_to_try:
                train_rows = soup.select(selector)
                if train_rows:
                    print(f"使用選擇器 '{selector}' 找到 {len(train_rows)} 個元素")
                    break
            
            if train_rows:
                print("🎉 查詢成功！找到班次資訊")
                
                # 分析可訂票班次
                available_count = 0
                for i, row in enumerate(train_rows[:5]):
                    row_text = row.get_text().strip()
                    if row_text:
                        print(f"班次 {i+1}: {row_text[:100]}...")
                        
                        # 檢查是否可訂票
                        if '訂票' in row_text and '額滿' not in row_text:
                            available_count += 1
                
                print(f"找到 {available_count} 個可能可訂票的班次")
                
            else:
                print("❌ 沒有找到班次資訊")
                # 儲存網頁以供除錯
                with open('debug_final.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("已儲存網頁到 debug_final.html")
            
            # 測試成功，跳出重試迴圈
            print("✅ 自動化測試完成！")
            break
            
        except Exception as e:
            print(f"❌ 測試過程中發生錯誤: {e}")
            captcha_retry_count += 1
            if captcha_retry_count < MAX_CAPTCHA_RETRIES:
                print(f"將於 2 秒後重試...")
                time.sleep(2)
            continue
    
    if captcha_retry_count >= MAX_CAPTCHA_RETRIES:
        print(f"❌ 達到最大重試次數 ({MAX_CAPTCHA_RETRIES})，測試失敗")
    
    print("測試完成，瀏覽器將在 10 秒後關閉...")
    time.sleep(10)
    driver.quit()

if __name__ == "__main__":
    test_full_automation()