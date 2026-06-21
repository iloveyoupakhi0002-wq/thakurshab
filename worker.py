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
        
        # --- PHASE 1: WARM-UP (Human Emulation) ---
        print("🏠 Warming up on Home Page...")
        await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        await asyncio.sleep(random.randint(4, 7))
        
        print("🎬 Clicking on Reels tab for timepass...")
        try:
            await page.evaluate("(() => { let a = document.querySelectorAll('a[href^=\"/reels/\"]'); if(a.length>0) a[0].click(); })();")
            await asyncio.sleep(random.randint(4, 7))
            print("👇 Scrolling to next random reel...")
            await page.keyboard.press("ArrowDown")
            await asyncio.sleep(random.randint(3, 6))
            print("👇 Scrolling again...")
            await page.keyboard.press("ArrowDown")
            await asyncio.sleep(random.randint(3, 6))
        except Exception as e:
            print("⚠️ Warm-up minor issue, ignoring...", e)

        # --- PHASE 2: TARGET URL ---
        print(f"\n🎯 Jumping to Target URL: {TARGET_URL}")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        
        print("⏳ Watching video peacefully for 10-15 seconds before doing anything...")
        await asyncio.sleep(random.randint(10, 15))
        
        current_comment = random.choice(COMMENTS_LIST)

        # --- PHASE 3: RANDOMIZED ACTIONS (The Card Shuffle) ---
        
        async def do_follow():
            try:
                print("👤 Action: Follow")
                await page.evaluate("(() => { let b = document.querySelectorAll('button, div[role=\"button\"]'); for(let x of b) { if(x.innerText === 'Follow') { x.click(); return; } } })();")
            except Exception as e: print("Follow Error:", e)

        async def do_like():
            try:
                print("❤️ Action: Like")
                await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Like\"]'); if(s.length>0) s[0].closest('div[role=\"button\"]').click(); })();")
            except Exception as e: print("Like Error:", e)

        async def do_save():
            try:
                print("🔖 Action: Save")
                await page.evaluate("""(() => {
                    let svgs = document.querySelectorAll('svg[aria-label="Save"], svg[aria-label="Bookmark"]');
                    if (svgs.length > 0) { let btn = svgs[0].closest('div[role="button"], button, a'); if (btn) { btn.click(); } }
                })();""")
            except Exception as e: print("Save Error:", e)

        async def do_repost():
            try:
                print("🔁 Action: Repost (2-Step)")
                repost_icon = page.locator('svg[aria-label="Repost"]').first
                await repost_icon.click(force=True)
                await asyncio.sleep(2) 
                repost_confirm = page.locator('div[role="button"]:has-text("Repost"), div[role="menuitem"]:has-text("Repost"), span:has-text("Repost")').last
                if await repost_confirm.count() > 0 and await repost_confirm.is_visible():
                    await repost_confirm.click(force=True)
                await asyncio.sleep(1)
            except Exception as e: print("Repost Error:", e)

        async def do_comment():
            try:
                print("💬 Action: Comment")
                await page.locator('svg[aria-label="Comment"]').first.click(force=True)
                await asyncio.sleep(3) 
                selectors = ['.xjbqb8w', 'textarea[aria-label*="comment" i]', 'div[role="textbox"]', 'input[placeholder*="comment" i]', 'textarea[placeholder*="comment" i]']
                box_found = False
                for sel in selectors:
                    target_box = page.locator(sel).last
                    if await target_box.count() > 0 and await target_box.is_visible():
                        await target_box.hover()
                        await asyncio.sleep(1)
                        await target_box.click(force=True)
                        box_found = True
                        break 
                if not box_found: await page.keyboard.press("Tab")
                
                await asyncio.sleep(1)
                await page.keyboard.type(current_comment, delay=150)
                await asyncio.sleep(1)
                
                try:
                    post_btn = page.locator('div[role="button"]:has-text("Post"), span:has-text("Post")').last
                    if await post_btn.count() > 0 and await post_btn.is_visible(): await post_btn.click(force=True)
                    else: await page.get_by_text("Post", exact=True).last.click(force=True)
                except: await page.keyboard.press("Enter")
                
                await asyncio.sleep(4)
                await page.keyboard.press("Escape")
                await asyncio.sleep(1)
            except Exception as e: print("Comment Error:", e)

        # 🎲 Actions ko shuffle kar rahe hain
        actions = [do_follow, do_like, do_save, do_repost, do_comment]
        random.shuffle(actions)

        print("🃏 Shuffle done! Actions is random sequence me chalenge:")
        for action in actions:
            await action() # Action chalega
            
            # Har action ke beech random aaram (insano ki tarah)
            wait_time = random.randint(4, 10)
            print(f"   ⏳ Waiting {wait_time}s before next move...")
            await asyncio.sleep(wait_time)

        print("✅ Saare Actions Random sequence me successfully poore hue!")

        # --- PHASE 4: SCREENSHOT (Reel Page Par) ---
        print("\n📸 Reel page par saare actions dikhane ke liye screenshot le raha hu...")
        screenshot_path = f"proof_{account_num}.png"
        await page.screenshot(path=screenshot_path)
        await send_screenshot(screenshot_path, f"✅ Account {account_num} Actions Done!\n⏱️ Destiny Time: {total_session_time}s\n📝 Text: {current_comment}")

        # --- PHASE 5: PROFILE DEEP DIVE (Fan Moment) ---
        try:
            print("\n🕵️‍♂️ Clicking on Username to visit profile...")
            js_profile = """
            (() => {
                let svgs = document.querySelectorAll('canvas'); 
                if (svgs.length > 0) { let a = svgs[0].closest('a'); if (a) { a.click(); return; } }
                let btns = document.querySelectorAll('button, div[role="button"]');
                for(let b of btns) {
                    if(b.innerText === 'Follow' || b.innerText === 'Following') {
                        let link = b.closest('div').parentNode.querySelector('a');
                        if (link) { link.click(); return; }
                    }
                }
            })();
            """
            await page.evaluate(js_profile)
            print("⏳ Profile page par wait kar raha hu jab tak Destiny Timer poora na ho jaye...")
        except Exception as e:
            print("⚠️ Profile click mein issue, par video loop hoti rahegi...")

        # --- PHASE 6: EXACT WRAP-UP ---
        elapsed = time.time() - session_start_time
        remaining_time = total_session_time - elapsed
        
        if remaining_time > 0: 
            print(f"⏳ Session close hone me {int(remaining_time)} seconds bache hain...")
            await asyncio.sleep(remaining_time)
            
    except Exception as e: print("Error:", e)
    finally:
        print(f"🏁 Account {account_num} session closed perfectly at Destiny Time.")
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
