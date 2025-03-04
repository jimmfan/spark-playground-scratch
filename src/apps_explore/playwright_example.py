from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Open some tool
    page.goto("https://some-url.com/login")

    # Automate login
    page.fill("#username", "your_username")
    page.fill("#password", "your_password")
    page.click("#login-button")
    
    # Navigate to documents page
    page.goto("https://some-url.com/documents")
    
    # Download document
    with page.expect_download() as download_info:
        page.click("xpath=//a[contains(@href, '.pdf')]")
    download = download_info.value
    download.save_as("document.pdf")

    browser.close()