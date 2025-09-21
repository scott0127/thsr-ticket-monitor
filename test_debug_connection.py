import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def test_connection_step_by_step():
    """逐步測試連線並診斷問題"""
    
    print("=== 逐步診斷高鐵網站連線問題 ===")
    
    # 最強化的反偵測設定
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    # 核心反偵測設定
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 安全和隱私設定
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    
    # 視窗和顯示設定
    options.add_argument('--window-size=1366,768')  # 更常見的解析度
    options.add_argument('--start-maximized')
    
    # 更真實的 User-Agent (最新版 Chrome)
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    # 通知和資訊列設定
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    
    # 網路和快取設定
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-field-trial-config')
    
    # 特殊設定
    options.add_argument('--no-first-run')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--disable-default-apps')
    
    # 額外的偽裝設定
    prefs = {
        "profile.default_content_setting_values": {
            "notifications": 2,
            "media_stream": 2,
        },
        "profile.managed_default_content_settings": {
            "images": 1
        },
        "profile.default_content_settings": {
            "popups": 0
        },
        "webrtc.ip_handling_policy": "disable_non_proxied_udp",
        "webrtc.multiple_routes_enabled": False,
        "webrtc.nonproxied_udp_enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--log-level=3')
    
    print("1. 正在啟動 Chrome...")
    driver = webdriver.Chrome(service=service, options=options)
    
    # 更多 JavaScript 偽裝
    stealth_js = """
    // 隱藏 webdriver 屬性
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // 偽造 plugins
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
            {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''},
            {name: 'Native Client', filename: 'internal-nacl-plugin', description: 'Native Client'}
        ]
    });
    
    // 偽造語言設定
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-TW', 'zh', 'en-US', 'en']
    });
    
    // 偽造 Chrome 物件
    window.navigator.chrome = {
        runtime: {},
        loadTimes: function() {
            return {
                commitLoadTime: Date.now() / 1000 - Math.random(),
                finishDocumentLoadTime: Date.now() / 1000 - Math.random(),
                finishLoadTime: Date.now() / 1000 - Math.random(),
                firstPaintAfterLoadTime: 0,
                firstPaintTime: Date.now() / 1000 - Math.random(),
                navigationType: 'Other',
                npnNegotiatedProtocol: 'h2',
                requestTime: Date.now() / 1000 - Math.random(),
                startLoadTime: Date.now() / 1000 - Math.random(),
                connectionInfo: 'h2',
                wasFetchedViaSpdy: true,
                wasNpnNegotiated: true
            };
        },
        csi: function() {
            return {
                startE: Date.now(),
                onloadT: Date.now(),
                pageT: Math.random() * 100,
                tran: 15
            };
        }
    };
    
    // 偽造 permissions
    Object.defineProperty(navigator, 'permissions', {
        get: () => ({
            query: () => Promise.resolve({state: 'granted'})
        })
    });
    
    // 移除 automation 相關痕跡
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    """
    
    driver.execute_script(stealth_js)
    print("2. ✓ 已注入反偵測 JavaScript")
    
    # 先測試一個簡單的網站
    print("3. 測試基本網路連線...")
    try:
        driver.get("https://www.google.com")
        print("   ✓ Google 連線成功")
        time.sleep(2)
    except Exception as e:
        print(f"   ❌ Google 連線失敗: {e}")
        driver.quit()
        return
    
    # 再測試高鐵網站，但使用更長的逾時時間
    print("4. 嘗試連線高鐵網站...")
    driver.set_page_load_timeout(30)  # 設定 30 秒逾時
    
    try:
        start_time = time.time()
        print("   正在載入 https://irs.thsrc.com.tw/IMINT/?locale=tw ...")
        
        driver.get('https://irs.thsrc.com.tw/IMINT/?locale=tw')
        
        load_time = time.time() - start_time
        print(f"   ✓ 頁面載入完成 (耗時 {load_time:.2f} 秒)")
        
        # 立即檢查頁面內容
        print("5. 檢查頁面內容...")
        time.sleep(3)  # 等待 JavaScript 執行
        
        current_url = driver.current_url
        page_title = driver.title
        page_source = driver.page_source
        
        print(f"   當前 URL: {current_url}")
        print(f"   頁面標題: {page_title}")
        print(f"   頁面長度: {len(page_source)} 字元")
        
        # 檢查常見的阻擋訊息
        page_lower = page_source.lower()
        
        blocking_keywords = [
            '請稍後', 'loading', '載入中', 'access denied', 'blocked', 
            'captcha', '驗證', '安全檢查', 'security check', 'robot', '機器人'
        ]
        
        found_blocks = []
        for keyword in blocking_keywords:
            if keyword in page_lower:
                found_blocks.append(keyword)
        
        if found_blocks:
            print(f"   ❌ 發現阻擋關鍵字: {found_blocks}")
            print("   頁面可能被防護系統阻擋")
        else:
            print("   ✓ 沒有發現阻擋關鍵字")
        
        # 檢查是否有表單元素
        print("6. 檢查表單元素...")
        try:
            start_station = driver.find_element(By.NAME, 'selectStartStation')
            print("   ✓ 找到起始站選單")
            
            end_station = driver.find_element(By.NAME, 'selectDestinationStation')
            print("   ✓ 找到終點站選單")
            
            print("   ✓ 表單載入正常，反偵測成功！")
            
        except Exception as e:
            print(f"   ❌ 找不到表單元素: {e}")
            print("   可能被重定向或阻擋")
        
        # 保存頁面截圖和原始碼供檢查
        print("7. 保存診斷資料...")
        try:
            driver.save_screenshot("debug_screenshot.png")
            print("   ✓ 截圖已保存為 debug_screenshot.png")
        except:
            print("   ❌ 截圖保存失敗")
        
        try:
            with open("debug_page_source.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("   ✓ 頁面原始碼已保存為 debug_page_source.html")
        except:
            print("   ❌ 原始碼保存失敗")
        
        # 等待並觀察頁面變化
        print("8. 監控頁面狀態 30 秒...")
        for i in range(6):  # 30秒，每5秒檢查一次
            time.sleep(5)
            try:
                current_source = driver.page_source.lower()
                if '請稍後' in current_source or 'loading' in current_source:
                    print(f"   第 {(i+1)*5} 秒: ⚠️ 出現載入訊息")
                else:
                    print(f"   第 {(i+1)*5} 秒: ✓ 狀態正常")
            except:
                print(f"   第 {(i+1)*5} 秒: ❌ 無法檢查頁面")
                
    except Exception as e:
        print(f"   ❌ 連線失敗: {e}")
        print("   這可能是因為:")
        print("   1. 網站完全阻擋自動化瀏覽器")
        print("   2. 網路連線問題")
        print("   3. 網站暫時維護")
        
    finally:
        print("9. 清理資源...")
        time.sleep(2)
        driver.quit()
        print("=== 診斷完成 ===")

if __name__ == "__main__":
    test_connection_step_by_step()