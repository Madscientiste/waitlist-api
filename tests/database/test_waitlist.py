import pytest

from app.bootstrap import init
from app.database.connection import db, transaction
from app.models.health import Health
from app.models.user import User
from app.models.waitlist import Waitlist


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    init()
    yield


@pytest.fixture(scope="function", autouse=True)
def in_transaction():
    """
    Automatically wraps each test function in a database transaction,
    ensuring that any changes made to the database during the test are rolled back
    after the test completes. This keeps the database state clean between tests
    and avoids persisting test data.

    Usage:
        This fixture is applied automatically to all test functions in this module.
        Any database changes made within a test will be rolled back at the end of the test.
    """
    with transaction():
        yield
        # Explicitly roll back any changes before the transaction context commits,
        # ensuring the database remains unchanged after each test.
        db.session.rollback()


@pytest.fixture
def test_users():
    """Create test users for waitlist tests"""
    users = []
    for i in range(1, 5):  # Create users 1-4
        user = User(
            id=f"test_user_{i:03d}",
            email=f"test_user_{i:03d}@test.com",
            first_name=f"Test User {i}",
            last_name=f"Test User {i}",
        ).save()
        users.append(user)
    return users


def test_waitlist_creation():
    """Test basic waitlist entry creation with position calculation"""
    # Create a waitlist entry using real data from CSV
    waitlist_entry = Waitlist(
        id="wait_test_001",
        user_id="user_001",
        offer_id="off_001",  # General Admission from Jazz Festival
        representation_id="rep_001",  # Friday July 15 show
        requested_quantity=2,
    ).save()

    assert waitlist_entry.id == "wait_test_001"
    assert waitlist_entry.user_id == "user_001"
    assert waitlist_entry.offer_id == "off_001"
    assert waitlist_entry.representation_id == "rep_001"
    assert waitlist_entry.requested_quantity == 2

    #
    assert waitlist_entry.position == 1  # First entry should have position 1


def test_waitlist_position_auto_calculation(test_users):
    """Test that position is automatically calculated based on existing entries"""
    # test_users fixture creates users for us

    # Create first entry
    first_entry = Waitlist(
        id="wait_test_001",
        user_id="test_user_001",
        offer_id="off_001",
        representation_id="rep_001",
        requested_quantity=1,
    ).save()

    # Create second entry
    second_entry = Waitlist(
        id="wait_test_002",
        user_id="test_user_002",
        offer_id="off_001",
        representation_id="rep_001",
        requested_quantity=1,
    ).save()

    # Create third entry
    third_entry = Waitlist(
        id="wait_test_003",
        user_id="test_user_003",
        offer_id="off_001",
        representation_id="rep_001",
        requested_quantity=1,
    ).save()

    assert first_entry.position == 1
    assert second_entry.position == 2
    assert third_entry.position == 3


def test_waitlist_position_per_combination(test_users):
    """Test that position is calculated separately for each offer/representation combination"""
    # Create entries for first combination (off_001 + rep_001)
    first_combo_entry1 = Waitlist(
        id="wait_test_001",
        user_id="test_user_001",
        offer_id="off_001",  # General Admission
        representation_id="rep_001",  # Friday July 15
        requested_quantity=1,
    ).save()

    first_combo_entry2 = Waitlist(
        id="wait_test_002",
        user_id="test_user_002",
        offer_id="off_001",  # General Admission
        representation_id="rep_001",  # Friday July 15
        requested_quantity=1,
    ).save()

    # Create entry for different combination (off_002 + rep_002)
    second_combo_entry = Waitlist(
        id="wait_test_003",
        user_id="test_user_003",
        offer_id="off_002",  # VIP Package
        representation_id="rep_002",  # Saturday July 16
        requested_quantity=1,
    ).save()

    # First combination should have positions 1 and 2
    assert first_combo_entry1.position == 1
    assert first_combo_entry2.position == 2

    # Second combination should start at position 1
    assert second_combo_entry.position == 1


def test_waitlist_default_quantity():
    """Test that requested_quantity defaults to 1"""
    waitlist_entry = Waitlist(
        id="wait_test_001",
        user_id="user_001",
        offer_id="off_001",
        representation_id="rep_001",
        # requested_quantity not specified
    ).save()

    assert waitlist_entry.requested_quantity == 1
    assert waitlist_entry.position == 1


def test_waitlist_unique_constraint(test_users):
    """Test that users can only join the same waitlist once per offer/representation"""
    # Create first entry
    first_entry = Waitlist(
        id="wait_test_001",
        user_id="user_001",
        offer_id="off_001",
        representation_id="rep_001",
        requested_quantity=1,
    ).save()

    # Try to create duplicate entry - should fail due to unique constraint
    with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
        duplicate_entry = Waitlist(
            id="wait_test_002",
            user_id="user_001",  # Same user
            offer_id="off_001",  # Same offer
            representation_id="rep_001",  # Same representation
            requested_quantity=2,
        ).save()


def test_waitlist_with_real_data(test_users):
    """Test waitlist using actual data from CSV files"""
    # Test with real event data from the CSV files

    # Jazz Festival General Admission for Friday show (rep_001 + off_001)
    jazz_friday_general = Waitlist(
        id="wait_jazz_001",
        user_id="user_001",
        offer_id="off_001",  # General Admission
        representation_id="rep_001",  # Friday July 15
        requested_quantity=3,
    ).save()

    # Jazz Festival VIP for Friday show (rep_001 + off_002)
    jazz_friday_vip = Waitlist(
        id="wait_jazz_002",
        user_id="test_user_002",
        offer_id="off_002",  # VIP Package
        representation_id="rep_001",  # Friday July 15
        requested_quantity=1,
    ).save()

    # Jazz Festival General Admission for Saturday show (rep_002 + off_001)
    jazz_saturday_general = Waitlist(
        id="wait_jazz_003",
        user_id="test_user_003",
        offer_id="off_001",  # General Admission
        representation_id="rep_002",  # Saturday July 16
        requested_quantity=2,
    ).save()

    # Check positions are calculated correctly per combination
    assert jazz_friday_general.position == 1  # First in Friday General
    assert jazz_friday_vip.position == 1  # First in Friday VIP
    assert jazz_saturday_general.position == 1  # First in Saturday General


def test_waitlist_query_by_position(test_users):
    """Test querying waitlist entries by position"""
    # Create multiple entries
    entries = []
    for i in range(1, 4):
        entry = Waitlist(
            id=f"wait_test_{i:03d}",
            user_id=f"test_user_{i:03d}",
            offer_id="off_001",
            representation_id="rep_001",
            requested_quantity=1,
        ).save()
        entries.append(entry)

    # Query by position
    first_in_line = (
        Waitlist.session.query(Waitlist)
        .filter(Waitlist.offer_id == "off_001", Waitlist.representation_id == "rep_001")
        .order_by(Waitlist.position)
        .first()
    )

    assert first_in_line.position == 1
    assert first_in_line.user_id == "test_user_001"

    # Get all entries ordered by position
    all_entries = (
        Waitlist.session.query(Waitlist)
        .filter(Waitlist.offer_id == "off_001", Waitlist.representation_id == "rep_001")
        .order_by(Waitlist.position)
        .all()
    )

    assert len(all_entries) == 3
    assert all_entries[0].position == 1
    assert all_entries[1].position == 2
    assert all_entries[2].position == 3
