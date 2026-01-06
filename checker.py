import asyncio
import argparse
import random
import os
from playwright.async_api import async_playwright
from colorama import Fore, Style, init
from tqdm.asyncio import tqdm

init(autoreset=True)

class XChecker:
    def __init__(self, use_proxies=None):
        self.proxies = use_proxies if use_proxies else []
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.0.0 Safari/537.36"
        ]

    def get_proxy(self):
        if not self.proxies: return None
        return {"server": random.choice(self.proxies).strip()}

    async def check_username(self, browser, username):
        proxy = self.get_proxy()
        # Increased stealth: Custom viewport and disabling automation flags
        context = await browser.new_context(
            user_agent=random.choice(self.user_agents),
            proxy=proxy if proxy else None,
            viewport={'width': 1280, 'height': 720}
        )
        
        page = await context.new_page()
        # Extra script to hide automation fingerprints
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        url = f"https://x.com/{username}"
        status = "UNKNOWN"
        
        try:
            # Wait a bit longer to simulate human speed
            await asyncio.sleep(random.uniform(2.0, 4.0))
            
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Wait for specific content to load
            await asyncio.sleep(1.5)
            content = await page.content()

            # 1. Check for Login Wall (Rate Limit/Bot Detection)
            if "Log in to X" in content or "Sign in to X" in content or "rb_login_count" in content:
                status = "BLOCKED/LOGIN_REQUIRED"
            
            # 2. Check for 404 or "Doesn't exist" (Available)
            elif response and response.status == 404:
                status = "AVAILABLE"
            elif "This account doesn’t exist" in content or "Try searching for another" in content:
                status = "AVAILABLE"
            
            # 3. Check for Suspended
            elif "Account suspended" in content:
                status = "TAKEN (SUSPENDED)"
            
            # 4. Check for existing profile indicators
            elif "UserProfileHeader" in content or "Follow" in content or "Joined" in content:
                status = "TAKEN"
                
            else:
                # If we aren't sure, check status code
                if response and response.status == 200:
                    status = "TAKEN"
                else:
                    status = "UNKNOWN/CHECK_FAILED"

            if status == "AVAILABLE":
                with open("available_found.txt", "a") as f:
                    f.write(f"{username}\n")

        except Exception as e:
            status = f"TIMEOUT/ERROR"
        finally:
            await context.close()
            return username, status

async def main():
    parser = argparse.ArgumentParser(description="X Username Bulk Checker")
    parser.add_argument("--file", default="usernames.txt", help="File with usernames")
    parser.add_argument("--proxy", help="File with proxies")
    parser.add_argument("--workers", type=int, default=2, help="Concurrent workers (Keep low for better stability)")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        with open(args.file, "w") as f: f.write("elonmusk\navailable_user_992211")
        print(f"{Fore.YELLOW}[!] Created {args.file}. Please add usernames.")
        return

    with open(args.file, "r") as f:
        usernames = [line.strip().replace('@', '') for line in f if line.strip()]

    proxies = []
    if args.proxy and os.path.exists(args.proxy):
        with open(args.proxy, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]

    checker = XChecker(use_proxies=proxies)
    print(f"{Fore.CYAN}--- Starting X Checker (Workers: {args.workers}) ---")

    async with async_playwright() as p:
        # Launch with additional args to bypass detection
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        semaphore = asyncio.Semaphore(args.workers)

        async def worker(user):
            async with semaphore:
                name, res = await checker.check_username(browser, user)
                if res == "AVAILABLE":
                    print(f"{Fore.GREEN}[+] AVAILABLE: @{name}")
                elif res == "BLOCKED/LOGIN_REQUIRED":
                    print(f"{Fore.YELLOW}[!] BLOCKED/LOGIN WALL: @{name} (Use Proxies)")
                elif "TAKEN" in res:
                    print(f"{Fore.RED}[-] TAKEN: @{name}")
                else:
                    print(f"{Fore.WHITE}[?] {res}: @{name}")
                return name, res

        tasks = [worker(u) for u in usernames]
        results = await tqdm.gather(*tasks, desc="Checking")
        await browser.close()

    available = [n for n, r in results if r == "AVAILABLE"]
    print(f"\n{Fore.MAGENTA}=== FINAL RESULTS ===")
    print(f"Total: {len(results)} | Available: {len(available)}")
    if available: print(f"Available usernames saved to available_found.txt")

if __name__ == "__main__":
    asyncio.run(main())
