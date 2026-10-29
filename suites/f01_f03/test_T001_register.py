# T001 checks required fields, password confirmation, and successful registration.
from uuid import uuid4
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_T001_S1_empty_registration():
    # Submit the blank form to trigger required-field validation.
    driver = webdriver.Chrome()
    try:
        driver.get(
            "https://opencart.abstracta.us/index.php?route=account/register"
        )
        driver.find_element(
            By.CSS_SELECTOR, "input[value='Continue']"
        ).click()

        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"),
                "First Name must be between 1 and 32 characters!",
            )
        )
        # Confirm that validation appears without leaving the registration page.
        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "E-Mail Address does not appear to be valid!" in page_text
        assert "route=account/register" in driver.current_url

        Path("evidence").mkdir(exist_ok=True)
        driver.save_screenshot("evidence/T001_S1_empty.png")
    finally:
        driver.quit()

def test_T001_S2_password_mismatch():
    # Use a unique email so this negative test cannot conflict with an old account.
    driver = webdriver.Chrome()
    try:
        driver.get(
            "https://opencart.abstracta.us/index.php?route=account/register"
        )

        test_email = f"mismatch.{uuid4().hex[:8]}@example.com"
        details = {
            "firstname": "Test",
            "lastname": "User",
            "email": test_email,
            "telephone": "0400000000",
            "password": "Testing2026!",
            "confirm": "Different2026!",
        }
        for field_name, value in details.items():
            driver.find_element(By.NAME, field_name).send_keys(value)

        driver.find_element(By.NAME, "agree").click()
        driver.find_element(
            By.CSS_SELECTOR, "input[value='Continue']"
        ).click()
        # A mismatched confirmation must block registration.
        error = "Password confirmation does not match password!"
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), error)
        )
        assert "route=account/register" in driver.current_url

        Path("evidence").mkdir(exist_ok=True)
        driver.save_screenshot("evidence/T001_S2_mismatch.png")
    finally:
        driver.quit()

def test_T001_S3_valid_registration():
    # Create a new account with matching passwords and privacy consent.
    driver = webdriver.Chrome()
    try:
        driver.get(
            "https://opencart.abstracta.us/index.php?route=account/register"
        )

        test_email = f"registration.{uuid4().hex[:12]}@example.com"
        test_password = "Testing2026!"
        details = {
            "firstname": "Test",
            "lastname": "User",
            "email": test_email,
            "telephone": "0400000000",
            "password": test_password,
            "confirm": test_password,
        }
        for field_name, value in details.items():
            driver.find_element(By.NAME, field_name).send_keys(value)

        driver.find_element(By.NAME, "agree").click()
        driver.find_element(
            By.CSS_SELECTOR, "input[value='Continue']"
        ).click()
         # Verify the success message and the account-success route.
        success_message = "Your new account has been successfully created!"
        WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"), success_message
            )
        )
        assert "route=account/success" in driver.current_url

        Path("evidence").mkdir(exist_ok=True)
        driver.save_screenshot("evidence/T001_S3_success.png")
        print(f"TEST_EMAIL={test_email}")
    finally:
        driver.quit()
