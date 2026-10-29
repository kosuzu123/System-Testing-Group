
import re
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Assignment 3 - Member B
# T004: Product Search
# Website: OpenCart Demo Store

HOME_URL = "https://opencart.abstracta.us/"

EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)

SCREENSHOT_NAMES = {
    "test_T004_S1_valid_product_search": "T004_S1_Automated_Result.png",
    "test_T004_S2_nonexistent_keyword": "T004_S2_Automated_Result.png",
    "test_T004_S3_empty_keyword": "T004_S3_Automated_Result.png",
}


@pytest.fixture
def driver(request):
    """
    Create Chrome for each test.
    Save a screenshot even if the test fails.
    """
    browser = webdriver.Chrome()

    try:
        browser.maximize_window()
        yield browser

    finally:
        screenshot = EVIDENCE_DIR / SCREENSHOT_NAMES.get(
            request.node.name,
            f"{request.node.name}.png"
        )

        try:
            browser.save_screenshot(str(screenshot))
            print(f"Evidence screenshot: {screenshot}")

        except Exception as exc:
            print(f"Could not save screenshot: {exc}")

        browser.quit()


def submit_search(driver, keyword):
    """
    Open the homepage, enter a keyword,
    and submit the search.
    """
    wait = WebDriverWait(driver, 20)

    driver.get(HOME_URL)

    search_box = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#search input[name='search']")
        )
    )

    search_box.clear()

    if keyword:
        search_box.send_keys(keyword)

    search_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#search button")
        )
    )

    search_button.click()

    heading = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#content h1")
        )
    )

    wait.until(
        lambda d: "search" in d.current_url.lower()
    )

    print(f"Search keyword: {keyword!r}")
    print(f"Results URL: {driver.current_url}")
    print(f"Page heading: {heading.text}")

    return heading.text.strip()


def visible_product_cards(driver):
    """
    Find visible product cards on the results page.
    """
    cards = driver.find_elements(
        By.CSS_SELECTOR,
        "#content .product-thumb"
    )

    return [
        card for card in cards
        if card.is_displayed()
    ]


# =====================================================
# T004 - Scenario 1
# Valid Product Keyword Search
# Test Data: MacBook
# =====================================================

def test_T004_S1_valid_product_search(driver):

    # Step 1: Search for MacBook
    heading = submit_search(driver, "MacBook")

    # Step 2: Verify the search heading
    assert heading == "Search - MacBook", (
        f"Unexpected heading: {heading}"
    )

    # Step 3: Wait for product listings
    cards = WebDriverWait(driver, 20).until(
        lambda d: visible_product_cards(d) or False
    )

    matched_names = []

    # Step 4: Check matching product names and prices
    for card in cards:

        title = card.find_element(
            By.CSS_SELECTOR,
            "h4 a"
        ).text.strip()

        if "macbook" not in title.casefold():
            continue

        price_text = card.find_element(
            By.CSS_SELECTOR,
            ".price"
        ).text

        assert re.search(
            r"\$\s*[\d,]+(?:\.\d{2})?",
            price_text
        ), (
            f"No visible price for {title}: "
            f"{price_text!r}"
        )

        matched_names.append(title)

        print(
            f"Matching product: {title} | "
            f"{price_text.splitlines()[0]}"
        )

    # Step 5: Verify at least one matching product
    assert matched_names, (
        "No matching MacBook products "
        "with visible prices found."
    )

    print(
        f"PASS: Found {len(matched_names)} "
        "matching product(s)."
    )


# =====================================================
# T004 - Scenario 2
# Search with a Non-existent Keyword
# Test Data: zzzxxyy998877
# =====================================================

def test_T004_S2_nonexistent_keyword(driver):

    keyword = "zzzxxyy998877"

    # Step 1: Search for a non-existent product
    heading = submit_search(driver, keyword)

    # Step 2: Verify the heading
    assert heading == f"Search - {keyword}", (
        f"Unexpected heading: {heading}"
    )

    # Step 3: Check product listings and page text
    cards = visible_product_cards(driver)

    content = driver.find_element(
        By.ID,
        "content"
    ).text

    print(f"Visible product cards: {len(cards)}")
    print("Observed results text:", content[-350:])

    # Step 4: Verify no products were returned
    assert not cards, (
        "Unexpected products were returned "
        "for a non-existent keyword."
    )

    # Step 5: Verify the no-results message
    assert re.search(
        r"no products?|no matching products?|"
        r"no results|does not match|"
        r"did not match|nothing found|not found",
        content,
        re.IGNORECASE
    ), (
        "FAIL - Possible website defect: "
        "No relevant no-results message was displayed. "
        "The page may show "
        "'Your shopping cart is empty!' instead."
    )

    print(
        "PASS: An appropriate no-results "
        "message is displayed."
    )


# =====================================================
# T004 - Scenario 3
# Search with an Empty Keyword
# Test Data: Empty String
# =====================================================

def test_T004_S3_empty_keyword(driver):

    # Step 1: Submit an empty search
    heading = submit_search(driver, "")

    # Step 2: Verify the search page loads
    assert heading == "Search", (
        f"Unexpected empty-search heading: {heading}"
    )

    # Step 3: Read the search results
    content = driver.find_element(
        By.ID,
        "content"
    ).text

    cards = visible_product_cards(driver)

    print(
        f"Visible products for empty search: "
        f"{len(cards)}"
    )

    print("Observed results text:", content[-350:])

    # Step 4: Verify a meaningful response
    # Showing products is acceptable.
    # Otherwise, a relevant search message is required.
    if not cards:

        assert re.search(
            r"no products?|no results|"
            r"enter (?:a |the )?keyword|"
            r"please enter|search term|required|"
            r"nothing found|no matching|does not match",
            content,
            re.IGNORECASE
        ), (
            "FAIL - Possible website defect: "
            "Empty search returned no products "
            "and no relevant search message. "
            "An unrelated shopping cart message "
            "may have been displayed."
        )

    print(
        "PASS: Empty search was handled "
        "with relevant feedback."
    )
