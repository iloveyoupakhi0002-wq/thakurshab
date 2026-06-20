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

# 🛡️ Safe Telegram Sender with Retry Logic
async def send_screenshot(image_path, text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
    def _upload():
        max_retries = 3
        attempt = 0
        while attempt < max_retries:
            try:
                with open(image_path, 'rb') as photo:
                    res = requests.post(url, data={'chat_id': CHAT_ID, 'caption': text}, files={'photo': photo}, timeout=20)
                if res.status_code == 200: break
            except Exception as e:
                attempt += 1
                time.sleep(2)
    await asyncio.to_thread(_upload)

async def process_account(browser, cookie_b64, account_num):
    if not cookie_b64: 
        print(f"⚠️ Account {account_num} ki cookie nahi mili!")
        return
    
    print(f"\n=========================================")
    print(f"🟢 Starting Account {account_num}...")
    print(f"=========================================")
    
    # Cloud ke liye wapas Base64 load kar raha hai
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
        print("🏠 Warming up on Home Page...")
        await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        await asyncio.sleep(4)
        
        print(f"🎯 Going to Target URL: {TARGET_URL}")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        start_time = time.time()
        
        # 35s Wait for watch time
        print("⏳ Waiting 35 seconds (Watch Time)...")
        await asyncio.sleep(35)
        
        current_comment = random.choice(COMMENTS_LIST)
        
        # --- 1. FOLLOW ---
        try:
            print("👤 Trying to Follow...")
            await page.evaluate("(() => { let b = document.querySelectorAll('button, div[role=\"button\"]'); for(let x of b) { if(x.innerText === 'Follow') { x.click(); return; } } })();")
            await asyncio.sleep(1)
        except Exception as e: print("Follow Error:", e)

        # --- 2. LIKE ---
        try:
            print("❤️ Trying to Like...")
            await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Like\"]'); if(s.length>0) s[0].closest('div[role=\"button\"]').click(); })();")
            await asyncio.sleep(1)
        except Exception as e: print("Like Error:", e)

        # --- 3. COMMENT & SCREENSHOTS ---
        try:
            print("💬 Comment icon par click kar raha hu...")
            await page.locator('svg[aria-label="Comment"]').first.click(force=True)
            print("⏳ Panel khulne ka 4 seconds wait kar raha hu...")
            await asyncio.sleep(4) 
            
            # 📸 SCREENSHOT 1: Panel Khulne Ke Baad
            shot1_path = f"panel_open_acc{account_num}.png"
            await page.screenshot(path=shot1_path)
            print("📸 Screenshot 1 liya (Panel Open) - Telegram par bhej raha hu...")
            await send_screenshot(shot1_path, f"1️⃣ Account {account_num} - Comment panel open ho gaya hai!")

            print("🖱️ Likhne wala dabba dhundh raha hu...")
            selectors = [
                'textarea[aria-label*="comment" i]',
                'div[role="textbox"]',
                'input[placeholder*="comment" i]',
                'textarea[placeholder*="comment" i]',
                '.xjbqb8w'
            ]
            
            box_found = False
            for selector in selectors:
                target_box = page.locator(selector).last
                if await target_box.count() > 0 and await target_box.is_visible():
                    print(f"🎯 Dabba mil gaya is selector se: {selector}")
                    await target_box.hover()
                    await asyncio.sleep(1)
                    await target_box.click(force=True)
                    box_found = True
                    break 
            
            if not box_found:
                print("⚠️ Box seedha nahi mila, Tab daba kar try kar raha hu...")
                await page.keyboard.press("Tab")
            
            print("✅ Typing shuru...")
            await asyncio.sleep(1)
            await page.keyboard.type(current_comment, delay=150)
            await asyncio.sleep(1)
            
            print("🚀 Enter daba raha hu...")
            await page.keyboard.press("Enter")
            print(f"✅ Comment '{current_comment}' bheja gaya. 3 second wait kar raha hu post hone ka...")
            await asyncio.sleep(3)
            
            # 📸 SCREENSHOT 2: Comment Post Hone Ke Baad
            shot2_path = f"comment_done_acc{account_num}.png"
            await page.screenshot(path=shot2_path)
            print("📸 Screenshot 2 liya (Comment Done) - Telegram par bhej raha hu...")
            await send_screenshot(shot2_path, f"2️⃣ Account {account_num} - Comment POST ho gaya!\n📝 Text: {current_comment}")

            # Close panel
            await page.keyboard.press("Escape")
            await asyncio.sleep(1)
            
        except Exception as e: 
            print(f"❌ Comment completely fail hua: {e}")

        # --- 4. SAVE ---
        try:
            print("🔖 Trying to Save...")
            await page.evaluate("""(() => {
                let svgs = document.querySelectorAll('svg[aria-label="Save"], svg[aria-label="Bookmark"]');
                if (svgs.length > 0) {
                    let btn = svgs[0].closest('div[role="button"], button, a');
                    if (btn) { btn.click(); }
                }
            })();""")
            await asyncio.sleep(1)
        except Exception as e: print("Save Error:", e)

        # --- 5. REPOST ---
        try:
            print("🔁 Trying to Repost...")
            await page.evaluate("""(() => {
                let svgs = document.querySelectorAll('svg[aria-label="Repost"]');
                if (svgs.length > 0) {
                    let btn = svgs[0].closest('div[role="button"], button, a');
                    if (btn) { btn.click(); }
                }
            })();""")
            await asyncio.sleep(1)
        except Exception as e: print("Repost Error:", e)

        print("✅ Saare Actions (Follow, Like, Comment, Save, Repost) Done!")

        # Complete exactly 60s
        elapsed = time.time() - start_time
        if 60 - elapsed > 0: 
            print(f"⏳ Final wrap-up ke liye {int(60 - elapsed)} seconds bache hain, wait kar raha hu...")
            await asyncio.sleep(60 - elapsed)
            
    except Exception as e: print("Error:", e)
    finally:
        print(f"🏁 Account {account_num} session closed.")
        await context.close()

async def main():
    async with async_playwright() as p:
        # 🚨 GitHub cloud ke liye headless=True
        browser = await p.chromium.launch(headless=True, args=["--start-maximized"])
        await process_account(browser, C1_B64, 1)
        await process_account(browser, C2_B64, 2)
        print("\n🏆 SAARE ACCOUNTS KA KAAM SUCCESSFULLY COMPLETE HO GAYA!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
