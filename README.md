# x-checker
A high-performance, asynchronous tool for checking X.com username availability at scale using Playwright.

🚀 Key Features

1. Asynchronous Engine: Built on Playwright for fast, multi-threaded browser automation.

2. Proxy Rotation: Support for HTTP/SOCKS5 proxies to bypass IP-based rate limiting.

3. Bulk Processing: Check thousands of handles from a text file.

4. Auto-Export: Automatically saves available handles to available_found.txt.

5. Stealth Mode: Randomized User-Agents and human-like interaction delays.

🛠️ Installation

1. Clone the repo:

git clone [https://github.com/yourusername/x-checker.git](https://github.com/yourusername/x-checker.git)
cd x-checker


2. Install Dependencies:

pip install -r requirements.txt

playwright install chromium


📖 Usage

1. Bulk Check

2. Place your usernames in usernames.txt (one per line) and run:

3. python checker.py --file usernames.txt --workers 5


With Proxies

1. Add proxies to proxies.txt (http://user:pass@host:port) and run:

2. python checker.py --file usernames.txt --proxy proxies.txt


⚠️ Disclaimer

This tool is for educational purposes only. Use it responsibly and in compliance with X's Terms of Service.
