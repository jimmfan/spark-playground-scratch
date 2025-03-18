# Python Attachment Downloader Documentation

## Overview

This script automates the process of downloading attachments from an internally hosted website using Playwright's synchronous API. It navigates the site, performs a search, and downloads a subset of attachments found within an iframe. The code serves as a template that can be extended or customized for similar web automation tasks.

## Purpose

- **Automate Attachment Retrieval:** Streamline the process of accessing and downloading attachments from a web portal.
- **Reduce Manual Effort:** Replace manual interactions with scripted actions, saving time and reducing the risk of human error.
- **Template for Customization:** Provide a base implementation that can be modified to accommodate different websites, search terms, or download criteria.

## Prerequisites

Before running the script, ensure you have:

- **Python 3.x** installed.
- **Playwright for Python** installed, along with the required browsers:

  ```bash
  pip install playwright
  playwright install
  ```

- **Network access and permissions** to the internally hosted website and download directories.
- Basic familiarity with Python and web automation concepts.

## Setup

1. **Download Directory:**  
   The script uses `/tmp/playwright_downloads` as the download directory. This directory is created if it does not exist.

2. **Playwright Context:**  
   The script launches a persistent Chromium browser context with downloads accepted.

## Process Flow

1. **Initialization:**
   - Import necessary modules (`time`, `re`, `os`, and `Playwright`).
   - Set up the download directory.

2. **Browser Launch and Navigation:**
   - Start a persistent Chromium context.
   - Open a new page and navigate to the target website (e.g., `https://examplesite.com`).

3. **Search Operation:**
   - Click on the "Search" button.
   - Focus on the search textbox (using a Control/Meta key modifier).
   - Fill in the search term and submit the search.
   - Filter the search results using a regular expression and click the corresponding button.

4. **Iframe and Attachment Interaction:**
   - Wait for the iframe containing attachments to load.
   - Retrieve the iframe (selecting the first frame with a name) and extract its name.
   - Wait briefly (using `time.sleep`) to ensure that the document names within the frame are fully loaded.

5. **Attachment Download:**
   - Extract document names from the iframe by locating anchor tags with a `Type=Attachment` parameter.
   - Iterate over a limited number of document names (for testing purposes).
   - For each document:
     - Expect a download and a popup triggered by clicking the attachment link.
     - Save the downloaded file to the specified download directory using the suggested filename.
