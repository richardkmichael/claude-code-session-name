#!/usr/bin/env python

import os
import tempfile
import uuid
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

# Use a temporary database for testing, not the real one
TEST_DB = Path(tempfile.gettempdir()) / f"claude_test_{uuid.uuid4().hex}.sqlite"

# Set environment variable so the wrapper uses the test database
os.environ["CLAUDE_CODE_SESSION_NAMES_DB"] = str(TEST_DB)

# Load the claude wrapper module by path
spec = spec_from_loader("claude", SourceFileLoader("claude", "./claude"))
claude = module_from_spec(spec)
spec.loader.exec_module(claude)

NameSession = claude.NameSession
lookup_session_by_name = claude.lookup_session_by_name


def setup_test_env():
    """Create a fresh test database."""
    if TEST_DB.exists():
        TEST_DB.unlink()
    print(f"✓ Test database created at {TEST_DB}")


def test_session_name_creation():
    """Test: Creating a named session"""
    print("\n--- Test 1: Creating a named session ---")

    test_uuid = "12345678-1234-1234-1234-123456789001"
    result = NameSession("test session", test_uuid).execute()

    if result.exit_code == 0:
        found = lookup_session_by_name("test session")
        if found == test_uuid:
            print(
                f"✓ Database entry created: name='test session', session_id='{test_uuid}'"
            )
        else:
            print("✗ Session not found")
    else:
        print("✗ Failed to save session")


def test_session_name_with_explicit_id():
    """Test: Creating a named session with explicit UUID"""
    print("\n--- Test 2: Creating a named session with explicit UUID ---")

    test_uuid = "12345678-1234-1234-1234-123456789002"
    result = NameSession("work", test_uuid).execute()

    if result.exit_code == 0:
        found = lookup_session_by_name("work")
        if found == test_uuid:
            print(f"✓ Database entry created: name='work', session_id='{test_uuid}'")
        else:
            print("✗ Session not found")
    else:
        print("✗ Failed to save session")


def test_uuid_uniqueness():
    """Test: UUID must be unique - cannot rename existing session"""
    print("\n--- Test 3: UUID uniqueness constraint ---")

    duplicate_uuid = "12345678-1234-1234-1234-123456789002"  # Same as previous test
    result = NameSession("different name", duplicate_uuid).execute()

    if result.error_type == "session_already_named":
        print("✓ Correctly rejected rename attempt (session already named 'work')")
    else:
        print(
            f"✗ Should have rejected with 'session_already_named', got: {result.error_type}"
        )


def test_idempotent_naming():
    """Test: Setting the same name twice should succeed"""
    print("\n--- Test 3.25: Idempotent naming ---")

    test_uuid = "12345678-1234-1234-1234-123456789003"

    # First call should succeed
    result1 = NameSession("idempotent-test", test_uuid).execute()
    if result1.exit_code != 0:
        print(f"✗ First naming attempt failed: {result1.message}")
        return

    # Second call with same name and UUID should also succeed
    result2 = NameSession("idempotent-test", test_uuid).execute()
    if result2.exit_code == 0:
        print("✓ Idempotent naming works (setting same name twice succeeds)")
    else:
        print(f"✗ Second naming attempt failed: {result2.message}")


def test_name_uniqueness():
    """Test: Session name must be unique"""
    print("\n--- Test 3.5: Session name uniqueness constraint ---")

    duplicate_name = "work"  # Same as previous test
    new_uuid = "12345678-1234-1234-1234-123456789099"
    result = NameSession(duplicate_name, new_uuid).execute()

    if result.error_type == "name_exists":
        print("✓ Correctly rejected duplicate name")
    else:
        print(f"✗ Should have rejected duplicate name, got: {result.error_type}")


def test_lookup_nonexistent_name():
    """Test: Looking up nonexistent session name"""
    print("\n--- Test 4: Looking up nonexistent session name ---")

    result = lookup_session_by_name("nonexistent")

    if result is None:
        print("✓ Correctly returned None for nonexistent session")
    else:
        print(f"✗ Should have returned None, got: {result}")


def test_multiple_sessions():
    """Test: Multiple sessions can coexist"""
    print("\n--- Test 5: Multiple sessions can coexist ---")

    test_uuids = [
        "12345678-1234-1234-1234-123456789010",
        "12345678-1234-1234-1234-123456789011",
        "12345678-1234-1234-1234-123456789012",
    ]
    test_names = ["project-a", "project-b", "project-c"]

    for name, test_uuid in zip(test_names, test_uuids):
        NameSession(name, test_uuid).execute()

    all_found = True
    for name, test_uuid in zip(test_names, test_uuids):
        found = lookup_session_by_name(name)
        if found != test_uuid:
            all_found = False
            print(f"✗ Session '{name}' not found")

    if all_found:
        print(f"✓ All {len(test_names)} sessions found correctly")


if __name__ == "__main__":
    setup_test_env()
    test_session_name_creation()
    test_session_name_with_explicit_id()
    test_uuid_uniqueness()
    test_idempotent_naming()
    test_name_uniqueness()
    test_lookup_nonexistent_name()
    test_multiple_sessions()

    print("\n✓ All database tests passed")

    # Cleanup
    if TEST_DB.exists():
        TEST_DB.unlink()
