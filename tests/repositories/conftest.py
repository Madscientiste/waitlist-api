from datetime import datetime, timedelta

import pytest

from app.bootstrap import init
from app.database.connection import transaction
from app.models.event import Event
from app.models.inventory import Inventory
from app.models.offer import Offer
from app.models.representation import Representation
from app.models.user import User


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """This time, this will reset the database and create the tables for each test"""
    init(skip_data=True)

    yield


@pytest.fixture
def event(setup_database):
    """Create a test event"""
    return Event(
        id="test_event_001",
        title="Test Concert",
        organization_id="TEST_ORG",
        venue_name="Test Venue",
        venue_address="123 Test St",
        timezone="Europe/Paris",
    ).save()


@pytest.fixture
def representation(event):
    """Create a test representation for the event"""
    return Representation(
        id="test_rep_001",
        event_id=event.id,
        start_datetime=datetime.now(),
        end_datetime=datetime.now() + timedelta(hours=3),
    ).save()


@pytest.fixture
def offer(event):
    """Create a test offer for the event"""
    return Offer(
        offer_id="test_offer_001",
        event_id=event.id,
        name="General Admission",
        type="ticket",
        max_quantity_per_order=4,
        description="Test tickets",
    ).save()


@pytest.fixture
def user(setup_database):
    """Create a test user"""
    return User(
        id="test_user_001",
        email="test@example.com",
        first_name="Test",
        last_name="User",
    ).save()


@pytest.fixture
def sold_out_inventory(offer, representation):
    """Create sold out inventory (waitlist available)"""
    return Inventory(
        inventory_id="test_inv_sold_out_001",
        offer_id=offer.offer_id,
        representation_id=representation.id,
        total_stock=100,
        available_stock=0,
    ).save()


@pytest.fixture
def available_inventory(offer, representation):
    """Create available inventory (waitlist not available)"""
    return Inventory(
        inventory_id="test_inv_available_001",
        offer_id=offer.offer_id,
        representation_id=representation.id,
        total_stock=100,
        available_stock=100,
    ).save()
