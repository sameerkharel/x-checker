import asyncio
import argparse
import random
import os
import json
from playwright.async_api import async_playwright
from colorama import Fore, Style, init
from tqdm.asyncio import tqdm

init(autoreset=True)

class XChecker:
    def __init__(self, use_proxies=None):
        self.proxies = use_proxies if use_proxies else []
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ]

    def get_proxy(self):
        if not self.proxies: return None
        return {"server": random.choice(self.proxies).strip()}

    async def check_username(self, browser, username):
        proxy = self.get_proxy()
        context = await browser.new_context(
            user_agent=random.choice(self.user_agents),
            proxy=proxy if proxy else None
        )
        page = await context.new_page()
        
        # We use the 'intent/user' endpoint which is lighter and more reliable for checking existence
        url = f"https://x.com/intent/user?screen_name={username}"
        status = "UNKNOWN"
        
        try:
            # Random delay
            await asyncio.sleep(random.uniform(1.5, 3.0))
            
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            content = await page.content()

            # Logic check
            if "Log in to X" in content and "screen_name" not in content:
                status = "RATE_LIMITED (Login Wall)"
            
            # X shows "Account not found" or "This page doesn’t exist" on intent pages if available
            elif "Account not found" in content or "This page doesn’t exist" in content or response.status == 404:
                status = "AVAILABLE"
            
            # If we see the User ID or a "Follow" prompt for that specific user
            elif username.lower() in content.lower():
                status = "TAKEN"
            
            else:
                status = "TAKEN" # Default to taken if we see a valid response but no 404

            if status == "AVAILABLE":
                with open("available_found.txt", "a") as f:
                    f.write(f"{username}\n")

        except Exception:
            status = "TIMEOUT"
        finally:
            await context.close()
            return username, status

async def main():
    parser = argparse.ArgumentParser(description="X Username Bulk Checker")
    parser.add_argument("--file", default="usernames.txt", help="File with usernames")
    parser.add_argument("--proxy", help="File with proxies")
    parser.add_argument("--workers", type=int, default=1, help="Keep workers at 1-2 to avoid instant IP ban")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"{Fore.RED}[!] Create {args.file} first.")
        return

    with open(args.file, "r") as f:
        usernames = [line.strip().replace('@', '') for line in f if line.strip()]

    checker = XChecker(use_proxies=None) # Add proxies here if you have them

    async with async_playwright() as p:
        # Launching with specific arguments to look less like a bot
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        semaphore = asyncio.Semaphore(args.workers)

        async def worker(user):
            async with semaphore:
                name, res = await checker.check_username(browser, user)
                if res == "AVAILABLE":
                    print(f"{Fore.GREEN}[+] AVAILABLE: @{name}")
                elif "RATE_LIMITED" in res:
                    print(f"{Fore.YELLOW}[!] RATE LIMITED: @{name}")
                else:
                    print(f"{Fore.RED}[-] TAKEN: @{name}")
                return name, res

        tasks = [worker(u) for u in usernames]
        await tqdm.gather(*tasks, desc="Checking")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
