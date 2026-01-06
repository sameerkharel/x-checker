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
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    def get_proxy(self):
        if not self.proxies: return None
        return {"server": random.choice(self.proxies).strip()}

    async def check_username(self, browser, username):
        proxy = self.get_proxy()
        # Create a fresh context per check for better isolation
        context = await browser.new_context(
            user_agent=random.choice(self.user_agents),
            proxy=proxy if proxy else None
        )
        page = await context.new_page()
        url = f"https://x.com/{username}"
        
        status = "UNKNOWN"
        try:
            # Jitter to avoid bot detection
            await asyncio.sleep(random.uniform(1.0, 2.0))
            
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            if response and response.status == 404:
                status = "AVAILABLE"
            else:
                content = await page.content()
                if "This account doesn’t exist" in content:
                    status = "AVAILABLE"
                elif "Account suspended" in content:
                    status = "TAKEN (SUSPENDED)"
                elif "UserProfileHeader" in content or "Follow" in content:
                    status = "TAKEN"
                else:
                    status = "RATE_LIMITED"

            if status == "AVAILABLE":
                with open("available_found.txt", "a") as f:
                    f.write(f"{username}\n")

        except Exception:
            status = "ERROR/TIMEOUT"
        finally:
            await context.close()
            return username, status

async def main():
    parser = argparse.ArgumentParser(description="X Username Bulk Checker")
    parser.add_argument("--file", default="usernames.txt", help="File with usernames")
    parser.add_argument("--proxy", help="File with proxies")
    parser.add_argument("--workers", type=int, default=3, help="Concurrent workers")
    args = parser.parse_args()

    # Create empty usernames file if missing
    if not os.path.exists(args.file):
        with open(args.file, "w") as f: f.write("example_user_1\nexample_user_2")
        print(f"{Fore.YELLOW}[!] Created {args.file}. Please add usernames to it.")
        return

    with open(args.file, "r") as f:
        usernames = [line.strip().replace('@', '') for line in f if line.strip()]

    proxies = []
    if args.proxy and os.path.exists(args.proxy):
        with open(args.proxy, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]

    checker = XChecker(use_proxies=proxies)
    
    print(f"{Fore.CYAN}--- Starting X Checker ({len(usernames)} targets) ---")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        semaphore = asyncio.Semaphore(args.workers)

        async def worker(user):
            async with semaphore:
                name, res = await checker.check_username(browser, user)
                if res == "AVAILABLE":
                    print(f"{Fore.GREEN}[+] AVAILABLE: @{name}")
                elif "TAKEN" in res:
                    print(f"{Fore.RED}[-] TAKEN: @{name}")
                else:
                    print(f"{Fore.YELLOW}[?] {res}: @{name}")
                return name, res

        tasks = [worker(u) for u in usernames]
        results = await tqdm.gather(*tasks, desc="Checking")
        await browser.close()

    # Final Statistics
    available = [n for n, r in results if r == "AVAILABLE"]
    print(f"\n{Fore.MAGENTA}==============================")
    print(f"{Fore.WHITE}Total Processed: {len(results)}")
    print(f"{Fore.GREEN}Available Found: {len(available)}")
    print(f"{Fore.WHITE}Saved to: available_found.txt")
    print(f"{Fore.MAGENTA}=============================={Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(main())
