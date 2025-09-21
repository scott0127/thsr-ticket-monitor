import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# --- 測試用設定 ---
START_STATION = 'TaiPei'   # 起始站 (台北)
END_STATION = 'ChiaYi'     # 終點站 (嘉義)
SEARCH_DATE = '2025/09/26'  # 查詢日期 (格式：YYYY/MM/DD)
SEARCH_TIME = '18:00'       # 查詢時間 (24小時制，會查詢此時間之後的班次)

def check_thsr_tickets():
    """啟動瀏覽器並檢查高鐵是否有票"""
    
    print("開始初始化 Chrome WebDriver...")
    
    # 設定 Selenium WebDriver - 使用 webdriver-manager 自動管理 ChromeDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # 加入一些穩定性選項
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    # options.add_argument('--headless')  # 在背景執行，不顯示瀏覽器視窗 (可選)
    options.add_argument('--log-level=3') # 減少不必要的日誌輸出
    
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)  # 明確等待元素出現
    
    print("Chrome WebDriver 初始化完成!")

    try:
        print("正在開啟高鐵訂票網站...")
        driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')
        print("網站載入完成!")

        # 等待網頁載入
        print("等待頁面元素載入...")
        time.sleep(10)  # 增加等待時間
        
        # 檢查頁面載入狀態
        print(f"當前頁面標題: {driver.title}")
        print(f"當前頁面 URL: {driver.current_url}")
        
        # 檢查是否有需要點擊的 cookies 同意按鈕等
        try:
            # 可能有 cookies 同意按鈕需要點擊
            cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '同意') or contains(text(), '確定') or contains(text(), 'Accept')]")
            if cookie_buttons:
                print("找到同意按鈕，嘗試點擊...")
                cookie_buttons[0].click()
                time.sleep(2)
        except:
            pass

        print("開始填寫表單...")
        
        # 使用明確等待來等待元素出現
        try:
            print("等待起始站選單載入...")
            start_select_element = wait.until(EC.presence_of_element_located((By.ID, 'select_location01')))
            print("起始站選單已載入!")
        except:
            print("無法找到起始站選單，嘗試查看頁面內容...")
            # 列印頁面部分內容以便除錯
            page_source = driver.page_source
            print("頁面部分內容:")
            print(page_source[:2000])
            
            # 嘗試尋找其他可能的選擇器
            select_elements = driver.find_elements(By.TAG_NAME, 'select')
            print(f"找到 {len(select_elements)} 個下拉選單")
            for i, select in enumerate(select_elements):
                select_id = select.get_attribute('id')
                select_name = select.get_attribute('name')
                print(f"下拉選單 {i+1}: id='{select_id}', name='{select_name}'")
            
            raise Exception("找不到起始站選單")
        
        # 填寫起始站
        print(f"選擇起始站: {START_STATION}")
        start_select = Select(start_select_element)
        start_select.select_by_value(START_STATION)
        start_select.select_by_value(START_STATION)
        
        # 填寫終點站
        print(f"選擇終點站: {END_STATION}")
        end_select = Select(driver.find_element(By.ID, 'select_location02'))
        end_select.select_by_value(END_STATION)
        
        # 填寫日期
        print(f"設定查詢日期: {SEARCH_DATE}")
        driver.execute_script(f"document.getElementById('toTimeInputField').value = '{SEARCH_DATE}'")
        
        # 填寫時間
        print(f"設定查詢時間: {SEARCH_TIME}")
        time_select = Select(driver.find_element(By.ID, 'toTimeTable'))
        time_select.select_by_value(SEARCH_TIME)

        print(f"查詢設定完成：{SEARCH_DATE} {SEARCH_TIME} 從 {START_STATION} 到 {END_STATION}")
        
        # 點擊查詢按鈕
        print("點擊查詢按鈕...")
        query_button = driver.find_element(By.ID, 'QUERY')
        query_button.click()

        # 等待查詢結果載入
        print("等待查詢結果載入...")
        time.sleep(8)

        print("開始分析查詢結果...")
        # 分析結果頁面
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 列印頁面標題確認我們在正確的頁面
        page_title = driver.title
        print(f"當前頁面標題: {page_title}")
        
        train_rows = soup.select('tr.trip-column')
        print(f"找到 {len(train_rows)} 個班次列")
        
        if not train_rows:
            print("無法找到任何班次資訊，可能頁面結構已變更或查詢無結果。")
            # 列印部分頁面原始碼以便除錯
            print("頁面部分內容:")
            print(driver.page_source[:1000])
            return False, []

        found_ticket = False
        available_trains = []

        for i, row in enumerate(train_rows):
            print(f"檢查第 {i+1} 個班次...")
            button_cell = row.select_one('td.book-seat-content')
            if button_cell:
                button = button_cell.select_one('button.btn-primary:not([disabled])')
                if button:
                    found_ticket = True
                    train_id_element = row.select_one('td:nth-of-type(1) span.train-code')
                    departure_time_element = row.select_one('td:nth-of-type(2) span.font-16px')
                    arrival_time_element = row.select_one('td:nth-of-type(3) span.font-16px')
                    
                    if train_id_element and departure_time_element and arrival_time_element:
                        train_id = train_id_element.text.strip()
                        departure_time = departure_time_element.text.strip()
                        arrival_time = arrival_time_element.text.strip()
                        available_trains.append(f"車次 {train_id} ({departure_time} - {arrival_time})")
                        print(f"找到可訂票班次: 車次 {train_id} ({departure_time} - {arrival_time})")
                else:
                    print(f"第 {i+1} 個班次目前無票")
            else:
                print(f"第 {i+1} 個班次無法找到訂票按鈕區域")
        
        return found_ticket, available_trains

    except Exception as e:
        print(f"查詢過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False, []
    finally:
        print("關閉瀏覽器...")
        driver.quit()

if __name__ == "__main__":
    print("=== 高鐵票券檢查測試開始 ===")
    
    is_ticket_available, trains = check_thsr_tickets()
    
    print("\n=== 測試結果 ===")
    if is_ticket_available:
        print("✓ 偵測到有票!")
        print("可訂票車次：")
        for train in trains:
            print(f"- {train}")
    else:
        print("✗ 目前無票或檢查失敗")
    
    print("=== 測試完成 ===")