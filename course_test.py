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

    # Open ONE course
    page.goto("https://lms.nust.edu.pk/portal/course/view.php?id=57604")

    page.wait_for_timeout(5000)

    links = page.locator("a")

    print("\n===== COURSE LINKS =====\n")

    for i in range(links.count()):
        try:
            text = links.nth(i).inner_text().strip()
            href = links.nth(i).get_attribute("href")

            if href:
                print(text, "->", href)

        except:
            pass

    input("\nPress Enter to close...")

    browser.close()