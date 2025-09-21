import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def human_like_delay(min_seconds=1, max_seconds=3):
    """模擬人類操作的隨機延遲"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def test_blocking_detection():
    """專門測試網站阻擋偵測"""
    
    print("=== 測試高鐵網站阻擋偵測 ===")
    
    # 最強反偵測設定
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    # 核心反偵測設定
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 安全設定
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    
    # 視窗設定
    options.add_argument('--window-size=1366,768')
    options.add_argument('--start-maximized')
    
    # 真實的 User-Agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    # 通知設定
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    
    # 背景處理設定
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    
    # 額外偽裝
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
    
    print("1. 啟動 Chrome...")
    driver = webdriver.Chrome(service=service, options=options)
    
    # 強化 JavaScript 偽裝
    stealth_js = """
    // 隱藏 webdriver
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // 偽造 plugins
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
            {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
            {name: 'Native Client', filename: 'internal-nacl-plugin'}
        ]
    });
    
    // 偽造語言
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-TW', 'zh', 'en-US', 'en']
    });
    
    // 偽造 Chrome 物件
    window.navigator.chrome = {
        runtime: {},
        loadTimes: function() { return {}; },
        csi: function() { return {}; }
    };
    
    // 偽造 permissions
    Object.defineProperty(navigator, 'permissions', {
        get: () => ({
            query: () => Promise.resolve({state: 'granted'})
        })
    });
    
    // 移除自動化標記
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    """
    
    driver.execute_script(stealth_js)
    print("2. ✓ 反偵測 JavaScript 已注入")
    
    # 設定逾時
    driver.set_page_load_timeout(30)
    
    try:
        print("3. 嘗試載入高鐵網站...")
        start_time = time.time()
        
        driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')
        
        load_time = time.time() - start_time
        print(f"   ✓ 頁面載入完成 (耗時 {load_time:.2f} 秒)")
        
        # 立即檢查阻擋狀態
        print("4. 檢查阻擋狀態...")
        
        for check_round in range(5):  # 檢查 5 次，每次間隔 3 秒
            human_like_delay(2, 4)
            
            current_url = driver.current_url
            page_title = driver.title
            page_source = driver.page_source
            
            print(f"   第 {check_round + 1} 次檢查:")
            print(f"   - URL: {current_url}")
            print(f"   - 標題: {page_title}")
            print(f"   - 頁面長度: {len(page_source)} 字元")
            
            # 檢查各種阻擋關鍵字
            page_lower = page_source.lower()
            blocking_keywords = [
                '請稍候', '請稍后', 'loading', '載入中', 
                'access denied', 'blocked', 'captcha', 
                '驗證', '安全檢查', 'security check', 
                'robot', '機器人', '系統忙碌中'
            ]
            
            found_blocks = []
            for keyword in blocking_keywords:
                if keyword in page_lower:
                    found_blocks.append(keyword)
            
            if found_blocks:
                print(f"   ❌ 發現阻擋關鍵字: {found_blocks}")
                
                # 如果是「請稍候」，等待更久再檢查
                if '請稍候' in found_blocks or '請稍后' in found_blocks:
                    print(f"   ⏳ 偵測到「請稍候」，等待 10 秒...")
                    time.sleep(10)
                    continue
                    
            else:
                print("   ✓ 沒有發現阻擋關鍵字")
                
                # 檢查表單是否存在
                try:
                    start_station = driver.find_element(By.NAME, 'selectStartStation')
                    print("   ✓ 表單載入成功！")
                    print("   🎉 成功繞過反自動化偵測！")
                    
                    # 保存成功的截圖
                    driver.save_screenshot("success_screenshot.png")
                    print("   ✓ 成功截圖已保存")
                    
                    break  # 成功，跳出檢查迴圈
                    
                except:
                    print("   ⚠️ 頁面載入但找不到表單")
        
        else:
            print("   ❌ 所有檢查都發現阻擋或問題")
            
        # 最終狀態報告
        print("5. 最終狀態報告...")
        final_source = driver.page_source.lower()
        
        if '請稍候' in final_source:
            print("   ❌ 最終狀態：仍被「請稍候」阻擋")
            print("   建議方案：")
            print("   1. 使用不同的 IP 位址 (VPN/代理)")
            print("   2. 降低訪問頻率")
            print("   3. 模擬更真實的使用者行為")
            print("   4. 嘗試不同時間訪問")
        elif 'selectStartStation' in final_source:
            print("   ✅ 最終狀態：成功載入表單")
        else:
            print("   ⚠️ 最終狀態：未知狀態")
        
        # 保存診斷檔案
        with open("blocking_test_result.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("   ✓ 診斷結果已保存至 blocking_test_result.html")
        
        print("6. 保持瀏覽器開啟 30 秒供手動檢查...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")
        
    finally:
        driver.quit()
        print("=== 測試完成 ===")

if __name__ == "__main__":
    test_blocking_detection()