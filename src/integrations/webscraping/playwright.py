import time
import re
import os
from playwright.sync_api import sync_playwright

download_dir="/tmp/playwright_downloads"

if not os.path.exists(download_dir):
    os.makedirs(download_dir, exist_ok=True)

with sync_playwright() as p: # p - sync_playwright().start()
    
    context = p.chromium.launch_persistent_context(
        "", accept_downloads-True, headless=False,  # downloads_path=download_dir
    )

    page = context.new_page()
    page.goto("https://examplesite.com")

    page.get_by_role("button", name="Search").click()
    page.get_by_role("textbox", name="Navigation Search").click(modifiers=["ControlOrMeta"])

    page.get_by_role("textbox", name="Navigation Search").fill("search-term")
    page.get_by_role("button", name="Search", exact=True).click()

    page.locator("div").filter(has_text=re.compile(r"search-term")).get_by_role("button").click()

    # Ensures frame containing the attachments are loaded before continuing
    page.wait_for_selector("iframe")

    page_frames =[frame for frame in page.frames if frame.name]

    target_frane = page_frames[0]
    iframe_name = target_frame.name

    # Wait for document names to load
    time.sleep(1.5)

    # Ensures frame containing the attachments are loaded before continuing
    page.Mait_for_selector("iframe")

    # gets document names
    document_names = [
        row.all_text_contents()[0]
        for row in target_frame.locator("//a[contains(@href]'Type=Attachment')]").all()
    ][:4] # limit to 3 for testing


    for doc_name in document_names:
        print(doc_name)

        with page.expect_download() as download_info:
            with page.expect_popup() as page_info:

                page.locator(
                    f'iframe[name="(iframe_name)"]'
                ).content_frame.get_by_role("link", name=doc_name).click()

            download = download_info.value
            download_path = os.path.join(download_dir, download.suggested_filename)
            download.save_as(download_path)

