import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 測試設定 - 使用正確的站點數字
START_STATION = '2'         # 起始站 (台北)
END_STATION = '10'          # 終點站 (嘉義)
SEARCH_DATE = '2025/09/26'  # 查詢日期 (格式：YYYY/MM/DD)
SEARCH_TIME = '600P'        # 查詢時間 (網站格式：600P = 18:00)

def test_form_filling():
    """測試表單填寫功能"""
    
    # 設定 Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--log-level=3')
    
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    try:
        print("正在開啟高鐵訂票網站...")
        driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')

        # 等待網頁載入
        time.sleep(3)
        print(f"當前頁面標題: {driver.title}")

        # 處理 Cookie 同意頁面
        try:
            print("檢查是否有 Cookie 同意頁面...")
            agree_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我同意')]")))
            print("發現 Cookie 同意頁面，正在點擊「我同意」...")
            agree_button.click()
            time.sleep(3)
            print("已點擊同意按鈕")
        except Exception as e:
            print(f"沒有發現 Cookie 同意頁面: {e}")

        # 等待表單載入
        print("等待表單載入...")
        time.sleep(3)

        # 填寫表單
        try:
            # 選擇起始站
            print("尋找起始站選擇器...")
            start_station_select = wait.until(EC.element_to_be_clickable((By.NAME, 'selectStartStation')))
            print("找到起始站選擇器，正在選擇...")
            Select(start_station_select).select_by_value(START_STATION)
            print(f"✓ 已選擇起始站: 台北 (值: {START_STATION})")
            
            # 選擇終點站
            print("尋找終點站選擇器...")
            end_station_select = driver.find_element(By.NAME, 'selectDestinationStation')
            print("找到終點站選擇器，正在選擇...")
            Select(end_station_select).select_by_value(END_STATION)
            print(f"✓ 已選擇終點站: 嘉義 (值: {END_STATION})")
            
            # 設定日期
            print("設定日期...")
            driver.execute_script(f"document.getElementById('toTimeInputField').value = '{SEARCH_DATE}'")
            print(f"✓ 已設定日期: {SEARCH_DATE}")
            
            # 選擇時間
            print("尋找時間選擇器...")
            time_select = driver.find_element(By.NAME, 'toTimeTable')
            print("找到時間選擇器，正在選擇...")
            Select(time_select).select_by_value(SEARCH_TIME)
            print(f"✓ 已選擇時間: 18:00 (值: {SEARCH_TIME})")

            print(f"\n表單填寫完成！")
            print(f"查詢設定：{SEARCH_DATE} 18:00 從台北到嘉義")
            
            # 檢查驗證碼
            try:
                captcha_input = driver.find_element(By.ID, 'securityCode')
                print("發現驗證碼欄位")
                print("請在瀏覽器中手動輸入驗證碼...")
                print("輸入完成後按 Enter 繼續...")
                input()
                
                # 點擊查詢按鈕
                submit_button = driver.find_element(By.ID, 'SubmitButton')
                print("正在點擊查詢按鈕...")
                submit_button.click()
                print("✓ 已點擊查詢按鈕")
                
                # 等待查詢結果
                print("等待查詢結果載入...")
                time.sleep(8)
                
                # 檢查結果
                print("檢查查詢結果...")
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # 嘗試不同的班次選擇器
                selectors_to_try = [
                    'tr.trip-column',
                    '.trip-column',
                    'tr[class*="trip"]',
                    'table tr',
                    '.train-info'
                ]
                
                train_rows = []
                for selector in selectors_to_try:
                    train_rows = soup.select(selector)
                    if train_rows:
                        print(f"使用選擇器 '{selector}' 找到 {len(train_rows)} 個元素")
                        break
                
                if train_rows:
                    print(f"✓ 查詢成功！找到 {len(train_rows)} 個結果")
                    
                    # 分析前幾個結果
                    for i, row in enumerate(train_rows[:5]):
                        print(f"結果 {i+1}: {row.get_text()[:100]}...")
                else:
                    print("❌ 沒有找到班次資訊")
                    print("儲存網頁原始碼以供除錯...")
                    with open('debug_result.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print("已儲存到 debug_result.html")
                
            except Exception as e:
                print(f"處理驗證碼或查詢時發生錯誤: {e}")

        except Exception as e:
            print(f"表單填寫過程中發生錯誤: {e}")
            print("目前網頁原始碼:")
            with open('debug_form.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("已儲存到 debug_form.html")

        print("測試完成，瀏覽器將在 10 秒後關閉...")
        time.sleep(10)

    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_form_filling()