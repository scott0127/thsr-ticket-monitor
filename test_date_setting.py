import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# 測試設定
START_STATION = '2'         # 起始站 (台北)
END_STATION = '10'          # 終點站 (嘉義)
SEARCH_DATE = '2025/09/26'  # 查詢日期
SEARCH_TIME = '600P'        # 查詢時間

def test_date_setting():
    """專門測試日期設定功能"""
    
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
        time.sleep(3)

        # 處理 Cookie 同意
        try:
            agree_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我同意')]")))
            agree_button.click()
            time.sleep(3)
            print("✓ 已點擊同意")
        except:
            print("沒有 Cookie 同意頁面")

        # 先填寫起始站和終點站
        print("填寫起始站和終點站...")
        start_station = wait.until(EC.element_to_be_clickable((By.NAME, 'selectStartStation')))
        Select(start_station).select_by_value(START_STATION)
        
        end_station = driver.find_element(By.NAME, 'selectDestinationStation')
        Select(end_station).select_by_value(END_STATION)
        print("✓ 已選擇車站")

        # 測試日期設定的不同方法
        print("開始測試日期設定...")
        
        # 檢查目前日期值
        current_date = driver.execute_script("return document.getElementById('toTimeInputField').value")
        print(f"目前日期值: {current_date}")
        
        # 方法1: 直接設定隱藏欄位
        print("方法1: 設定隱藏的日期欄位...")
        driver.execute_script(f"document.getElementById('toTimeInputField').value = '{SEARCH_DATE}'")
        new_date = driver.execute_script("return document.getElementById('toTimeInputField').value")
        print(f"設定後日期值: {new_date}")
        
        # 方法2: 點擊可見的日期欄位並輸入
        print("方法2: 點擊可見的日期欄位...")
        try:
            # 找到可見的日期輸入欄位
            visible_date_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"][readonly]')
            for i, input_field in enumerate(visible_date_inputs):
                if input_field.is_displayed():
                    print(f"找到可見的日期欄位 {i+1}")
                    # 點擊欄位
                    input_field.click()
                    time.sleep(1)
                    
                    # 嘗試清除並輸入新日期
                    driver.execute_script("arguments[0].removeAttribute('readonly')", input_field)
                    input_field.clear()
                    input_field.send_keys(SEARCH_DATE)
                    input_field.send_keys(Keys.TAB)  # 失去焦點觸發事件
                    break
        except Exception as e:
            print(f"方法2失敗: {e}")
        
        # 方法3: 使用 flatpickr API (如果存在)
        print("方法3: 嘗試使用 flatpickr API...")
        try:
            driver.execute_script(f"""
                var dateInput = document.getElementById('toTimeInputField');
                if (dateInput._flatpickr) {{
                    dateInput._flatpickr.setDate('{SEARCH_DATE}');
                }} else {{
                    // 手動觸發事件
                    dateInput.value = '{SEARCH_DATE}';
                    var event = new Event('change', {{ bubbles: true }});
                    dateInput.dispatchEvent(event);
                }}
            """)
        except Exception as e:
            print(f"方法3失敗: {e}")
        
        # 檢查最終結果
        final_date = driver.execute_script("return document.getElementById('toTimeInputField').value")
        print(f"最終日期值: {final_date}")
        
        # 檢查可見欄位的值
        try:
            visible_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
            for i, inp in enumerate(visible_inputs):
                if inp.is_displayed() and 'date' in inp.get_attribute('class').lower():
                    print(f"可見日期欄位 {i+1} 的值: {inp.get_attribute('value')}")
        except:
            pass
        
        # 繼續填寫時間
        print("設定時間...")
        time_select = driver.find_element(By.NAME, 'toTimeTable')
        Select(time_select).select_by_value(SEARCH_TIME)
        print("✓ 已設定時間")
        
        print("請檢查瀏覽器中的表單是否正確填寫")
        print("按 Enter 繼續...")
        input()

    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("測試完成，瀏覽器將在 5 秒後關閉...")
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    test_date_setting()