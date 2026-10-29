"""F10: add, duplicate and remove wishlist products using an isolated account."""
import pytest


# Authenticate with the isolated demo account and reset its wish list before each scenario.
def prepare(shop, account):
    shop.login(account)
    shop.clear_wishlist()

# Scenario T010-S1: add one product, verify its identity, capture evidence, then clean up.
@pytest.mark.scenario('T010-S1')
def test_add_wishlist_product(shop, account):
    prepare(shop, account)
    shop.add_list('wishlist', 40)
    shop.open('account/wishlist')
    rows = shop.wishlist_rows(40)
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert len(rows) == 1 and 'iPhone' in rows[0].text
    # Save the actual browser state as evidence for this scenario.
    shop.capture('added')
    shop.remove_wishlist(40)

# Scenario T010-S2: adding the same product twice must retain exactly one wishlist row.
@pytest.mark.scenario('T010-S2')
def test_duplicate_wishlist_product(shop, account):
    prepare(shop, account)
    shop.add_list('wishlist', 40)
    shop.add_list('wishlist', 40)
    shop.open('account/wishlist')
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert len(shop.wishlist_rows(40)) == 1, 'Duplicate addition must not create a second row.'
    # Save the actual browser state as evidence for this scenario.
    shop.capture('duplicate-single-row')
    shop.remove_wishlist(40)

# Scenario T010-S3: removing iPhone must preserve the unrelated iMac entry.
@pytest.mark.scenario('T010-S3')
def test_remove_one_wishlist_product(shop, account):
    prepare(shop, account)
    shop.add_list('wishlist', 40)
    shop.add_list('wishlist', 41)
    shop.open('account/wishlist')
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert len(shop.wishlist_rows(40)) == len(shop.wishlist_rows(41)) == 1
    # Save the actual browser state as evidence for this scenario.
    shop.capture('before-removal')
    shop.remove_wishlist(40)
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert not shop.wishlist_rows(40)
    # Check the expected outcome explicitly; a mismatch is reported as a test failure.
    assert len(shop.wishlist_rows(41)) == 1, 'The other product must remain.'
    # Save the actual browser state as evidence for this scenario.
    shop.capture('after-removal')
    shop.remove_wishlist(41)
