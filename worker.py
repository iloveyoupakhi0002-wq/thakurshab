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

# 🛡️ Telegram Screenshot Sender
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
    
    # ⏱️ DESTINY TIMER: 90 se 115 seconds ke beech random total time
    total_session_time = random.randint(90, 115)
    print(f"⏱️ Is account ka Destiny Timer set hua hai: {total_session_time} seconds!")
    print(f"=========================================")
    
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
        session_start_time = time.time()
        
        # --- PHASE 1: WARM-UP ---
        print("🏠 Warming up on Home Page...")
        await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        await asyncio.sleep(random.randint(4, 7))
        
        print("🎬 Clicking on Reels tab for timepass...")
        try:
            await page.evaluate("(() => { let a = document.querySelectorAll('a[href^=\"/reels/\"]'); if(a.length>0) a[0].click(); })();")
            await asyncio.sleep(random.randint(4, 7))
            await page.keyboard.press("ArrowDown")
            await asyncio.sleep(random.randint(3, 6))
            await page.keyboard.press("ArrowDown")
            await asyncio.sleep(random.randint(3, 6))
        except Exception as e:
            print("⚠️ Warm-up minor issue, ignoring...", e)

        # --- PHASE 2: TARGET URL (Bug Fix: SPA Navigation Lock) ---
        print("\n🧹 Clearing page state to avoid wrong video bug...")
        await page.goto("about:blank") # Yeh trick Insta ko refresh karne par majboor karegi
        
        print(f"🎯 Jumping EXACTLY to Target URL: {TARGET_URL}")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        
        print("⏳ Watching video peacefully for 10-15 seconds before doing anything...")
        await asyncio.sleep(random.randint(10, 15))
        
        current_comment = random.choice(COMMENTS_LIST)

        # --- PHASE 3: RANDOMIZED ACTIONS (Native Locators Only) ---

        async def do_like():
            try:
                print("❤️ Action: Like")
                like_btn = page.locator('svg[aria-label="Like"]').first
                if await like_btn.count() > 0:
                    await like_btn.click(force=True)
            except Exception as e: print("Like Error:", e)

        async def do_save():
            try:
                print("🔖 Action: Save")
                save_btn = page.locator('svg[aria-label="Save"]').first
                if await save_btn.count() > 0:
                    await save_btn.click(force=True)
            except Exception as e: print("Save Error:", e)

        async def do_repost():
            try:
                print("🔁 Action: Repost")
                repost_icon = page.locator('svg[aria-label="Repost"]').first
                if await repost_icon.count() > 0:
                    await repost_icon.click(force=True)
                    await asyncio.sleep(2) 
                    repost_confirm = page.locator('div[role="button"]:has-text("Repost"), span:has-text("Repost")').last
                    if await repost_confirm.count() > 0 and await repost_confirm.is_visible():
                        await repost_confirm.click(force=True)
                await asyncio.sleep(1)
            except Exception as e: print("Repost Error:", e)

        async def do_comment():
            try:
                print("💬 Action: Comment (Strict Sniper Mode)")
                comment_icon = page.locator('svg[aria-label="Comment"]').first
                if await comment_icon.count() > 0:
                    await comment_icon.click(force=True)
                    await asyncio.sleep(3) 
                    
                    # Direct click on the editable div instead of searching P tags
                    editor = page.locator('div[contenteditable="true"][role="textbox"], textarea[aria-label*="comment" i]').first
                    
                    if await editor.count() > 0 and await editor.is_visible():
                        print("✅ Dabba mil gaya, click kar raha hu...")
                        await editor.click(force=True)
                        await asyncio.sleep(1)
                        
                        print(f"⌨️ Typing: {current_comment}")
                        await page.keyboard.type(current_comment, delay=150)
                        await asyncio.sleep(1)
                        
                        print("🚀 Post daba raha hu...")
                        post_btn = page.locator('div[role="button"]:has-text("Post"), span:has-text("Post")').last
                        if await post_btn.count() > 0 and await post_btn.is_visible():
                            await post_btn.click(force=True)
                        else:
                            await page.keyboard.press("Enter")
                    else:
                        print("⚠️ Editor nahi mila!")
                    
                    await asyncio.sleep(4)
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(1)
            except Exception as e: print("Comment Error:", e)

        # 🎲 Sirf 4 Actions ko shuffle kar rahe hain
        actions = [do_like, do_save, do_repost, do_comment]
        random.shuffle(actions)

        print("🃏 Actions is random sequence me chalenge:")
        for action in actions:
            await action() 
            wait_time = random.randint(4, 10)
            print(f"   ⏳ Waiting {wait_time}s before next move...")
            await asyncio.sleep(wait_time)

        print("✅ Saare Actions poore hue!")

        # --- PHASE 4: SCREENSHOT ---
        print("\n📸 Reel page par screenshot le raha hu...")
        screenshot_path = f"proof_{account_num}.png"
        await page.screenshot(path=screenshot_path)
        await send_screenshot(screenshot_path, f"✅ Account {account_num} Actions Done!\n⏱️ Destiny Time: {total_session_time}s\n📝 Text: {current_comment}")

        # --- PHASE 5: EXACT WRAP-UP (No Profile Click for Maximum Safety) ---
        elapsed = time.time() - session_start_time
        remaining_time = total_session_time - elapsed
        
        if remaining_time > 0: 
            print(f"⏳ Session close hone me {int(remaining_time)} seconds bache hain, watch time de raha hu...")
            await asyncio.sleep(remaining_time)
            
    except Exception as e: print("Error:", e)
    finally:
        print(f"🏁 Account {account_num} session closed perfectly.")
        await context.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--start-maximized"])
        await process_account(browser, C1_B64, 1)
        await process_account(browser, C2_B64, 2)
        print("\n🏆 SAARE ACCOUNTS KA KAAM SUCCESSFULLY COMPLETE HO GAYA!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
