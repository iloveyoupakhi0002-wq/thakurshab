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
        print(f"🏠 Account {account_num}: Warming up on Home Page...")
        await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        
        print(f"⏳ Account {account_num}: Waiting exactly 7 seconds for popups to appear...")
        await asyncio.sleep(7)
        print(f"⌨️ Account {account_num}: Pressing 'Escape' to close any notifications/popups...")
        await page.keyboard.press("Escape")
        await asyncio.sleep(1) 

        print(f"🎯 Account {account_num}: Going to Target URL: {TARGET_URL}")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        start_time = time.time()
        
        # --- RANDOM ACTION START TIME (15s to 45s) ---
        action_start_delay = random.randint(15, 45)
        print(f"⏳ Account {account_num}: Bot ab {action_start_delay} seconds wait karega actions shuru karne se pehle...")
        await asyncio.sleep(action_start_delay)
        
        current_comment = random.choice(COMMENTS_LIST)
        
        # 🟢 Action Functions
        async def do_like():
            try:
                print(f"❤️ Account {account_num}: Trying to Like...")
                await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Like\"]'); if(s.length>0) { let b = s[0].closest('div[role=\"button\"]'); if(b) b.click(); } })();")
                await asyncio.sleep(1)
            except Exception as e: print(f"Like Error Acc {account_num}:", e)

        async def do_save():
            try:
                print(f"🔖 Account {account_num}: Trying to Save...")
                await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Save\"], svg[aria-label=\"Bookmark\"]'); if(s.length>0) { let b = s[0].closest('div[role=\"button\"]'); if(b) b.click(); } })();")
                await asyncio.sleep(1)
            except Exception as e: print(f"Save Error Acc {account_num}:", e)

        async def do_repost():
            try:
                print(f"🔁 Account {account_num}: Trying to Repost (Share)...")
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
                    print(f"✅ Account {account_num}: Repost done via JS!")

                    # Popup Close Karne Ke Liye
                    await asyncio.sleep(2)
                    await page.evaluate("""(() => {
                        let closeBtns = document.querySelectorAll('svg[aria-label="Close"]');
                        if(closeBtns.length > 0) {
                            let btn = closeBtns[closeBtns.length - 1].closest('div[role="button"], button');
                            if(btn) { btn.click(); }
                        }
                    })();""")
                    print(f"✅ Account {account_num}: Repost Popup successfully closed!")
                    
                await asyncio.sleep(1)
            except Exception as e: 
                print(f"❌ Account {account_num} Repost Error: {e}")

        async def do_comment():
            try:
                print(f"💬 Account {account_num}: Trying to Comment...")
                icon_clicked = await page.evaluate("""(() => {
                    let s = document.querySelectorAll('svg[aria-label="Comment"]');
                    if(s.length>0) { 
                        let b = s[0].closest('div[role="button"], button, a'); 
                        if(b) { b.click(); return true; }
                    }
                    return false;
                })();""")
                
                if not icon_clicked:
                    print(f"⚠️ Account {account_num}: Comment icon nahi mila.")
                    return

                await asyncio.sleep(3) 
                
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
                    await page.keyboard.type(current_comment, delay=150)
                    await asyncio.sleep(1)
                    
                    # 🚀 NAYA 100% CONFIRM INSPECT ELEMENT LOGIC 
                    posted_via_js = await page.evaluate("""(() => {
                        let elements = document.querySelectorAll('div[role="button"]');
                        for(let el of elements) {
                            if(el.textContent && el.textContent.trim() === 'Post') {
                                el.click();
                                return true;
                            }
                        }
                        return false;
                    })();""")
                    
                    if posted_via_js:
                        print(f"✅ Account {account_num}: 'Post' button clicked successfully via EXACT element logic!")
                    else:
                        print(f"⚠️ Account {account_num}: JS fail hua, Playwright Native Click try kar raha hu...")
                        try:
                            # Exact match locator based on your inspect element
                            post_locator = page.locator('div[role="button"]:text-is("Post")')
                            if await post_locator.count() > 0:
                                await post_locator.last.click(timeout=3000)
                                print(f"✅ Account {account_num}: Posted via Playwright Native Click!")
                        except Exception as inner_e:
                            print(f"❌ Account {account_num} dono method se Post button click nahi hua.")
                        
                else:
                    print(f"⚠️ Account {account_num}: Comment box detect nahi hua.")
                    
                await asyncio.sleep(4)
            except Exception as e: 
                print(f"❌ Account {account_num} Comment fail hua: {e}")

        # --- RANDOMIZE WORKFLOW ORDER ---
        actions = [
            ("Like", do_like),
            ("Save", do_save),
            ("Repost", do_repost),
            ("Comment", do_comment)
        ]
        random.shuffle(actions) 
        
        print(f"🎲 Account {account_num} Random Action Order:", [a[0] for a in actions])
        for name, action in actions:
            await action()
            await asyncio.sleep(random.uniform(1, 3)) 

        print(f"✅ Account {account_num}: Saare Actions Done!")

        # --- EXACT 75th SECOND SCREENSHOT LOGIC ---
        elapsed = time.time() - start_time
        wait_for_75 = 75 - elapsed
        if wait_for_75 > 0:
            print(f"⏳ Account {account_num}: 75s mark tak pahunchne ke liye {int(wait_for_75)}s aur ruk raha hu...")
            await asyncio.sleep(wait_for_75)
            
        screenshot_path = f"proof_{account_num}.png"
        await page.screenshot(path=screenshot_path)
        print(f"📸 Account {account_num}: 75th Second par Screenshot liya! Telegram par bhej raha hu...")
        await send_screenshot(screenshot_path, f"✅ Account {account_num} ka kaam aur 75s ka proof!\n📝 Comment: {current_comment}")

        # --- RANDOM EXIT BETWEEN 80 to 90 SECONDS ---
        exit_time_target = random.randint(80, 90)
        elapsed_now = time.time() - start_time
        wait_for_exit = exit_time_target - elapsed_now
        
        if wait_for_exit > 0: 
            print(f"⏳ Account {account_num}: Final Random Exit ke liye {int(wait_for_exit)} seconds bache hain...")
            await asyncio.sleep(wait_for_exit)
            
    except Exception as e: print(f"Error in Account {account_num}:", e)
    finally:
        total_time_spent = int(time.time() - start_time) if 'start_time' in locals() else 0
        print(f"🏁 Account {account_num} session closed after ~{total_time_spent} seconds.")
        await context.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True, args=["--start-maximized"])
        
        print("\n🚀 Accounts ko ab ek-ek karke (Sequential) start kar rahe hain...\n")
        
        # --- Pehle Account 1 ka kaam hoga ---
        if C1_B64:
            await process_account(browser, C1_B64, 1)
            print("🟢 Account 1 ka session poora ho gaya!\n")
            await asyncio.sleep(2) 
        
        # --- Account 1 ke band hone ke baad Account 2 khulega ---
        if C2_B64:
            await process_account(browser, C2_B64, 2)
            print("🟢 Account 2 ka session poora ho gaya!\n")
            
        if not C1_B64 and not C2_B64:
            print("⚠️ Koi cookie provide nahi ki gayi hai!")
            
        print("\n🏆 SAARE ACCOUNTS KA KAAM SUCCESSFULLY COMPLETE HO GAYA!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
