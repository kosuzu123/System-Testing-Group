
# =====================================================
# Assignment 3 - Member B: Chuyu Liang
# T005 - Product Filtering
# Website: OpenCart Demo Store
# Tool: Python + Selenium + pytest
# =====================================================

import re
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# =====================================================
# Test Environment
# =====================================================

HOME_URL = "https://opencart.abstracta.us/"

EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)

SCREENSHOTS = {
    "test_T005_S1_cameras_category":
        "T005_S1_Automated_Result.png",

    "test_T005_S2_apple_brand":
        "T005_S2_Automated_Result.png",

    "test_T005_S3_empty_software_category":
        "T005_S3_Automated_Result.png",
}


# =====================================================
# Browser Setup and Screenshot Saving
# =====================================================

@pytest.fixture
def driver(request):

    # Open Google Chrome
    browser = webdriver.Chrome()
    browser.maximize_window()

    try:
        yield browser

    finally:
        # Save screenshot even if an assertion fails
        screenshot = EVIDENCE_DIR / SCREENSHOTS.get(
            request.node.name,
            f"{request.node.name}.png"
        )

        try:
            browser.save_screenshot(str(screenshot))
            print(f"Evidence screenshot: {screenshot}")

        except Exception as exc:
            print(f"Could not save screenshot: {exc}")

        # Close browser
        browser.quit()


# =====================================================
# Helper 1: Verify Page Heading
# =====================================================

def wait_for_heading(driver, expected):

    wait = WebDriverWait(driver, 20)

    wait.until(
        lambda d: any(
            element.is_displayed()
            and element.text.strip() == expected
            for element in d.find_elements(
                By.CSS_SELECTOR,
                "#content h1, #content h2"
            )
        )
    )

    print(f"Page heading verified: {expected}")


# =====================================================
# Helper 2: Open Product Category
# =====================================================

def open_category(driver, category):

    driver.get(HOME_URL)

    wait = WebDriverWait(driver, 20)

    # Locate the category in the navigation menu
    category_link = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//nav[@id='menu']//a"
                f"[normalize-space()='{category}']"
            )
        )
    )

    # Open the selected category
    category_link.click()

    # Verify page heading
    wait_for_heading(driver, category)

    print(f"Category URL: {driver.current_url}")


# =====================================================
# Helper 3: Extract Visible Product Names
# =====================================================

def visible_product_names(driver):

    cards = driver.find_elements(
        By.CSS_SELECTOR,
        "#content .product-thumb"
    )

    names = []

    for card in cards:

        if card.is_displayed():

            name = card.find_element(
                By.CSS_SELECTOR,
                "h4 a"
            ).text.strip()

            names.append(name)

    return names


# =====================================================
# T005 - Scenario 1
# Filter Products by Category (Cameras)
# =====================================================

def test_T005_S1_cameras_category(driver):

    # Step 1: Open Cameras category
    open_category(driver, "Cameras")

    # Step 2: Wait for product listings
    names = WebDriverWait(driver, 20).until(
        lambda d: visible_product_names(d) or False
    )

    print("Cameras products:", names)

    # Step 3: Verify expected camera products
    assert "Canon EOS 5D" in names, (
        "FAIL: Canon EOS 5D was not displayed."
    )

    assert "Nikon D300" in names, (
        "FAIL: Nikon D300 was not displayed."
    )

    # Step 4: Verify unrelated products are absent
    assert "MacBook" not in names, (
        "FAIL: MacBook appeared in Cameras category."
    )

    assert "iPhone" not in names, (
        "FAIL: iPhone appeared in Cameras category."
    )

    # Step 5: Verify visible product prices
    cards = driver.find_elements(
        By.CSS_SELECTOR,
        "#content .product-thumb"
    )

    for card in cards:

        if card.is_displayed():

            title = card.find_element(
                By.CSS_SELECTOR,
                "h4 a"
            ).text.strip()

            price = card.find_element(
                By.CSS_SELECTOR,
                ".price"
            ).text.strip()

            # Check that a price is displayed
            assert re.search(
                r"\$\s*[\d,]+(?:\.\d{2})?",
                price
            ), (
                f"FAIL: A visible price was not found "
                f"for {title}."
            )

            print(
                f"Verified: {title} | "
                f"{price.splitlines()[0]}"
            )

    print(
        "PASS: Cameras category displayed "
        "the expected products."
    )


