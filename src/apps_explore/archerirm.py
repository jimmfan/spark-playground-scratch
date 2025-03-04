from playwright.sync_api import sync_playwright

def download_archer_attachments():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set True for background execution
        page = browser.new_page()

        # Navigate to some login page
        page.goto("https://some-url.com/login")

        # Login
        page.fill("#username", "your_username")  # Adjust selector if needed
        page.fill("#password", "your_password")
        page.click("#login-button")  # Adjust as necessary

        # Navigate to the attachments page
        page.goto("https://some-url.com/attachments")
        page.wait_for_selector("table")  # Ensure the table loads

        # Locate the first row to find the "Name" column dynamically
        headers = page.locator("table tbody tr:first-child td").all_text_contents()
        print(f"Table Headers: {headers}")  # Debugging output
        
        # Find the index of the "Name" column
        name_column_index = headers.index("Name") + 1  # Convert to 1-based index for nth-child()

        # Locate all cells under the "Name" column
        name_cells = page.locator(f"table tbody tr:not(:first-child) td:nth-child({name_column_index})").all()

        print(f"Found {len(name_cells)} attachments.")

        for idx, cell in enumerate(name_cells):
            with page.expect_download() as download_info:
                cell.click()  # Click the "Name" cell to trigger download
            
            download = download_info.value
            file_path = f"downloaded_attachment_{idx+1}.pdf"
            download.save_as(file_path)
            print(f"Downloaded: {file_path}")

        browser.close()

# Run the function
download_archer_attachments()