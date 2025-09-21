import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 測試設定
START_STATION = 'TaiPei'   # 起始站 (台北)
END_STATION = 'ChiaYi'     # 終點站 (嘉義)
SEARCH_DATE = '2025/09/26'  # 查詢日期 (格式：YYYY/MM/DD)
SEARCH_TIME = '18:00'       # 查詢時間 (24小時制，會查詢此時間之後的班次)

def test_thsr_with_cookie():
    """測試高鐵查詢流程，包括處理 Cookie 同意頁面"""
    
    # 設定 Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--log-level=3')
    
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)  # 增加等待時間

    try:
        print("正在開啟高鐵訂票網站...")
        driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')

        # 等待網頁載入
        time.sleep(3)
        print(f"當前頁面標題: {driver.title}")

        # 處理 Cookie 同意頁面
        try:
            print("檢查是否有 Cookie 同意頁面...")
            # 尋找並點擊「我同意」按鈕
            agree_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我同意')]")))
            print("發現 Cookie 同意頁面，正在點擊「我同意」...")
            agree_button.click()
            time.sleep(3)  # 等待頁面跳轉
            print(f"點擊後頁面標題: {driver.title}")
        except Exception as e:
            print(f"沒有發現 Cookie 同意頁面，或已經同意過了: {e}")

        # 等待查詢表單載入
        print("等待查詢表單載入...")
        time.sleep(3)

        # 檢查表單元素是否存在
        try:
            start_select = wait.until(EC.presence_of_element_located((By.ID, 'select_location01')))
            print("找到起始站選擇器")
            
            end_select = driver.find_element(By.ID, 'select_location02')
            print("找到終點站選擇器")
            
            date_input = driver.find_element(By.ID, 'toTimeInputField')
            print("找到日期輸入欄位")
            
            time_select = driver.find_element(By.ID, 'toTimeTable')
            print("找到時間選擇器")
            
            # 填寫表單
            print("正在填寫表單...")
            Select(start_select).select_by_value(START_STATION)
            print(f"已選擇起始站: {START_STATION}")
            
            Select(end_select).select_by_value(END_STATION)
            print(f"已選擇終點站: {END_STATION}")
            
            driver.execute_script(f"document.getElementById('toTimeInputField').value = '{SEARCH_DATE}'")
            print(f"已設定日期: {SEARCH_DATE}")
            
            Select(time_select).select_by_value(SEARCH_TIME)
            print(f"已設定時間: {SEARCH_TIME}")

            # 點擊查詢按鈕
            query_button = driver.find_element(By.ID, 'QUERY')
            print("正在點擊查詢按鈕...")
            query_button.click()

            # 等待查詢結果載入
            print("等待查詢結果載入...")
            time.sleep(8)

            # 檢查是否有結果
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            train_rows = soup.select('tr.trip-column')
            
            print(f"找到 {len(train_rows)} 個班次")
            
            if train_rows:
                print("查詢成功！找到班次資訊")
                for i, row in enumerate(train_rows[:3]):  # 只顯示前3個班次
                    try:
                        train_id = row.select_one('td:nth-of-type(1) span.train-code')
                        departure = row.select_one('td:nth-of-type(2) span.font-16px')
                        arrival = row.select_one('td:nth-of-type(3) span.font-16px')
                        
                        if train_id and departure and arrival:
                            print(f"班次 {i+1}: {train_id.text.strip()} ({departure.text.strip()} - {arrival.text.strip()})")
                        
                        # 檢查是否可訂票
                        button_cell = row.select_one('td.book-seat-content')
                        if button_cell:
                            button = button_cell.select_one('button.btn-primary:not([disabled])')
                            if button:
                                print("  *** 此班次可訂票！***")
                            else:
                                print("  (此班次目前無票)")
                    except Exception as e:
                        print(f"  解析班次資訊時發生錯誤: {e}")
            else:
                print("沒有找到班次資訊，可能需要調整選擇器")
                # 儲存網頁原始碼以供除錯
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("已將網頁原始碼儲存到 debug_page.html")

        except Exception as e:
            print(f"表單操作時發生錯誤: {e}")

        print("測試完成，瀏覽器將在 5 秒後關閉...")
        time.sleep(5)

    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_thsr_with_cookie()