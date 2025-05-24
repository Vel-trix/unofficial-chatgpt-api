from flask import Flask, jsonify
import asyncio
import logging
from pathlib import Path
from playwright.async_api import async_playwright

# --- Flask and Logging ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# --- Hardcoded Gmail credentials (ONLY FOR TESTING) ---
EMAIL = "isnamen892@gmail.com"
PASSWORD = "nameisname123"
COOKIE_PATH = Path("cookies.json")

# --- Main login logic ---
async def login_and_save_cookies():
    logging.info("Launching browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=str(COOKIE_PATH) if COOKIE_PATH.exists() else None)

        page = await context.new_page()
        await page.goto("https://accounts.google.com/signin/v2/identifier", timeout=60000)

        logging.info("Filling email...")
        await page.fill('input[type="email"]', EMAIL)
        await page.click('#identifierNext')
        await page.wait_for_timeout(2000)

        logging.info("Filling password...")
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('#passwordNext')

        try:
            await page.wait_for_url("https://myaccount.google.com/*", timeout=15000)
            logging.info("Login successful!")
        except Exception as e:
            logging.warning(f"Login likely failed: {e}")
            await browser.close()
            return False

        await context.storage_state(path=str(COOKIE_PATH))
        await browser.close()
        logging.info("Cookies saved.")
        return True

# --- Flask route ---
@app.route("/cookies", methods=["GET"])
def get_cookies():
    async def handle():
        if not COOKIE_PATH.exists():
            logging.info("No cookies file. Running login...")
            success = await login_and_save_cookies()
            if not success:
                return jsonify({"error": "Login failed"}), 401

        with open(COOKIE_PATH, "r") as f:
            cookies = f.read()
        return jsonify({"cookies": cookies})

    return asyncio.run(handle())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
