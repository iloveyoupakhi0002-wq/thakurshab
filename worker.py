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

# Async Telegram sender
async def send_screenshot(image_path, text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
    def _upload():
        with open(image_path, 'rb') as photo:
            requests.post(url, data={'chat_id': CHAT_ID, 'caption': text}, files={'photo': photo})
    await asyncio.to_thread(_upload)

async def process_account(browser, cookie_b64, account_num):
    if not cookie_b64: 
        print(f"⚠️ Account {account_num} ki cookie nahi mili!")
        return
    
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
        
        # 35s Wait for watch time
        print("⏳ Waiting 35 seconds...")
        await asyncio.sleep(35)
        
        current_comment = random.choice(COMMENTS_LIST)
        
        # 1. ⚡ Actions: Follow, Like, Save, Repost
        try:
            # Follow
            await page.evaluate("(() => { let b = document.querySelectorAll('button, div[role=\"button\"]'); for(let x of b) { if(x.innerText === 'Follow') { x.click(); return; } } })();")
            await asyncio.sleep(1)
            
            # Like
            await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Like\"]'); if(s.length>0) s[0].closest('div[role=\"button\"]').click(); })();")
            await asyncio.sleep(1)
            
            # Save
            await page.evaluate("""(() => {
                let svgs = document.querySelectorAll('svg[aria-label="Save"], svg[aria-label="Bookmark"]');
                if (svgs.length > 0) {
                    let btn = svgs[0].closest('div[role="button"], button, a');
                    if (btn) { btn.click(); }
                }
            })();""")
            await asyncio.sleep(1)

            # Repost
            await page.evaluate("""(() => {
                let svgs = document.querySelectorAll('svg[aria-label="Repost"]');
                if (svgs.length > 0) {
                    let btn = svgs[0].closest('div[role="button"], button, a');
                    if (btn) { btn.click(); }
                }
            })();""")
            await asyncio.sleep(1)
            print("✅ Actions (Like, Save, Repost) Done!")
            
        except Exception as e: print("Actions Error:", e)

        # 2. 💬 Commenting Logic (REELS BULLETPROOF FIX)
        try:
            print(f"💬 Trying to comment: {current_comment}")
            
            # Click Comment Icon using robust JS query
            await page.evaluate("""(() => { 
                let svgs = document.querySelectorAll('svg[aria-label="Comment"]'); 
                if(svgs.length > 0) { 
                    let btn = svgs[svgs.length - 1].closest('div[role="button"], span'); 
                    if(btn) btn.click(); 
                } 
            })();""")
            
            print("⏳ Waiting for comment panel to open...")
            await asyncio.sleep(3) 
            
            # Use Playwright's native locator with the EXACT placeholder you provided
            input_box = page.locator('input[placeholder="Add a comment…"]').last
            
            # Ensure it is visible and ready before clicking
            await input_box.wait_for(state="visible", timeout=5000)
            await input_box.click(force=True)
            await asyncio.sleep(1)
            
            # Type slowly and press Enter
            await page.keyboard.type(current_comment, delay=150)
            await asyncio.sleep(1)
            await page.keyboard.press("Enter")
            print("✅ Comment done!")
            
            await asyncio.sleep(2)
            await page.keyboard.press("Escape") 
        except Exception as e: 
            print("❌ Comment Error:", e)

        # 📸 55th Second Screenshot Logic
        elapsed = time.time() - start_time
        wait_for_55 = 55 - elapsed
        if wait_for_55 > 0: await asyncio.sleep(wait_for_55)
            
        screenshot_path = f"proof_{account_num}.png"
        await page.screenshot(path=screenshot_path)
        print("📸 Screenshot taken, sending to Telegram...")
        await send_screenshot(screenshot_path, f"✅ Account {account_num} ka kaam aur 55s ka proof!\n📝 Comment: {current_comment}")

        # Complete 60s
        elapsed = time.time() - start_time
        if 60 - elapsed > 0: await asyncio.sleep(60 - elapsed)
            
    except Exception as e: print("Error:", e)
    finally:
        await context.close()

async def main():
    async with async_playwright() as p:
        # Headless=True rakha hai GitHub Actions ke liye
        browser = await p.chromium.launch(headless=True, args=["--start-maximized"])
        await process_account(browser, C1_B64, 1)
        await process_account(browser, C2_B64, 2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
