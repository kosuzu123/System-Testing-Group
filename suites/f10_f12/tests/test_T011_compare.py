"""F11: identity, de-duplication and scoped removal in the comparison table."""
import pytest
from selenium.webdriver.common.by import By

# Scenario T011-S1: verify both product IDs, displayed names, and model labels.
@pytest.mark.scenario('T011-S1')
def test_compare_two_products(shop):
    shop.add_list('compare', 40)
    shop.add_list('compare', 41)
    shop.open('product/compare')
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert sorted(shop.comparison_ids()) == [40, 41]
    text = shop.driver.find_element(By.CSS_SELECTOR, '#content table').text.lower()
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert 'iphone' in text and 'imac' in text
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert 'product 11' in text and 'product 14' in text

# Scenario T011-S2: duplicate additions must not create another comparison column.
@pytest.mark.scenario('T011-S2')
def test_duplicate_comparison_product(shop):
    shop.add_list('compare', 40)
    shop.add_list('compare', 40)
    shop.open('product/compare')
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert shop.comparison_ids() == [40], 'One product must create one comparison column.'

# Scenario T011-S3: remove only the selected product and verify the remaining ID.
@pytest.mark.scenario('T011-S3')
def test_remove_one_comparison_product(shop):
    shop.add_list('compare', 40)
    shop.add_list('compare', 41)
    shop.open('product/compare')
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert sorted(shop.comparison_ids()) == [40, 41]
    # Save the actual browser state as evidence for this scenario.
    shop.capture('before-removal')
    shop.click('#content a[href*="remove=40"]')
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert shop.comparison_ids() == [41]
