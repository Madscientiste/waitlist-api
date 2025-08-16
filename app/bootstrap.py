# This script initializes the database by creating all tables,
# and then loads fixture data from CSV files in the data/ directory.
# It serves as a utility to quickly teardown and set up the entire project,
# streamlining the development and testing workflow.
import csv
from datetime import datetime
from pathlib import Path
from random import randint, random

from app.logger import logger
from app.models.user import User
from app.models.waitlist import Waitlist

# Data is at the root of the project
DATA_DIR = Path(__file__).parent.parent / "data"


def init(skip_data=False):
    from app.database.connection import db
    from app.database.model import BaseModel
    from app.models import Event, Inventory, Offer, Representation

    # Just remove everything and start fresh each time
    BaseModel.metadata.drop_all(db.engine)
    BaseModel.metadata.create_all(db.engine)

    if skip_data:
        return

    # Load events
    with open(DATA_DIR / "events.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            event = Event(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                thumbnail_url=row["thumbnail_url"] if row["thumbnail_url"] else None,
                organization_id=row["organization_id"],
                venue_name=row["venue_name"],
                venue_address=row["venue_address"],
                timezone=row["timezone"],
            ).save()
            logger.info(f"Created event: {event.title}")

    # Load representations
    with open(DATA_DIR / "representations.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Parse datetime strings
            start_dt = datetime.fromisoformat(row["start_datetime"])
            end_dt = datetime.fromisoformat(row["end_datetime"])

            representation = Representation(
                id=row["id"], event_id=row["event_id"], start_datetime=start_dt, end_datetime=end_dt
            ).save()
            logger.info(f"Created representation: {representation.id} for event {representation.event_id}")

    # Load offers
    with open(DATA_DIR / "offers.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            offer = Offer(
                offer_id=row["offer_id"],
                event_id=row["event_id"],
                name=row["name"],
                type=row["type"],
                max_quantity_per_order=int(row["max_quantity_per_order"]),
                description=row["description"] if row["description"] else None,
            ).save()
            logger.info(f"Created offer: {offer.name} for event {offer.event_id}")

    # Load inventory
    with open(DATA_DIR / "inventory.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            inventory = Inventory(
                inventory_id=row["inventory_id"],
                offer_id=row["offer_id"],
                representation_id=row["representation_id"],
                total_stock=int(row["total_stock"]),
                available_stock=int(row["available_stock"]),
            ).save()
            logger.info(
                f"Created inventory: {inventory.inventory_id} - {inventory.available_stock}/{inventory.total_stock} available"
            )

    # create 30 waitlist entries
    for i in range(30):
        user = User(
            id=f"user_0{i:02d}",
            email=f"test{i}@test.com",
            first_name=f"Test{i}",
            last_name=f"User{i}",
        ).save()

        # create a waitlist entry for the user
        Waitlist(
            id=f"wait_user_0{i:02d}_off_001_repr_001",
            user_id=user.id,
            offer_id="off_001",
            representation_id="rep_001",
            requested_quantity=randint(1, 10),
        ).save()


def teardown():
    """Drop all tables to clean the database"""
    from app.database.connection import db
    from app.database.model import BaseModel

    BaseModel.metadata.drop_all(db.engine)


# If we want to run this script directly, we can do so with:
# python -m app.bootstrap
# or
# python -m app.bootstrap teardown
# to teardown the database
# Otherwise, its meant to be used for testing.. mainly.
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "teardown":
        teardown()
        logger.info("Database teardown complete!")
    else:
        init()
        logger.info("Database bootstrap complete!")
