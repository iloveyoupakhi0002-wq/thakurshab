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
        
        print("⏳ Waiting exactly 7 seconds for popups to appear...")
        await asyncio.sleep(7)
        print("⌨️ Pressing 'Escape' to close any notifications/popups...")
        await page.keyboard.press("Escape")
        await asyncio.sleep(1) 

        print(f"🎯 Going to Target URL: {TARGET_URL}")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        start_time = time.time()
        
        # --- RANDOM ACTION START TIME (15s to 45s) ---
        action_start_delay = random.randint(15, 45)
        print(f"⏳ Bot ab {action_start_delay} seconds wait karega actions shuru karne se pehle...")
        await asyncio.sleep(action_start_delay)
        
        current_comment = random.choice(COMMENTS_LIST)
        
        # 🟢 Action Functions (100% Scroll-Proof via JavaScript)
        async def do_like():
            try:
                print("❤️ Trying to Like...")
                await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Like\"]'); if(s.length>0) { let b = s[0].closest('div[role=\"button\"]'); if(b) b.click(); } })();")
                await asyncio.sleep(1)
            except Exception as e: print("Like Error:", e)

        async def do_save():
            try:
                print("🔖 Trying to Save...")
                await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Save\"], svg[aria-label=\"Bookmark\"]'); if(s.length>0) { let b = s[0].closest('div[role=\"button\"]'); if(b) b.click(); } })();")
                await asyncio.sleep(1)
            except Exception as e: print("Save Error:", e)

        async def do_repost():
            try:
                print("🔁 Trying to Repost (Share)...")
                # JS ke zariye Share icon click karenge taaki scroll na ho
                clicked = await page.evaluate("""(() => {
                    let s = document.querySelectorAll('svg[aria-label="Share Post"], svg[aria-label="Share"], svg[aria-label="Repost"]');
                    if(s.length>0) { 
                        let b = s[0].closest('div[role="button"], button, a'); 
                        if(b) { b.click(); return true; }
                    }
                    return false;
                })();""")
                
                if clicked:
                    await asyncio.sleep(2) 
                    # Confirm Repost bhi JS se karenge
                    await page.evaluate("""(() => {
                        let elements = document.querySelectorAll('div[role="button"], span, div');
                        for(let el of elements) {
                            if(el.textContent && el.textContent.trim() === 'Repost') {
                                let btn = el.closest('div[role="button"]') || el;
                                btn.click();
                                break;
                            }
                        }
                    })();""")
                    print("✅ Repost done via JS!")
                await asyncio.sleep(1)
            except Exception as e: 
                print(f"❌ Repost Error: {e}")

        async def do_comment():
            try:
                print("💬 Trying to Comment...")
                # 1. Comment icon par JS se click (No Scroll)
                icon_clicked = await page.evaluate("""(() => {
                    let s = document.querySelectorAll('svg[aria-label="Comment"]');
                    if(s.length>0) { 
                        let b = s[0].closest('div[role="button"], button, a'); 
                        if(b) { b.click(); return true; }
                    }
                    return false;
                })();""")
                
                if not icon_clicked:
                    print("⚠️ Comment icon nahi mila.")
                    return

                await asyncio.sleep(3) 
                
                # 2. Text Box dhundhkar usko focus karna (JS se)
                box_focused = await page.evaluate("""(() => {
                    let box = document.querySelector('textarea[aria-label*="comment" i], div[role="textbox"], input[placeholder*="comment" i], textarea[placeholder*="comment" i]');
                    if(box) { 
                        box.focus(); 
                        box.click(); 
                        return true; 
                    }
                    return false;
                })();""")
                
                if box_focused:
                    await asyncio.sleep(1)
                    # Ab safe hai type karna
                    await page.keyboard.type(current_comment, delay=150)
                    await asyncio.sleep(1)
                    
                    # 3. Post button par JS se click (No Scroll)
                    await page.evaluate("""(() => {
                        let elements = document.querySelectorAll('div[role="button"], span');
                        for(let el of elements) {
                            if(el.textContent && el.textContent.trim() === 'Post') {
                                let btn = el.closest('div[role="button"]') || el;
                                btn.click();
                                break;
                            }
                        }
                    })();""")
                else:
                    print("⚠️ Comment box detect nahi hua.")
                    
                await asyncio.sleep(4)
                # 🚨 Yahan se 'Escape' hata diya hai taaki video player galti se close ya jump na ho
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
        browser = await p.chromium.launch(channel="chrome", headless=True, args=["--start-maximized"])
        await process_account(browser, C1_B64, 1)
        await process_account(browser, C2_B64, 2)
        print("\n🏆 SAARE ACCOUNTS KA KAAM SUCCESSFULLY COMPLETE HO GAYA!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())s
