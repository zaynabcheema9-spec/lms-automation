from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import re

# ========================
# CONFIG
# ========================
load_dotenv()

USERNAME = os.getenv("LMS_USERNAME")
PASSWORD = os.getenv("LMS_PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("Missing LMS_USERNAME or LMS_PASSWORD in .env")

BASE_DOWNLOAD_FOLDER = "Downloads"
os.makedirs(BASE_DOWNLOAD_FOLDER, exist_ok=True)

LOG_FILE = os.path.join(BASE_DOWNLOAD_FOLDER, "download_log.txt")


# ========================
# HELPERS
# ========================
def clean_filename(name: str) -> str:
    name = str(name)
    name = name.replace("Course name", "")
    name = re.sub(r'[\\/*?:"<>|\n\r]', " ", name)
    name = " ".join(name.split())
    return name.strip()


def load_completed():
    """Read log and skip already successful courses"""
    if not os.path.exists(LOG_FILE):
        return set()

    completed = set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "SUCCESS" in line:
                completed.add(line.split(" -> ")[0].strip())
    return completed


# ========================
# MAIN SCRIPT
# ========================
with sync_playwright() as p:

    import os
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Check if script is running on GitHub Actions
    is_github = os.getenv("GITHUB_ACTIONS") == "true"

    browser = p.chromium.launch(
        headless=is_github
    )

    page = browser.new_page()

    # Tumhara baki code yahan
    # page.goto(...)
    # ...

    browser.close()
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    print("Opening LMS...")

    page.goto(
        "https://lms.nust.edu.pk/portal/login/index.php",
        wait_until="networkidle"
    )

    print("Logging in...")

    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)
    page.press("#password", "Enter")

    page.wait_for_url("**/my/**", timeout=30000)

    print("✅ Login successful!")
    page.wait_for_timeout(3000)

    print("\nCollecting courses...")

    links = page.locator("a")
    courses = {}

    for i in range(links.count()):
        try:
            text = links.nth(i).inner_text().strip()
            href = links.nth(i).get_attribute("href")

            if text and href and "/course/view.php?id=" in href:
                text = clean_filename(text)
                courses[text] = href

        except:
            pass

    print(f"✅ Found {len(courses)} courses")

    completed = load_completed()

    with open(LOG_FILE, "a", encoding="utf-8") as log:

        for course_name, course_url in courses.items():

            if course_name in completed:
                print(f"⏭ Skipping already downloaded: {course_name}")
                continue

            print("\n" + "=" * 60)
            print("Processing:", course_name)

            try:
                match = re.search(r"id=(\d+)", course_url)

                if not match:
                    print("❌ Could not extract course ID")
                    log.write(f"{course_name} -> FAILED (No Course ID)\n")
                    continue

                course_id = match.group(1)

                # Make folder per course
                course_folder = os.path.join(BASE_DOWNLOAD_FOLDER, course_name)
                os.makedirs(course_folder, exist_ok=True)

                download_center_url = (
                    f"https://lms.nust.edu.pk/portal/"
                    f"local/downloadcenter/index.php?courseid={course_id}"
                )

                print("Opening Download Center...")

                page.goto(download_center_url, wait_until="networkidle")
                page.wait_for_timeout(2000)

                checkboxes = page.locator('input[type="checkbox"]')
                count = checkboxes.count()

                print(f"Resources found: {count}")

                if count == 0:
                    print("⚠ No downloadable resources")
                    log.write(f"{course_name} -> NO RESOURCES\n")
                    continue

                # select all
                for j in range(count):
                    try:
                        checkboxes.nth(j).check()
                    except:
                        pass

                print("Creating ZIP archive...")

                with page.expect_download(timeout=180000) as download_info:
                    page.locator(
                        'input[type="submit"][value="Create ZIP archive"]'
                    ).click()

                download = download_info.value

                save_path = os.path.join(
                    course_folder,
                    f"{clean_filename(course_name)}.zip"
                )

                download.save_as(save_path)

                print("✅ Downloaded")

                log.write(f"{course_name} -> SUCCESS\n")

            except Exception as e:
                print("❌ Failed:", str(e))
                log.write(f"{course_name} -> FAILED -> {str(e)}\n")

    print("\n🎉 ALL COURSES PROCESSED")
    print(f"Downloads saved in: {BASE_DOWNLOAD_FOLDER}")

    browser.close()
