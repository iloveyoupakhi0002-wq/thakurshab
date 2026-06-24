import asyncio
import base64
import json
import os
import random
import time

import requests
from playwright.async_api import async_playwright

TARGET_URL = os.environ.get("TARGET_URL")
CHAT_ID = os.environ.get("CHAT_ID")
TG_TOKEN = os.environ.get("TG_TOKEN")
C1_B64 = os.environ.get("COOKIE_1")
C2_B64 = os.environ.get("COOKIE_2")

COMMENTS_LIST = ["🔥 Ek number bhai!", "Bhai kya baat hai! 😍", "Superb video bro 🚀", "Gajab editing 👏"]

# ---------- HUMAN-LIKE MOUSE MOVEMENTS ----------
async def human_like_move(page, target_x, target_y, steps=None, wobble=10):
    if steps is None:
        steps = random.randint(15, 30)
    start_x, start_y = random.randint(100, 600), random.randint(200, 700)
    for i in range(steps):
        progress = (i + 1) / steps
        ease = progress ** random.uniform(0.3, 3)
        x = start_x + (target_x - start_x) * ease + random.randint(-wobble, wobble)
        y = start_y + (target_y - start_y) * ease + random.randint(-wobble, wobble)
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.005, 0.02))

async def human_like_click(page, element):
    try:
        box = await element.bounding_box()
        if box:
            center_x = box['x'] + box['width'] / 2 + random.randint(-3, 3)
            center_y = box['y'] + box['height'] / 2 + random.randint(-3, 3)
            await human_like_move(page, center_x, center_y)
            await asyncio.sleep(random.uniform(0.1, 0.3))
            await page.mouse.click(center_x, center_y, delay=random.randint(20, 80))
            return
    except Exception:
        pass
    await element.click(force=True, delay=random.randint(100, 300))

async def random_scroll(page):
    scroll_amount = random.randint(200, 800)
    direction = random.choice(['down', 'up', 'down'])
    if direction == 'down':
        await page.mouse.wheel(0, scroll_amount)
    elif direction == 'up':
        await page.mouse.wheel(0, -scroll_amount)
    await asyncio.sleep(random.uniform(0.3, 1.5))

