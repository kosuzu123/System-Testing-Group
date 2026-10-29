
import re
from decimal import Decimal
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


# Assignment 3 - Member B: Chuyu Liang
# T006 - Product Sorting
# Website: OpenCart

CATEGORY_URL = (
    "https://opencart.abstracta.us/"
    "index.php?route=product/category&path=20"
)

EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)


# =====================================================
# Browser Setup
# =====================================================

@pytest.fixture
def driver():

    browser = webdriver.Chrome()
    browser.maximize_window()

    try:
        yield browser
    finally:
        browser.quit()


# =====================================================
# Helper 1 - Open Desktops Category
# =====================================================

def open_desktops(driver):

    driver.get(CATEGORY_URL)

    wait = WebDriverWait(driver, 20)

    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#content h2")
        )
    )

    heading = driver.find_element(
        By.CSS_SELECTOR,
        "#content h2"
    ).text.strip()

    assert heading == "Desktops", (
        f"Unexpected category: {heading}"
    )

    wait.until(
        EC.presence_of_element_located(
            (By.ID, "input-sort")
        )
    )

    wait.until(
        lambda d: len(
            d.find_elements(
                By.CSS_SELECTOR,
                "#content .product-thumb"
            )
        ) >= 2
    )


# =====================================================
# Helper 2 - Apply Sorting
# =====================================================

def apply_sort(driver, option):

    wait = WebDriverWait(driver, 20)

    dropdown = wait.until(
        EC.element_to_be_clickable(
            (By.ID, "input-sort")
        )
    )

    choices = [
        item.text.strip()
        for item in Select(dropdown).options
    ]

    assert option in choices, (
        f"Sort option not found: {option}. "
        f"Available options: {choices}"
    )

    Select(dropdown).select_by_visible_text(option)

    # Wait for the sorted page to load
    wait.until(
        lambda d: "sort=" in d.current_url.lower()
    )

    wait.until(
        lambda d: (
            Select(
                d.find_element(By.ID, "input-sort")
            ).first_selected_option.text.strip() == option
            and d.execute_script(
                "return document.readyState"
            ) == "complete"
        )
    )

    wait.until(
        lambda d: len(
            d.find_elements(
                By.CSS_SELECTOR,
                "#content .product-thumb"
            )
        ) >= 2
    )

    print(f"Selected sorting option: {option}")


# =====================================================
# Helper 3 - Extract Product Names and Prices
# =====================================================

def get_products(driver):

    products = []

    cards = driver.find_elements(
        By.CSS_SELECTOR,
        "#content .product-thumb"
    )

    for card in cards:

        if not card.is_displayed():
            continue

        name = card.find_element(
            By.CSS_SELECTOR,
            "h4 a"
        ).text.strip()

        price_text = card.find_element(
            By.CSS_SELECTOR,
            ".price"
        ).text

        # Get current selling price, not Ex Tax price
        match = re.search(
            r"\$\s*([\d,]+\.\d{2})",
            price_text
        )

        assert match, (
            f"No valid selling price for {name}"
        )

        price = Decimal(
            match.group(1).replace(",", "")
        )

        products.append((name, price))

    assert len(products) >= 2, (
        "Not enough products to test sorting."
    )

    return products


# =====================================================
# Helper 4 - Verify Product Count
# =====================================================

def check_all_products_visible(driver, products):

    text = driver.find_element(
        By.ID,
        "content"
    ).text

    match = re.search(
        r"Showing\s+1\s+to\s+(\d+)\s+of\s+"
        r"(\d+)\s+\((\d+)\s+Pages\)",
        text,
        re.IGNORECASE
    )

    assert match, (
        "Could not verify product count."
    )

    shown, total, pages = [
        int(value)
        for value in match.groups()
    ]

    assert pages == 1, (
        f"More than one page found: {pages}"
    )

    assert shown == total == len(products), (
        "The extracted product count does not "
        "match the displayed total."
    )

    print(
        f"Verified all {total} products on one page."
    )


# =====================================================
# Helper 5 - Save Screenshots
# =====================================================

def save_evidence(driver, scenario):

    # Capture first products and sorting dropdown
    driver.execute_script(
        "window.scrollTo(0, 150);"
    )

    top_path = (
        EVIDENCE_DIR /
        f"{scenario}_Automated_Top.png"
    )

    assert driver.save_screenshot(
        str(top_path)
    ), "Top screenshot could not be saved."

    # Capture remaining products and page count
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);"
    )

    bottom_path = (
        EVIDENCE_DIR /
        f"{scenario}_Automated_Bottom.png"
    )

    assert driver.save_screenshot(
        str(bottom_path)
    ), "Bottom screenshot could not be saved."

    print(f"Screenshot saved: {top_path.name}")
    print(f"Screenshot saved: {bottom_path.name}")


# =====================================================
# Helper 6 - Run and Validate Sorting
# =====================================================

def run_sort_test(
    driver,
    scenario,
    option,
    sort_type
):

    # Step 1 - Open the category
    open_desktops(driver)

    # Step 2 - Apply the required sorting
    apply_sort(driver, option)

    # Step 3 - Extract all visible products
    products = get_products(driver)

    # Step 4 - Verify all products are displayed
    check_all_products_visible(driver, products)

    # Step 5 - Save screenshots before assertions
    save_evidence(driver, scenario)

    # Step 6 - Print displayed product order
    print("Displayed product order:")

    for index, (name, price) in enumerate(
        products,
        start=1
    ):
        print(
            f"{index}. {name} - ${price:,.2f}"
        )

    # Step 7 - Validate sorting order
    if sort_type == "price_ascending":

        actual = [
            price for _, price in products
        ]

        expected = sorted(actual)

    elif sort_type == "price_descending":

        actual = [
            price for _, price in products
        ]

        expected = sorted(
            actual,
            reverse=True
        )

    elif sort_type == "name_ascending":

        actual = [
            name.casefold()
            for name, _ in products
        ]

        expected = sorted(actual)

    else:
        raise ValueError(
            f"Unknown sorting type: {sort_type}"
        )

    assert actual == expected, (
        f"FAIL: Incorrect {option} sorting.\n"
        f"Actual: {actual}\n"
        f"Expected: {expected}"
    )

    print(
        f"PASS: All {len(products)} products "
        f"were correctly sorted using {option}."
    )


# =====================================================
# T006 - Scenario 1
# Price (Low to High)
# =====================================================

def test_T006_S1_price_low_to_high(driver):

    run_sort_test(
        driver,
        "T006_S1",
        "Price (Low > High)",
        "price_ascending"
    )
# =====================================================
# T006 - Scenario 2
# Price (High to Low)
# =====================================================

def test_T006_S2_price_high_to_low(driver):

    run_sort_test(
        driver,
        "T006_S2",
        "Price (High > Low)",
        "price_descending"
    )
# =====================================================
# T006 - Scenario 3
# Name (A to Z)
# =====================================================

def test_T006_S3_name_a_to_z(driver):

    run_sort_test(
        driver,
        "T006_S3",
        "Name (A - Z)",
        "name_ascending"
    )
