from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os

load_dotenv()

DOWNLOAD_FOLDER = "Downloads"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    context = browser.new_context(
        accept_downloads=True
    )

    page = context.new_page()

    page.goto("https://lms.nust.edu.pk/portal/login/index.php")

    page.fill("#username", os.getenv("LMS_USERNAME"))
    page.fill("#password", os.getenv("LMS_PASSWORD"))

    page.press("#password", "Enter")

    page.wait_for_url("**/my/**")

    page.goto(
        "https://lms.nust.edu.pk/portal/local/downloadcenter/index.php?courseid=57604"
    )

    page.wait_for_timeout(5000)

    checkboxes = page.locator('input[type="checkbox"]')

    for i in range(checkboxes.count()):
        checkboxes.nth(i).check()

    print("All resources selected")

    with page.expect_download() as download_info:

        page.locator(
            'input[type="submit"][value="Create ZIP archive"]'
        ).click()

    download = download_info.value

    filename = download.suggested_filename

    filepath = os.path.join(
        DOWNLOAD_FOLDER,
        filename
    )

    download.save_as(filepath)

    print("\nDownload complete!")
    print("Saved to:", filepath)

    input("\nPress Enter to close...")

    browser.close()