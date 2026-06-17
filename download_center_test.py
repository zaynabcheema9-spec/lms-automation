from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os

load_dotenv()

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto("https://lms.nust.edu.pk/portal/login/index.php")

    page.fill("#username", os.getenv("LMS_USERNAME"))
    page.fill("#password", os.getenv("LMS_PASSWORD"))

    page.press("#password", "Enter")

    page.wait_for_url("**/my/**")

    page.goto(
        "https://lms.nust.edu.pk/portal/local/downloadcenter/index.php?courseid=57604"
    )

    page.wait_for_timeout(8000)

    print(page.title())

    print("\n===== BUTTONS =====\n")

    buttons = page.locator("button")

    for i in range(buttons.count()):
        try:
            print(buttons.nth(i).inner_text())
        except:
            pass

    input("\nPress Enter to close...")

    browser.close()