"""F12: checkout gating, validation and order review; no final order/payment."""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Scenario T012-S1: a fresh empty cart must redirect away from checkout.
@pytest.mark.scenario('T012-S1')
def test_empty_cart_cannot_checkout(shop):
    shop.open('checkout/checkout')
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert 'checkout/cart' in shop.driver.current_url
    content = shop.driver.find_element(By.ID, 'content')
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert 'Your shopping cart is empty!' in content.text
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert not content.find_elements(By.CSS_SELECTOR, 'table tbody tr')

# Scenario T012-S2: incomplete guest details must display errors and prevent final confirmation.
@pytest.mark.scenario('T012-S2')
def test_guest_required_fields(shop):
    shop.guest_form()
    # Save the actual browser state as evidence for this scenario.
    shop.capture('empty-required-fields')
    shop.click('#button-guest')
    shop.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#collapse-payment-address .text-danger')))
    errors = shop.driver.find_elements(By.CSS_SELECTOR, '#collapse-payment-address .text-danger')
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert len([e for e in errors if e.is_displayed()]) >= 3
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert shop.driver.find_element(By.ID, 'input-payment-firstname').is_displayed()
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert not any((e.is_displayed() for e in shop.driver.find_elements(By.ID, 'button-confirm')))

# Scenario T012-S3: progress through guest checkout and stop at review without placing an order.
@pytest.mark.scenario('T012-S3')
def test_valid_guest_reaches_review_without_order(shop):
    shop.guest_form()
    # The shared helper waits for dynamically refreshed country/region options.
    shop.complete_guest()
    shop.wait.until(lambda d: any((e.is_displayed() for e in d.find_elements(By.CSS_SELECTOR, '#collapse-shipping-method input[name="shipping_method"], #collapse-shipping-method .alert-danger'))))
    methods = [e for e in shop.driver.find_elements(By.CSS_SELECTOR, '#collapse-shipping-method input[name="shipping_method"]') if e.is_displayed()]
    if not methods:
        # Save the actual browser state as evidence for this scenario.
        shop.capture('shipping-unavailable')
        # Missing delivery/payment configuration blocks execution; it is not a passing result.
        pytest.skip('BLOCKED: no shipping method for the test address.')
    methods[0].click()
    # Save the actual browser state as evidence for this scenario.
    shop.capture('shipping-method')
    shop.click('#button-shipping-method')
    shop.wait.until(lambda d: any((e.is_displayed() for e in d.find_elements(By.CSS_SELECTOR, '#collapse-payment-method input[name="payment_method"], #collapse-payment-method .alert-danger'))))
    payments = [e for e in shop.driver.find_elements(By.CSS_SELECTOR, '#collapse-payment-method input[name="payment_method"]') if e.is_displayed()]
    if not payments:
        # Save the actual browser state as evidence for this scenario.
        shop.capture('payment-unavailable')
        # Missing delivery/payment configuration blocks execution; it is not a passing result.
        pytest.skip('BLOCKED: no configured payment method.')
    payments[0].click()
    agree = shop.driver.find_element(By.CSS_SELECTOR, '#collapse-payment-method input[name="agree"]')
    if not agree.is_selected():
        agree.click()
    # Save the actual browser state as evidence for this scenario.
    shop.capture('payment-method')
    shop.click('#button-payment-method')
    shop.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#collapse-checkout-confirm table')))
    review = shop.driver.find_element(By.ID, 'collapse-checkout-confirm')
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert 'iPhone' in review.text and 'Total' in review.text
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert 'checkout/success' not in shop.driver.current_url
    # Save the actual browser state as evidence for this scenario.
    shop.capture('order-review-not-submitted')

# Safety boundary: never click button-confirm or execute a payment confirmation endpoint.
