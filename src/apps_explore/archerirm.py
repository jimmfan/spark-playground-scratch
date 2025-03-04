from playwright.sync_api import sync_playwright

def download_some_attachments():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set True for headless execution
        page = browser.new_page()

        # Step 1: Navigate to some  login page
        page.goto("https://some-url.com/login")

        # Step 2: Perform login (update selectors if needed)
        page.fill("#username", "your_username")
        page.fill("#password", "your_password")
        page.click("#login-button")

        # Step 3: Wait for the page to fully load
        page.wait_for_load_state("networkidle")

        # Step 4: Ensure iframe exists and switch to it
        page.wait_for_selector("iframe")  # Wait for the iframe to load
        iframe = page.frame_locator("iframe")  # Adjust if iframe has a unique ID

        print("Switched to iframe.")

        # Step 5: Wait for master_content_rt inside the iframe
        iframe.wait_for_selector("#master_content_rt")
        print("✅ Found #master_content_rt inside iframe.")

        # Step 6: Locate the table inside the iframe
        table = iframe.locator("#master_tbl")

        # Step 7: Print table structure for debugging
        table_html = table.inner_html()
        print("Table HTML:", table_html[:1000])  # Print first 1000 characters for readability

        # Step 8: Dynamically find headers inside the table
        headers = table.locator("tr:first-child th, tr:first-child td").all_text_contents()
        print("Headers:", headers)

        # Step 9: Find the "Name" column index
        try:
            name_column_index = headers.index("Name") + 1  # Convert to 1-based index for nth-child
        except ValueError:
            print("❌ Error: 'Name' column not found!")
            browser.close()
            return

        # Step 10: Select all file names under "Name" column dynamically
        name_cells = table.locator(f"tbody tr td:nth-child({name_column_index})").all()

        print(f"📂 Found {len(name_cells)} attachments.")

        # Step 11: Click each row dynamically to trigger downloads
        for idx, cell in enumerate(name_cells):
            with page.expect_download() as download_info:
                cell.click()  # Click dynamically
            
            download = download_info.value
            file_path = f"downloaded_attachment_{idx+1}.pdf"
            download.save_as(file_path)
            print(f"✅ Downloaded: {file_path}")

        # Step 12: Close the browser
        browser.close()

# Run the function
download_some_attachments()