async def send_screenshot(image_path, text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
    def _upload():
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with open(image_path, 'rb') as photo:
                    res = requests.post(url, data={'chat_id': CHAT_ID, 'caption': text}, files={'photo': photo}, timeout=20)
                if res.status_code == 200:
                    break
            except Exception:
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

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    viewport = {'width': random.randint(1280, 1920), 'height': random.randint(720, 1080)}

    context = await browser.new_context(
        viewport=viewport,
        user_agent=random.choice(user_agents),
        locale=random.choice(['en-US', 'en-GB', 'en-IN']),
        timezone_id='Asia/Kolkata',
        permissions=['geolocation'],
        geolocation={'latitude': 28.6139, 'longitude': 77.2090},
        color_scheme=random.choice(['light', 'dark']),
    )

    await context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
    });
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
    });
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
    });
    window.chrome = { runtime: {} };
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    Object.defineProperty(window, 'outerWidth', {
        get: () => window.innerWidth,
    });
    Object.defineProperty(window, 'outerHeight', {
        get: () => window.innerHeight,
    });
    """)

    cleaned_cookies = []
    for c in cookies:
        if 'sameSite' in c and c['sameSite'] not in ['Strict', 'Lax', 'None']:
            c['sameSite'] = 'Lax'
        if 'id' in c:
            del c['id']
        cleaned_cookies.append(c)

    await context.add_cookies(cleaned_cookies)
    page = await context.new_page()

    start_time = time.time()
    try:
        print("🏠 Warming up: Home page...")
        await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        await asyncio.sleep(random.randint(3, 6))
        for _ in range(random.randint(2, 4)):
            await random_scroll(page)
        if random.random() < 0.3:
            print("🔍 Exploring Explore page...")
            await page.goto("https://www.instagram.com/explore/", wait_until="domcontentloaded")
            await asyncio.sleep(random.randint(2, 5))
            await random_scroll(page)

        print(f"🎯 Going to Target URL...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        await asyncio.sleep(random.randint(2, 5))
        await random_scroll(page)

        action_start_delay = random.randint(15, 45)
        print(f"⏳ Actions shuru hone se pehle {action_start_delay}s wait...")
        remaining = action_start_delay
        while remaining > 0:
            chunk = min(remaining, random.randint(1, 5))
            await asyncio.sleep(chunk)
            remaining -= chunk
            if random.random() < 0.2:
                await random_scroll(page)
            if random.random() < 0.3:
                await human_like_move(page, random.randint(100, 800), random.randint(100, 700))

        current_comment = random.choice(COMMENTS_LIST)

        async def do_like():
            try:
                print("❤️ Trying to Like...")
                like_btn = page.locator('svg[aria-label="Like"]').first
                if await like_btn.count() > 0:
                    await human_like_click(page, like_btn)
                else:
                    await page.evaluate("""
                        (() => {
                            let s = document.querySelectorAll('svg[aria-label="Like"]');
                            if(s.length>0) s[0].closest('div[role="button"]').click();
                        })();
                    """)
                await asyncio.sleep(random.uniform(0.8, 1.5))
            except Exception as e:
                print("Like Error:", e)

        async def do_save():
            try:
                print("🔖 Trying to Save...")
                save_btns = page.locator('svg[aria-label="Save"], svg[aria-label="Bookmark"]').first
                if await save_btns.count() > 0:
                    await human_like_click(page, save_btns)
                else:
                    await page.evaluate("""(() => {
                        let svgs = document.querySelectorAll('svg[aria-label="Save"], svg[aria-label="Bookmark"]');
                        if (svgs.length > 0) {
                            let btn = svgs[0].closest('div[role="button"], button, a');
                            if (btn) { btn.click(); }
                        }
                    })();""")
                await asyncio.sleep(random.uniform(0.8, 1.5))
            except Exception as e:
                print("Save Error:", e)

        async def do_repost():
            try:
                print("🔁 Trying to Repost...")
                repost_icon = page.locator('svg[aria-label="Repost"]').first
                if await repost_icon.count() > 0:
                    await human_like_click(page, repost_icon)
                    await asyncio.sleep(random.uniform(1.5, 2.5))
                    repost_confirm = page.locator('div[role="button"]:has-text("Repost"), div[role="menuitem"]:has-text("Repost"), span:has-text("Repost")').last
                    if await repost_confirm.count() > 0 and await repost_confirm.is_visible():
                        await human_like_click(page, repost_confirm)
                        print("✅ Repost confirm.")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"❌ Repost Error: {e}")

        async def do_comment():
            try:
                print("💬 Trying to Comment...")
                comment_icon = page.locator('svg[aria-label="Comment"]').first
                if await comment_icon.count() > 0:
                    await human_like_click(page, comment_icon)
                await asyncio.sleep(random.uniform(2, 4))

                selectors = [
                    'textarea[aria-label*="comment" i]',
                    'div[role="textbox"]',
                    'input[placeholder*="comment" i]',
                    'textarea[placeholder*="comment" i]',
                    '.xjbqb8w'
                ]
                box = None
                for s in selectors:
                    tmp = page.locator(s).last
                    if await tmp.count() > 0 and await tmp.is_visible():
                        box = tmp
                        break
                if box:
                    await human_like_click(page, box)
                else:
                    await page.keyboard.press("Tab")
                    await asyncio.sleep(0.5)

                if random.random() < 0.05:
                    print("❌ Oops! User ne comment type karne ke baad cancel kar diya...")
                    await page.keyboard.press("Escape")
                    return

                await page.keyboard.type(current_comment, delay=random.randint(100, 250))
                await asyncio.sleep(random.uniform(0.5, 1))

                post_btn = page.locator('div[role="button"]:has-text("Post"), span:has-text("Post")').last
                if await post_btn.count() > 0 and await post_btn.is_visible():
                    await human_like_click(page, post_btn)
                else:
                    await page.keyboard.press("Enter")
                await asyncio.sleep(3)
                try:
                    close_btn = page.locator('svg[aria-label="Close"]')
                    if await close_btn.count() > 0:
                        await human_like_click(page, close_btn.first)
                except:
                    pass
                await page.keyboard.press("Escape")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"❌ Comment fail: {e}")

        possible_actions = [
            ("Like", do_like),
            ("Save", do_save),
            ("Repost", do_repost),
            ("Comment", do_comment)
        ]
        actions_to_do = possible_actions.copy()
        if random.random() < 0.2:
            skip_count = random.randint(1, 2)
            actions_to_do = random.sample(possible_actions, k=len(possible_actions) - skip_count)
        random.shuffle(actions_to_do)

        print("🎲 Action order:", [a[0] for a in actions_to_do])
        for name, action in actions_to_do:
            if random.random() < 0.4:
                await random_scroll(page)
            await human_like_move(page, random.randint(200, 1000), random.randint(200, 800))
            await action()
            await asyncio.sleep(random.uniform(1, 3))

        print("✅ Actions (random order) done!")

        elapsed = time.time() - start_time
        wait_for_75 = 75 - elapsed
        if wait_for_75 > 0:
            print(f"⏳ 75s completion ke liye {int(wait_for_75)}s aur ruk raha hu...")
            end_time = time.time() + wait_for_75
            while time.time() < end_time:
                if random.random() < 0.2:
                    await random_scroll(page)
                else:
                    await human_like_move(page, random.randint(100, 900), random.randint(100, 700))
                await asyncio.sleep(random.uniform(0.5, 2))

        screenshot_path = f"proof_{account_num}.png"
        await page.screenshot(path=screenshot_path)
        print("📸 Screenshot liya! Telegram pe bhej raha hu...")
        await send_screenshot(screenshot_path, f"✅ Account {account_num} done!\n📝 Comment: {current_comment}")

        exit_time_target = random.randint(80, 90)
        elapsed_now = time.time() - start_time
        wait_for_exit = exit_time_target - elapsed_now
        if wait_for_exit > 0:
            print(f"⏳ Exit hone se pehle {int(wait_for_exit)}s aur...")
            end_time = time.time() + wait_for_exit
            while time.time() < end_time:
                if random.random() < 0.3:
                    await random_scroll(page)
                await human_like_move(page, random.randint(100, 900), random.randint(100, 700))
                await asyncio.sleep(random.uniform(0.5, 1.5))

    except Exception as e:
        print("Error:", e)
    finally:
        total_time_spent = int(time.time() - start_time) if 'start_time' in locals() else 0
        print(f"🏁 Account {account_num} session closed ~{total_time_spent}s.")
        await context.close()

async def main():
    async with async_playwright() as p:
        # ✅ headless=True (boolean, no string) – GitHub Actions ke liye perfect
        browser = await p.chromium.launch(
            headless=True,   # <-- yahi fix hai
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )
        await process_account(browser, C1_B64, 1)
        await process_account(browser, C2_B64, 2)
        print("\n🏆 SAARE ACCOUNTS KA KAAM SUCCESSFULLY COMPLETE HO GAYA!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
