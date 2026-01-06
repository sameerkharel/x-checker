# x-checker
A high-performance, asynchronous tool for checking X.com username availability at scale using Playwright.

🚀 Key Features

Asynchronous Engine: Built on Playwright for fast, multi-threaded browser automation.

Proxy Rotation: Support for HTTP/SOCKS5 proxies to bypass IP-based rate limiting.

Bulk Processing: Check thousands of handles from a text file.

Auto-Export: Automatically saves available handles to available_found.txt.

Stealth Mode: Randomized User-Agents and human-like interaction delays.

🛠️ Installation

Clone the repo:

git clone [https://github.com/yourusername/x-checker.git](https://github.com/yourusername/x-checker.git)
cd x-checker


Install Dependencies:

pip install -r requirements.txt
playwright install chromium


📖 Usage

Bulk Check

Place your usernames in usernames.txt (one per line) and run:

python checker.py --file usernames.txt --workers 5


With Proxies

Add proxies to proxies.txt (http://user:pass@host:port) and run:

python checker.py --file usernames.txt --proxy proxies.txt


⚠️ Disclaimer

This tool is for educational purposes only. Use it responsibly and in compliance with X's Terms of Service.
