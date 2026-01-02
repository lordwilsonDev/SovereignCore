import pytest
import os
from rekor_lite import RekorLite

# The name of the test database file
TEST_DB = "test_rekor.db"


@pytest.fixture
def rekor_db():
    """
    Pytest fixture to set up and tear down the RekorLite database for testing.
    This ensures each test runs with a fresh, clean database.
    """
    # Setup: Initialize RekorLite with a test-specific database file
    rekor = RekorLite(db_path=TEST_DB)

    # Yield the RekorLite instance to the test function
    yield rekor

    # Teardown: Clean up the database files after the test is complete
    # This prevents test data from leaking between runs.
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # RekorLite may create journal files, so we clean those up too.
    if os.path.exists(f"{TEST_DB}-shm"):
        os.remove(f"{TEST_DB}-shm")
    if os.path.exists(f"{TEST_DB}-wal"):
        os.remove(f"{TEST_DB}-wal")


def test_rekor_initialization(rekor_db: RekorLite):
    """
    Tests that the RekorLite database is initialized correctly.
    """
    assert rekor_db is not None
    stats = rekor_db.get_stats()
    # A new database should have 0 entries
    assert stats["entries"] == 0


def test_rekor_log_and_get_action(rekor_db: RekorLite):
    """
    Tests that logging an action correctly stores it and makes it retrievable.
    """
    # 1. Log a test action
    action = "test_action"
    data = "This is a test data payload."
    thermal_state = 1
    
    action_hash, merkle_root = rekor_db.log_action(action, data, thermal_state)

    # Check that the hashes are valid strings
    assert isinstance(action_hash, str) and len(action_hash) == 64
    assert isinstance(merkle_root, str) and len(merkle_root) == 64

    # 2. Verify stats are updated
    stats = rekor_db.get_stats()
    assert stats["entries"] == 1
    assert stats["merkle_root"] == merkle_root

    # 3. Retrieve the logged action by its hash
    retrieved_entry = rekor_db.get_entry(action_hash)
    
    assert retrieved_entry is not None
    assert retrieved_entry.action_type == action
    assert retrieved_entry.action_data == data
    assert retrieved_entry.thermal_state == thermal_state
    assert retrieved_entry.action_hash == action_hash


def test_rekor_multiple_entries(rekor_db: RekorLite):
    """
    Tests that the Merkle root is correctly updated with multiple entries.
    """
    # Log first action
    _, first_merkle_root = rekor_db.log_action("action1", "data1")
    
    # Log second action
    _, second_merkle_root = rekor_db.log_action("action2", "data2")

    # The Merkle roots should be different after each addition
    assert first_merkle_root != second_merkle_root

    # Check the final state
    stats = rekor_db.get_stats()
    assert stats["entries"] == 2
    assert stats["merkle_root"] == second_merkle_root

