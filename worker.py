import asyncio
from playwright.async_api import async_playwright
import os
import base64
import json
import time
import random
import requests

TARGET_URL = os.environ.get("TARGET_URL")
CHAT_ID = os.environ.get("CHAT_ID")
TG_TOKEN = os.environ.get("TG_TOKEN") 
C1_B64 = os.environ.get("COOKIE_1")
C2_B64 = os.environ.get("COOKIE_2")

COMMENTS_LIST = ["🔥 Ek number bhai!", "Bhai kya baat hai! 😍", "Superb video bro 🚀", "Gajab editing 👏"]

def send_screenshot(image_path, text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
    with open(image_path, 'rb') as photo:
        requests.post(url, data={'chat_id': CHAT_ID, 'caption': text}, files={'photo': photo})

async def process_account(browser, cookie_b64, account_num):
    if not cookie_b64: return
    
    print(f"🟢 Starting Account {account_num}...")
    cookie_str = base64.b64decode(cookie_b64).decode()
    cookies = json.loads(cookie_str)
    
    context = await browser.new_context(
        viewport={'width': 1080, 'height': 1920}, # मोबाइल जैसा व्यू ताकि बटन पास-पास दिखें
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    )
    
    cleaned_cookies = []
    for c in cookies:
        if 'sameSite' in c and c['sameSite'] not in ['Strict', 'Lax', 'None']: c['sameSite'] = 'Lax'
        if 'id' in c: del c['id']
        cleaned_cookies.append(c)
        
    await context.add_cookies(cleaned_cookies)
    page = await context.new_page()

    try:
        await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        await asyncio.sleep(5)
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        start_time = time.time()
        await asyncio.sleep(35) # 35s watch time
        
        # --- ACTIONS ---
        current_comment = random.choice(COMMENTS_LIST)
        
        # 1. Follow & Like
        await page.evaluate("(() => { document.querySelectorAll('button').forEach(b => { if(b.innerText.includes('Follow')) b.click(); }); })();")
        await page.evaluate("(() => { document.querySelectorAll('svg[aria-label=\"Like\"]').forEach(s => s.closest('div[role=\"button\"]').click()); })();")
        
        # 2. 🔖 SAVE (एकदम नया और पक्का तरीका)
        await page.evaluate("""(() => {
            let svgs = document.querySelectorAll('svg');
            for (let s of svgs) {
                if (s.getAttribute('aria-label') === 'Save') {
                    s.closest('div[role="button"]').click();
                    break;
                }
            }
        })();""")
        await asyncio.sleep(1)

        # 3. Commenting
        await page.evaluate("(() => { document.querySelectorAll('svg[aria-label=\"Comment\"]').forEach(s => s.closest('div[role=\"button\"]').click()); })();")
        await asyncio.sleep(2)
        
        # Tab press ताकि बॉक्स सेलेक्ट हो जाए
        await page.keyboard.press("Tab") 
        await page.keyboard.type(current_comment, delay=100)
        await page.keyboard.press("Enter")
        await asyncio.sleep(2)

        # Proof Screenshot
        elapsed = time.time() - start_time
        if elapsed < 55: await asyncio.sleep(55 - elapsed)
            
        screenshot_path = f"proof_{account_num}.png"
        await page.screenshot(path=screenshot_path)
        send_screenshot(screenshot_path, f"✅ Account {account_num} (Like/Save/Comment Done!)")

        # 60s Finish
        if time.time() - start_time < 60: await asyncio.sleep(60 - (time.time() - start_time))
            
    except Exception as e: print("Error:", e)
    await context.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        await process_account(browser, C1_B64, 1)
        await process_account(browser, C2_B64, 2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
