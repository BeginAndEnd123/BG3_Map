from playwright.sync_api import sync_playwright
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.dirname(os.path.abspath(__file__))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    # Login page screenshot
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto('http://localhost:5173/login')
    page.wait_for_load_state('networkidle')
    page.screenshot(path=os.path.join(OUT, 'redesign_login.png'))
    print("Saved redesign_login.png")

    # Login
    page.fill('input[placeholder*="用户名"]', 'admin')
    page.fill('input[placeholder*="密码"]', 'admin123')
    page.click('button[type="submit"]')
    page.wait_for_url('**/')
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(3000)

    # Homepage screenshot
    page.screenshot(path=os.path.join(OUT, 'redesign_home.png'))
    print("Saved redesign_home.png")

    # 404 page
    page.goto('http://localhost:5173/nonexistent')
    page.wait_for_load_state('networkidle')
    page.screenshot(path=os.path.join(OUT, 'redesign_404.png'))
    print("Saved redesign_404.png")

    browser.close()
    print("\nDone!")
