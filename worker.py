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
        await page.goto(TARGET_URL, wait_until="networkidle")
        await asyncio.sleep(4)

        # 🛡️ FIX 1: Turn on Notifications ya popups ko Escape dabakar close karna
        print("🛑 Closing popups (if any) using Escape key...")
        await page.keyboard.press("Escape")
        await asyncio.sleep(2)
        await page.keyboard.press("Escape") # Ek extra baar safe side ke liye
        await asyncio.sleep(1)
        
        # 🛡️ FIX 2: URL Verification Check (Galat video par jane se rokne ke liye)
        current_url = page.url
        if TARGET_URL and TARGET_URL.split('?')[0] not in current_url: 
            print(f"⚠️ Oops! Instagram ne redirect kar diya (Current: {current_url}). Wapas Target URL par jaa raha hu...")
            await page.goto(TARGET_URL, wait_until="networkidle")
            await asyncio.sleep(4)
            await page.keyboard.press("Escape") # Fir se popup hatao
            
            if TARGET_URL.split('?')[0] not in page.url:
                print("❌ Account target video par nahi pohoch paaya. Skipping...")
                return

        # Reels infinite scroll ko rokne ke liye ek baar page par click karke focus le aao
        try:
            await page.mouse.click(500, 500) 
        except:
            pass

        start_time = time.time()
        
        # --- RANDOM ACTION START TIME (15s to 45s) ---
        action_start_delay = random.randint(15, 45)
        print(f"⏳ Bot ab {action_start_delay} seconds wait karega actions shuru karne se pehle...")
        await asyncio.sleep(action_start_delay)
        
        current_comment = random.choice(COMMENTS_LIST)
        
        # Action Functions Define kar rahe hain taki inko random order me chala sakein
        async def do_like():
            try:
                print("❤️ Trying to Like...")
                await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Like\"]'); if(s.length>0) s[0].closest('div[role=\"button\"]').click(); })();")
                await asyncio.sleep(1)
            except Exception as e: print("Like Error:", e)

        async def do_save():
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

        async def do_repost():
            try:
                print("🔁 Trying to Repost...")
                repost_icon = page.locator('svg[aria-label="Repost"]').first
                await repost_icon.click(force=True)
                await asyncio.sleep(2) 
                repost_confirm = page.locator('div[role="button"]:has-text("Repost"), div[role="menuitem"]:has-text("Repost"), span:has-text("Repost")').last
                if await repost_confirm.count() > 0 and await repost_confirm.is_visible():
                    await repost_confirm.click(force=True)
                    print("✅ Repost confirm ho gaya!")
                else:
                    print("✅ Repost icon click ho gaya (fallback).")
                await asyncio.sleep(1)
            except Exception as e: 
                print(f"❌ Repost Error: {e}")

        async def do_comment():
            try:
                print("💬 Trying to Comment...")
                await page.locator('svg[aria-label="Comment"]').first.click(force=True)
                await asyncio.sleep(3) 
                selectors = [
                    'textarea[aria-label*="comment" i]', 'div[role="textbox"]',
                    'input[placeholder*="comment" i]', 'textarea[placeholder*="comment" i]', '.xjbqb8w'
                ]
                box_found = False
                for selector in selectors:
                    target_box = page.locator(selector).last
                    if await target_box.count() > 0 and await target_box.is_visible():
                        await target_box.hover()
                        await asyncio.sleep(1)
                        await target_box.click(force=True)
                        box_found = True
                        break 
                
                if not box_found:
                    await page.keyboard.press("Tab")
                
                await asyncio.sleep(1)
                await page.keyboard.type(current_comment, delay=random.randint(100, 250)) # Added random human delay here too
                await asyncio.sleep(1)
                
                try:
                    post_btn = page.locator('div[role="button"]:has-text("Post"), span:has-text("Post")').last
                    if await post_btn.count() > 0 and await post_btn.is_visible():
                        await post_btn.click(force=True)
                    else:
                        await page.get_by_text("Post", exact=True).last.click(force=True)
                except Exception:
                    await page.keyboard.press("Enter")
                    
                await asyncio.sleep(4)
                await page.keyboard.press("Escape")
                await asyncio.sleep(1)
            except Exception as e: 
                print(f"❌ Comment completely fail hua: {e}")

        # --- RANDOMIZE WORKFLOW ORDER ---
        actions = [
            ("Like", do_like),
            ("Save", do_save),
            ("Repost", do_repost),
            ("Comment", do_comment)
        ]
        random.shuffle(actions) 
        
        print("🎲 Random Action Order:", [a[0] for a in actions])
        for name, action in actions:
            await action()
            await asyncio.sleep(random.uniform(1, 3)) 

        print("✅ Saare Actions (Random Order mein) Done!")

        # --- EXACT 75th SECOND SCREENSHOT LOGIC ---
        elapsed = time.time() - start_time
        wait_for_75 = 75 - elapsed
        if wait_for_75 > 0:
            print(f"⏳ 75s mark tak pahunchne ke liye {int(wait_for_75)}s aur ruk raha hu...")
            await asyncio.sleep(wait_for_75)
            
        screenshot_path = f"proof_{account_num}.png"
        await page.screenshot(path=screenshot_path)
        print("📸 75th Second par Screenshot liya! Telegram par bhej raha hu...")
        await send_screenshot(screenshot_path, f"✅ Account {account_num} ka kaam aur 75s ka proof!\n📝 Comment: {current_comment}")

        # --- RANDOM EXIT BETWEEN 80 to 90 SECONDS ---
        exit_time_target = random.randint(80, 90)
        elapsed_now = time.time() - start_time
        wait_for_exit = exit_time_target - elapsed_now
        
        if wait_for_exit > 0: 
            print(f"⏳ Final Random Exit ({exit_time_target}s) ke liye {int(wait_for_exit)} seconds bache hain, wait kar raha hu...")
            await asyncio.sleep(wait_for_exit)
            
    except Exception as e: print("Error:", e)
    finally:
        total_time_spent = int(time.time() - start_time) if 'start_time' in locals() else 0
        print(f"🏁 Account {account_num} session closed after ~{total_time_spent} seconds.")
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
