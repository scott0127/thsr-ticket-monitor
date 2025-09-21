import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

def human_like_delay(min_seconds=1, max_seconds=3):
    """模擬人類操作的隨機延遲"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def test_enhanced_anti_detection():
    """測試強化的反偵測設定"""
    
    print("=== 測試強化反偵測設定 ===")
    
    # 強化反偵測的 Chrome 設定
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
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    
    # 設定 prefs
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
    
    # 執行多個 JavaScript 隱藏自動化痕跡
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['zh-TW', 'zh', 'en']})")
    driver.execute_script("window.navigator.chrome = {runtime: {}}")
    driver.execute_script("Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})})")
    
    wait = WebDriverWait(driver, 20)

    try:
        print("1. 正在開啟高鐵訂票網站...")
        driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')
        human_like_delay(3, 6)
        
        print("2. 檢查網頁標題...")
        print(f"   頁面標題: {driver.title}")
        
        if "高鐵" in driver.title:
            print("   ✓ 成功載入高鐵網站！")
        else:
            print("   ❌ 可能被偵測或載入失敗")
        
        print("3. 檢查頁面內容...")
        page_source = driver.page_source.lower()
        
        if '請稍後' in page_source or 'loading' in page_source or '載入中' in page_source:
            print("   ❌ 頁面顯示「請稍後」- 仍被偵測為自動化")
            print("   建議：")
            print("   - 嘗試使用不同的 User-Agent")
            print("   - 考慮使用代理伺服器")
            print("   - 增加更長的隨機延遲")
        elif 'access denied' in page_source or 'blocked' in page_source:
            print("   ❌ 存取被拒絕")
        else:
            print("   ✓ 頁面內容正常，沒有「請稍後」訊息")
            
            print("4. 檢查 Cookie 同意頁面...")
            try:
                agree_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我同意')]")))
                print("   ✓ 發現 Cookie 同意頁面")
                
                # 模擬人類點擊行為
                actions = ActionChains(driver)
                actions.move_to_element(agree_button)
                human_like_delay(1, 2)
                actions.click(agree_button)
                actions.perform()
                print("   ✓ 已點擊同意（使用人類行為模擬）")
                
                human_like_delay(3, 5)
                
            except:
                print("   沒有 Cookie 同意頁面")
            
            print("5. 檢查表單載入...")
            try:
                start_station = wait.until(EC.presence_of_element_located((By.NAME, 'selectStartStation')))
                print("   ✓ 表單載入成功！")
                print("   ✓ 反偵測設定有效！")
                
                # 再次檢查是否突然出現「請稍後」
                updated_source = driver.page_source.lower()
                if '請稍後' in updated_source:
                    print("   ⚠️  表單載入後出現「請稍後」")
                else:
                    print("   ✓ 表單狀態穩定，可以繼續操作")
                    
            except Exception as e:
                print(f"   ❌ 表單載入失敗: {e}")
        
        print("6. 保留瀏覽器視窗 60 秒供詳細檢查...")
        print("   請仔細檢查瀏覽器中的頁面狀態")
        print("   注意是否有「請稍後」、載入動畫或其他異常")
        
        for i in range(12):  # 60秒，每5秒檢查一次
            time.sleep(5)
            current_source = driver.page_source.lower()
            if '請稍後' in current_source:
                print(f"   ⚠️  第 {(i+1)*5} 秒：出現「請稍後」")
            else:
                print(f"   ✓ 第 {(i+1)*5} 秒：狀態正常")
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
    finally:
        driver.quit()
        print("=== 測試完成 ===")

if __name__ == "__main__":
    test_enhanced_anti_detection()