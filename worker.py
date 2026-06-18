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
        viewport={'width': 1920, 'height': 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
        await asyncio.sleep(4)
        
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        start_time = time.time()
        
        # 35s Wait
        await asyncio.sleep(35)
        
        # 1. Follow, Like, Save (Actions)
        current_comment = random.choice(COMMENTS_LIST)
        try:
            # Follow
            await page.evaluate("(() => { let b = document.querySelectorAll('button, div[role=\"button\"]'); for(let x of b) { if(x.innerText === 'Follow') { x.click(); return; } } })();")
            await asyncio.sleep(1)
            # Like
            await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Like\"]'); if(s.length>0) s[0].closest('div[role=\"button\"]').click(); })();")
            await asyncio.sleep(1)
            # 🔖 Save (नया फिक्स: शेयर के नीचे वाला बटन)
            await page.evaluate("""(() => {
                let btns = document.querySelectorAll('button, div[role="button"]');
                for (let b of btns) {
                    if (b.querySelector('svg[aria-label="Save"]')) {
                        b.click();
                        return;
                    }
                }
            })();""")
            await asyncio.sleep(1)
        except Exception as e: print("Actions Error:", e)

        # 2. Commenting Logic
        try:
            await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Comment\"]'); if(s.length>0) s[0].closest('div[role=\"button\"]').click(); })();")
            await asyncio.sleep(2)
            input_box = page.locator('input[placeholder="Add a comment…"]').last
            if not await input_box.is_visible(): input_box = page.locator('input.xjbqb8w').last
            await input_box.hover()
            await input_box.click(force=True)
            await asyncio.sleep(1)
            await page.keyboard.type(current_comment, delay=100)
            await page.keyboard.press("Enter")
            await asyncio.sleep(2)
            await page.keyboard.press("Escape")
        except Exception as e: print("Comment Error:", e)

        # 📸 55th Second Screenshot Logic
        elapsed = time.time() - start_time
        wait_for_55 = 55 - elapsed
        if wait_for_55 > 0: await asyncio.sleep(wait_for_55)
            
        screenshot_path = f"proof_{account_num}.png"
        await page.screenshot(path=screenshot_path)
        send_screenshot(screenshot_path, f"✅ Account {account_num} ka kaam aur 55s ka proof!\n📝 Comment: {current_comment}")

        # Complete 60s
        elapsed = time.time() - start_time
        if 60 - elapsed > 0: await asyncio.sleep(60 - elapsed)
            
    except Exception as e: print("Error:", e)
    await context.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--start-maximized"])
        await process_account(browser, C1_B64, 1)
        await process_account(browser, C2_B64, 2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