# =====================================================
# T005 - Scenario 2
# Filter Products by Brand (Apple)
# =====================================================

def test_T005_S2_apple_brand(driver):

    # Step 1: Open homepage
    driver.get(HOME_URL)

    wait = WebDriverWait(driver, 20)

    # Step 2: Click Brands in the footer
    brands_link = wait.until(
        EC.element_to_be_clickable(
            (By.LINK_TEXT, "Brands")
        )
    )

    brands_link.click()

    # Step 3: Verify the manufacturer list page
    wait_for_heading(
        driver,
        "Find Your Favorite Brand"
    )

    # Step 4: Select Apple
    apple_link = wait.until(
        EC.element_to_be_clickable(
            (By.LINK_TEXT, "Apple")
        )
    )

    apple_link.click()

    # Step 5: Verify Apple brand page
    wait_for_heading(driver, "Apple")

    # Step 6: Extract displayed products
    names = wait.until(
        lambda d: visible_product_names(d) or False
    )

    print("Apple products:", names)

    # Step 7: Verify expected products
    for expected in ("iMac", "iPhone", "MacBook"):

        assert expected in names, (
            f"FAIL: {expected} was not listed "
            "under the Apple brand."
        )

    # Save Apple brand listing screenshot
    brand_screenshot = (
        EVIDENCE_DIR /
        "T005_S2_Apple_Brand_List.png"
    )

    driver.save_screenshot(str(brand_screenshot))

    print(
        f"Apple brand list screenshot: "
        f"{brand_screenshot}"
    )

    # Step 8: Open the iMac product details
    imac_link = wait.until(
        EC.element_to_be_clickable(
            (By.LINK_TEXT, "iMac")
        )
    )

    imac_link.click()

    # Step 9: Verify iMac page
    wait_for_heading(driver, "iMac")

    # Step 10: Extract product information
    details = driver.find_element(
        By.ID,
        "content"
    ).text

    print("iMac product details:", details[:500])

    # Step 11: Verify manufacturer is Apple
    assert re.search(
        r"\bBrands?\s*:?\s*Apple\b",
        details,
        re.IGNORECASE
    ), (
        "FAIL: The iMac detail page "
        "did not show Apple as the brand."
    )

    print(
        "PASS: Apple brand listing and "
        "iMac brand information were verified."
    )


# =====================================================
# T005 - Scenario 3
# Filter Products by an Empty Category (Software)
# =====================================================

def test_T005_S3_empty_software_category(driver):

    # Step 1: Open Software category
    open_category(driver, "Software")

    # Step 2: Get displayed product names
    names = visible_product_names(driver)

    # Step 3: Get page content
    content = driver.find_element(
        By.ID,
        "content"
    ).text

    print("Software products:", names)
    print("Software page content:", content[-400:])

    # Step 4: Verify no products are displayed
    assert not names, (
        "FAIL: Unexpected products were "
        "displayed in Software category."
    )

    # Step 5: Look for a relevant empty-category message
    has_relevant_message = bool(
        re.search(
            r"\b(?:no products|no items|no results|"
            r"nothing found|no matching products|"
            r"no products available)\b",
            content,
            re.IGNORECASE
        )
    )

    # Step 6: Detect unrelated shopping cart message
    has_wrong_cart_message = (
        "your shopping cart is empty"
        in content.casefold()
    )

    print(
        "Relevant empty-category message:",
        has_relevant_message
    )

    print(
        "Unrelated shopping-cart message:",
        has_wrong_cart_message
    )

    # Step 7: Verify correct feedback
    assert (
        has_relevant_message
        and not has_wrong_cart_message
    ), (
        "FAIL - Possible website UI defect: "
        "The Software category contains no products, "
        "but an appropriate empty-category message "
        "was not displayed. "
        f"Shopping-cart message present: "
        f"{has_wrong_cart_message}."
    )

    print(
        "PASS: Empty Software category "
        "displayed a relevant message."
    )
