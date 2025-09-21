import time
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import ddddocr

# 測試設定
START_STATION = '2'         # 起始站 (台北)
END_STATION = '10'          # 終點站 (嘉義)
SEARCH_DATE = '2025/09/26'  # 查詢日期
SEARCH_TIME = '600A'        # 查詢時間

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
        print(f"   識別的驗證碼 (原始): {captcha_text_raw}")
        print(f"   識別的驗證碼 (大寫): {captcha_text}")
        
        # 輸入驗證碼
        captcha_input = driver.find_element(By.ID, 'securityCode')
        captcha_input.clear()
        captcha_input.send_keys(captcha_text)
        
        return True, captcha_text
        
    except Exception as e:
        print(f"   ❌ 驗證碼識別過程中發生錯誤: {e}")
        return False, ""

def refresh_captcha(driver):
    """刷新驗證碼"""
    try:
        refresh_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-reload')
        refresh_button.click()
        time.sleep(2)  # 等待新驗證碼載入
        print("   ✓ 已刷新驗證碼")
        return True
    except Exception as e:
        print(f"   ❌ 刷新驗證碼失敗: {e}")
        return False

def test_anti_detection():
    """測試反偵測設定並執行完整表單填寫"""
    
    print("=== 測試反偵測設定與完整流程 ===")
    
    # 初始化 ddddocr
    print("初始化 ddddocr...")
    ocr = ddddocr.DdddOcr()
    
    # 設定反偵測的 Chrome 選項
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    # 關鍵反偵測設定
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 強化設定
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins-discovery')
    
    # 其他設定
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
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

    try:
        print("1. 正在開啟高鐵訂票網站...")
        driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')
        time.sleep(3)
        
        print("2. 檢查網頁標題...")
        print(f"   頁面標題: {driver.title}")
        
        if "高鐵" in driver.title:
            print("   ✓ 成功載入高鐵網站！")
        else:
            print("   ❌ 可能被偵測或載入失敗")
        
        print("3. 處理 Cookie 同意頁面...")
        try:
            agree_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我同意')]")))
            print("   ✓ 發現 Cookie 同意頁面，正在點擊...")
            agree_button.click()
            time.sleep(3)
            print("   ✓ 已點擊同意")
        except:
            print("   沒有 Cookie 同意頁面")
        
        # 等待頁面完全載入
        time.sleep(5)
        
        print("4. 檢查頁面阻擋狀態...")
        page_source = driver.page_source.lower()
        if '請稍候' in page_source or '請稍后' in page_source or 'loading' in page_source or '載入中' in page_source:
            print("   ⚠️ 網站顯示「請稍候」，被偵測為自動化行為")
            print("   但仍嘗試繼續執行，看看能否填寫表單...")
        else:
            print("   ✓ 沒有被阻擋，繼續執行")
        
        print("5. 檢查並填寫表單...")
        try:
            # 選擇起始站
            start_station = wait.until(EC.element_to_be_clickable((By.NAME, 'selectStartStation')))
            Select(start_station).select_by_value(START_STATION)
            print("   ✓ 已選擇起始站")
            
            # 選擇終點站
            end_station = driver.find_element(By.NAME, 'selectDestinationStation')
            Select(end_station).select_by_value(END_STATION)
            print("   ✓ 已選擇終點站")
            
            # 設定日期
            driver.execute_script(f"""
                var element = document.getElementById('toTimeInputField');
                element.value = '{SEARCH_DATE}';
                element.dispatchEvent(new Event('change', {{ bubbles: true }}));
            """)
            print("   ✓ 已設定日期")
            
            # 選擇時間
            time_select = driver.find_element(By.NAME, 'toTimeTable')
            Select(time_select).select_by_value(SEARCH_TIME)
            print("   ✓ 已選擇時間")
            
            print("6. 開始票券監控 (驗證碼最多重試 3 次，查無票時 90 秒後重試)...")
            max_captcha_retries = 3
            captcha_retry_count = 0
            monitoring_round = 1
            
            while True:  # 無限循環直到找到票
                print(f"\n=== 第 {monitoring_round} 輪監控 ===")
                
                if captcha_retry_count >= max_captcha_retries:
                    print("   ❌ 驗證碼重試次數用盡，重置計數器並繼續監控...")
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
                
                print(f"   驗證碼嘗試: {captcha_retry_count + 1}/{max_captcha_retries}")
                
                captcha_success, captcha_text = solve_captcha(driver, ocr)
                
                if not captcha_success:
                    print("   ❌ 驗證碼識別失敗，刷新重試...")
                    if refresh_captcha(driver):
                        captcha_retry_count += 1
                        time.sleep(2)
                        continue
                    else:
                        captcha_retry_count += 1
                        continue
                
                print(f"   ✓ 驗證碼識別成功: {captcha_text}")
                
                print("7. 提交查詢...")
                submit_button = driver.find_element(By.ID, 'SubmitButton')
                submit_button.click()
                print("   ✓ 已點擊查詢按鈕")
                
                # 等待結果
                print("8. 等待查詢結果...")
                time.sleep(8)
                
                # 檢查結果
                result_source = driver.page_source
                print("   正在分析查詢結果...")
                
                # 情況 1: 驗證碼錯誤 (檢測碼輸入錯誤)
                if '檢測碼輸入錯誤' in result_source or '驗證碼錯誤' in result_source or '安全碼錯誤' in result_source:
                    print(f"   ❌ 驗證碼 '{captcha_text}' 錯誤，準備重試...")
                    
                    # 回到表單頁面重新開始
                    print("   正在重新載入頁面...")
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
                    print("   重新填寫表單...")
                    time.sleep(3)
                    
                    # 重新選擇車站和時間
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
                    print(f"   表單重新填寫完成，準備第 {captcha_retry_count + 1} 次驗證碼嘗試...")
                    time.sleep(2)
                
                # 情況 2: 查無可售車次 (需要等待 90 秒後重試)
                elif '去程查無可售車次' in result_source or '選購的車票已售完' in result_source or '查無可預訂' in result_source:
                    print("   ⚠️ 查無可售車次或已售完，將等待 90 秒後重新查詢...")
                    
                    # 90 秒倒數計時 - 每秒顯示
                    for remaining in range(90, 0, -1):
                        print(f"   等待中... 剩餘 {remaining} 秒", end='\r', flush=True)
                        time.sleep(1)
                    
                    print("\n   冷卻時間結束，重新查詢...")
                    
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
                    print("   重新填寫表單...")
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
                    
                    print("   表單重新填寫完成，準備重新識別驗證碼...")
                    # 重置驗證碼計數器，因為這不是驗證碼問題
                    captcha_retry_count = 0
                    monitoring_round += 1
                
                # 情況 3: 查詢成功，有可預訂班次 (檢查是否有錯誤訊息)
                elif 'uk-alert-danger' not in result_source and ('班次' in result_source or 'train' in result_source or '車次' in result_source):
                    # 進一步檢查是否真的有可訂票班次
                    if '訂票' in result_source and '額滿' not in result_source:
                        print("\n" + "="*60)
                        print("🎉 查詢有票！趕快訂購！")
                        print("="*60)
                        break  # 找到票了，結束程式
                    else:
                        print("   ⚠️ 有班次資訊但無可預訂座位，等待 90 秒後重試...")
                        # 按照查無可預訂的邏輯處理
                        for remaining in range(90, 0, -1):
                            print(f"   等待中... 剩餘 {remaining} 秒", end='\r', flush=True)
                            time.sleep(1)
                        print("\n   冷卻時間結束，重新查詢...")
                        captcha_retry_count = 0
                        monitoring_round += 1
                        continue
                
                # 情況 4: 其他未知結果
                else:
                    print("   ⚠️ 查詢結果不明確，保存頁面供分析...")
                    with open('unknown_result.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print("   已保存結果頁面至 unknown_result.html")
                    
                    # 檢查是否有任何錯誤訊息
                    if 'uk-alert-danger' in result_source:
                        print("   發現錯誤訊息，但無法識別具體類型")
                        # 嘗試提取錯誤訊息
                        try:
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(driver.page_source, 'html.parser')
                            error_msgs = soup.select('.feedbackPanelERROR')
                            for msg in error_msgs:
                                print(f"   錯誤訊息: {msg.get_text().strip()}")
                        except:
                            pass
                    
                    break  # 結束監控
                
        except Exception as e:
            print(f"   ❌ 表單填寫過程發生錯誤: {e}")
            print("   但仍保留瀏覽器供檢查...")
        
        print("\n🎯 票券監控完成！")
        print("9. 保留瀏覽器視窗 60 秒供檢查...")
        print("   如果找到票，請立即完成訂票")
        print("   如果需要繼續監控，請重新執行程式")
        time.sleep(60)
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        print("保留瀏覽器 30 秒供檢查錯誤狀態...")
        time.sleep(30)
    finally:
        driver.quit()
        print("=== 測試完成 ===")

if __name__ == "__main__":
    test_anti_detection()