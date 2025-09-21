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
MAX_CAPTCHA_RETRIES = 3     # 單次測試用較少重試次數

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
        captcha_text = ocr_engine.classification(captcha_data)
        print(f"識別的驗證碼: {captcha_text}")
        
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

def single_test():
    """單次完整測試"""
    
    print("=== 高鐵票券查詢單次測試開始 ===")
    
    # 初始化 ddddocr
    print("初始化 ddddocr...")
    ocr = ddddocr.DdddOcr()
    
    # 設定 Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    # 隱藏自動化痕跡，避免被高鐵網站偵測
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 穩定性選項
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--log-level=3')
    
    driver = webdriver.Chrome(service=service, options=options)
    
    # 執行 JavaScript 來進一步隱藏自動化痕跡
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    wait = WebDriverWait(driver, 15)

    captcha_retry_count = 0
    
    try:
        while captcha_retry_count < MAX_CAPTCHA_RETRIES:
            print(f"\n--- 嘗試 {captcha_retry_count + 1}/{MAX_CAPTCHA_RETRIES} ---")
            
            try:
                print("1. 正在開啟高鐵訂票網站...")
                driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')
                time.sleep(3)

                print("2. 處理 Cookie 同意頁面...")
                try:
                    agree_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我同意')]")))
                    agree_button.click()
                    time.sleep(3)
                    print("   ✓ 已點擊同意")
                except:
                    print("   沒有 Cookie 同意頁面")

                print("3. 填寫表單...")
                time.sleep(3)
                
                # 選擇起始站
                print("   3.1 選擇起始站...")
                start_station = wait.until(EC.element_to_be_clickable((By.NAME, 'selectStartStation')))
                Select(start_station).select_by_value(START_STATION)
                print("   ✓ 已選擇台北")
                
                # 選擇終點站
                print("   3.2 選擇終點站...")
                end_station = driver.find_element(By.NAME, 'selectDestinationStation')
                Select(end_station).select_by_value(END_STATION)
                print("   ✓ 已選擇嘉義")
                
                # 設定日期
                print("   3.3 設定日期...")
                driver.execute_script(f"""
                    var element = document.getElementById('toTimeInputField');
                    element.value = '{SEARCH_DATE}';
                    element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                """)
                # 驗證日期是否設定成功
                actual_date = driver.execute_script("return document.getElementById('toTimeInputField').value")
                print(f"   ✓ 已設定日期: {actual_date}")
                
                # 選擇時間
                print("   3.4 選擇時間...")
                time_select = driver.find_element(By.NAME, 'toTimeTable')
                Select(time_select).select_by_value(SEARCH_TIME)
                print("   ✓ 已選擇 18:00")

                print(f"4. 查詢設定完成：{SEARCH_DATE} 18:00 台北→嘉義")
                
                # 自動識別驗證碼
                print("5. 識別驗證碼...")
                captcha_success, captcha_text = solve_captcha(driver, ocr)
                
                if not captcha_success:
                    print("   ❌ 驗證碼識別失敗，刷新重試...")
                    refresh_captcha(driver)
                    captcha_retry_count += 1
                    time.sleep(2)
                    continue
                
                print(f"   ✓ 驗證碼識別成功: {captcha_text}")
                
                # 點擊查詢按鈕
                print("6. 提交查詢...")
                submit_button = driver.find_element(By.ID, 'SubmitButton')
                submit_button.click()
                print("   ✓ 已點擊查詢按鈕")

                # 等待結果
                print("7. 等待查詢結果...")
                time.sleep(10)

                # 檢查驗證碼錯誤
                page_source = driver.page_source.lower()
                if '驗證碼錯誤' in page_source or 'captcha' in page_source or '驗證失敗' in page_source or '安全碼錯誤' in page_source:
                    print(f"   ❌ 驗證碼 '{captcha_text}' 錯誤，重新嘗試...")
                    captcha_retry_count += 1
                    time.sleep(2)
                    continue

                print("8. 分析查詢結果...")
                
                # 分析結果頁面
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # 嘗試多種選擇器
                selectors_to_try = [
                    'tr.trip-column',
                    'tr[class*="trip"]', 
                    'table tbody tr',
                    '.train-info',
                    'tr:has(.btn-primary)',
                    'tr:has(button)'
                ]
                
                train_rows = []
                used_selector = ""
                
                for selector in selectors_to_try:
                    train_rows = soup.select(selector)
                    if train_rows and len(train_rows) > 0:
                        used_selector = selector
                        print(f"   使用選擇器 '{selector}' 找到 {len(train_rows)} 個元素")
                        break
                
                if train_rows:
                    print("   ✓ 查詢成功！分析班次資訊...")
                    
                    found_ticket = False
                    available_trains = []
                    
                    for i, row in enumerate(train_rows):
                        row_text = row.get_text().strip()
                        if row_text and len(row_text) > 10:  # 過濾空白行
                            print(f"   班次 {i+1}: {row_text[:80]}...")
                            
                            # 檢查是否可訂票
                            button_cell = row.select_one('td.book-seat-content')
                            if button_cell:
                                button = button_cell.select_one('button.btn-primary:not([disabled])')
                                if button:
                                    found_ticket = True
                                    try:
                                        train_id = row.select_one('td:nth-of-type(1) span.train-code')
                                        departure_time = row.select_one('td:nth-of-type(2) span.font-16px')
                                        arrival_time = row.select_one('td:nth-of-type(3) span.font-16px')
                                        
                                        if train_id and departure_time and arrival_time:
                                            train_info = f"車次 {train_id.text.strip()} ({departure_time.text.strip()} - {arrival_time.text.strip()})"
                                            available_trains.append(train_info)
                                            print(f"   🎉 可訂票: {train_info}")
                                    except:
                                        print(f"   🎉 班次 {i+1} 可訂票（無法解析詳細資訊）")
                                        available_trains.append(f"班次 {i+1}")
                            
                            # 只顯示前 10 個班次避免輸出過長
                            if i >= 9:
                                break
                    
                    if found_ticket:
                        print(f"\n🎉🎉🎉 發現 {len(available_trains)} 個可訂票班次！")
                        for train in available_trains:
                            print(f"   - {train}")
                    else:
                        print("   目前所有班次都已額滿")
                    
                    # 測試成功，結束
                    break
                    
                else:
                    print("   ❌ 沒有找到班次資訊")
                    print("   可能的原因：")
                    print("   - 查詢參數錯誤")
                    print("   - 網頁結構變更")
                    print("   - 驗證碼仍然錯誤")
                    
                    # 保存網頁供除錯
                    with open('debug_single_test.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print("   已儲存網頁到 debug_single_test.html")
                    break
                
            except Exception as e:
                print(f"   ❌ 過程中發生錯誤: {e}")
                captcha_retry_count += 1
                if captcha_retry_count < MAX_CAPTCHA_RETRIES:
                    print(f"   將於 2 秒後重試...")
                    time.sleep(2)
                continue
        
        if captcha_retry_count >= MAX_CAPTCHA_RETRIES:
            print(f"\n❌ 達到最大重試次數 ({MAX_CAPTCHA_RETRIES})，測試結束")
            
    finally:
        print("\n測試完成，瀏覽器將在 15 秒後關閉...")
        print("請檢查瀏覽器中的最終狀態")
        time.sleep(15)
        driver.quit()
        
    print("\n=== 單次測試結束 ===")

if __name__ == "__main__":
    single_test()