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

    page.wait_for_timeout(5000)

    print("\n===== ALL INPUTS =====\n")

    inputs = page.locator("input")

    for i in range(inputs.count()):
        try:
            print(
                i,
                inputs.nth(i).get_attribute("type"),
                inputs.nth(i).get_attribute("value")
            )
        except:
            pass

    print("\n===== ALL BUTTONS =====\n")

    buttons = page.locator("button")

    for i in range(buttons.count()):
        try:
            print(i, buttons.nth(i).inner_text())
        except:
            pass

    input("\nPress Enter to close...")

    browser.close()