# T003 verifies logout from different pages and blocks account access afterward.
import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_T003_S1_logout_from_account():
    # Sign in, then use the account menu to log out.
    driver = webdriver.Chrome()
    try:
        driver.get(
            "https://opencart.abstracta.us/index.php?route=account/login"
        )
        driver.find_element(By.NAME, "email").send_keys(
            os.environ["TEST_EMAIL"]
        )
        driver.find_element(By.NAME, "password").send_keys(
            os.environ["TEST_PASSWORD"]
        )
        driver.find_element(
            By.CSS_SELECTOR, "input[value='Login']"
        ).click()
        WebDriverWait(driver, 15).until(
            EC.url_contains("route=account/account")
        )

        driver.find_element(
            By.CSS_SELECTOR, "a[title='My Account']"
        ).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
        ).click()
        # The logout page must confirm that the session ended.
        WebDriverWait(driver, 15).until(
            EC.url_contains("route=account/logout")
        )
        assert "You have been logged off your account." in (
            driver.find_element(By.TAG_NAME, "body").text
        )

        Path("evidence").mkdir(exist_ok=True)
        driver.save_screenshot("evidence/T003_S1_logout.png")
    finally:
        driver.quit()

def test_T003_S2_account_redirect_after_logout():
    # A signed-out user should not reopen the account page directly.
    driver = webdriver.Chrome()
    try:
        driver.get(
            "https://opencart.abstracta.us/index.php?route=account/login"
        )
        driver.find_element(By.NAME, "email").send_keys(
            os.environ["TEST_EMAIL"]
        )
        driver.find_element(By.NAME, "password").send_keys(
            os.environ["TEST_PASSWORD"]
        )
        driver.find_element(
            By.CSS_SELECTOR, "input[value='Login']"
        ).click()
        WebDriverWait(driver, 15).until(
            EC.url_contains("route=account/account")
        )

        driver.find_element(
            By.CSS_SELECTOR, "a[title='My Account']"
        ).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
        ).click()
        WebDriverWait(driver, 15).until(
            EC.url_contains("route=account/logout")
        )
        # Attempt to revisit the protected account URL after logout.
        driver.get(
            "https://opencart.abstracta.us/index.php?route=account/account"
        )
        WebDriverWait(driver, 15).until(
            EC.url_contains("route=account/login")
        )
        assert driver.find_element(By.NAME, "email").is_displayed()

        Path("evidence").mkdir(exist_ok=True)
        driver.save_screenshot("evidence/T003_S2_login_redirect.png")
    finally:
        driver.quit()

def test_T003_S3_logout_from_home():
    # Check that the account menu can also log out from the home page.
    driver = webdriver.Chrome()
    try:
        driver.get(
            "https://opencart.abstracta.us/index.php?route=account/login"
        )
        driver.find_element(By.NAME, "email").send_keys(
            os.environ["TEST_EMAIL"]
        )
        driver.find_element(By.NAME, "password").send_keys(
            os.environ["TEST_PASSWORD"]
        )
        driver.find_element(
            By.CSS_SELECTOR, "input[value='Login']"
        ).click()
        WebDriverWait(driver, 15).until(
            EC.url_contains("route=account/account")
        )

        driver.get(
            "https://opencart.abstracta.us/index.php?route=common/home"
        )
        WebDriverWait(driver, 15).until(
            EC.url_contains("route=common/home")
        )

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[title='My Account']")
            )
        ).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
        ).click()

        WebDriverWait(driver, 15).until(
            EC.url_contains("route=account/logout")
        )
        # Confirm the same logged-off message as the account-page route.
        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "You have been logged off your account." in page_text

        Path("evidence").mkdir(exist_ok=True)
        driver.save_screenshot("evidence/T003_S3_home_logout.png")
    finally:
        driver.quit()
