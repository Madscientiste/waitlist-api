import math
from typing import List

from fastapi import APIRouter, Query

from app import logger
from app.api.schemas.offers import (
    JoinWaitlistResponse,
    LeaveWaitlistResponse,
    PageInfo,
    UserPositionResponse,
    WaitlistEntriesResponse,
    WaitlistEntryResponse,
)
from app.config import app_config
from app.context.app import get_app_context
from app.models.health import Health
from app.repositories.waitlist import WaitlistRepository

router = APIRouter(tags=["offers"])
repo = WaitlistRepository()


@router.get(
    "/offers/{offer_id}/representations/{representation_id}/waitlist",
    response_model=WaitlistEntriesResponse,
)
async def get_waitlist_entries(
    offer_id: str,
    representation_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of entries to return",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of entries to skip",
    ),
):
    """
    Get all entries in the waitlist for a specific offer and representation.
    """
    total_count = repo.get_waitlist_entries_count(offer_id, representation_id)
    entries = repo.get_waitlist_entries(offer_id, representation_id, limit, offset)

    # Calculate pagination info
    page = (offset // limit) + 1
    total_pages = math.ceil(total_count / limit) if total_count > 0 else 1
    has_next_page = offset + limit < total_count
    has_previous_page = offset > 0

    # Convert entries to response models
    items = [
        WaitlistEntryResponse(
            id=entry.id,
            user_id=entry.user_id,
            offer_id=entry.offer_id,
            representation_id=entry.representation_id,
            position=entry.position,
            requested_quantity=entry.requested_quantity,
            created=entry.created.isoformat(),
        )
        for entry in entries
    ]

    page_info = PageInfo(
        has_next_page=has_next_page,
        has_previous_page=has_previous_page,
        total_count=total_count,
        page=page,
        page_size=limit,
        total_pages=total_pages,
    )

    return WaitlistEntriesResponse(
        items=items,
        page_info=page_info,
    )


@router.get(
    "/offers/{offer_id}/representations/{representation_id}/waitlist/{user_id}",
    response_model=UserPositionResponse,
)
async def get_user_position(offer_id: str, representation_id: str, user_id: str):
    """
    Get the waitlist position for a specific user.
    """
    waitlist_entry = repo.get_user_waitlist(user_id, offer_id, representation_id)
    return UserPositionResponse(
        user_id=waitlist_entry.user_id,
        offer_id=waitlist_entry.offer_id,
        representation_id=waitlist_entry.representation_id,
        position=waitlist_entry.position,
        requested_quantity=waitlist_entry.requested_quantity,
    )


@router.post(
    "/offers/{offer_id}/representations/{representation_id}/waitlist",
    response_model=JoinWaitlistResponse,
)
async def join_waitlist(
    offer_id: str,
    representation_id: str,
    user_id: str = Query(..., description="ID of the user joining the waitlist"),
    quantity: int = Query(default=1, ge=1, le=10, description="Number of tickets requested"),
):
    """
    Join the waitlist for a specific offer and representation.
    """
    waitlist_entry = repo.join_waitlist(user_id, offer_id, representation_id, quantity)
    return JoinWaitlistResponse(
        id=waitlist_entry.id,
        user_id=waitlist_entry.user_id,
        offer_id=waitlist_entry.offer_id,
        representation_id=waitlist_entry.representation_id,
        position=waitlist_entry.position,
        requested_quantity=waitlist_entry.requested_quantity,
        message=f"Successfully joined waitlist at position {waitlist_entry.position}",
    )


@router.delete(
    "/offers/{offer_id}/representations/{representation_id}/waitlist/{user_id}",
    response_model=LeaveWaitlistResponse,
)
async def leave_waitlist(offer_id: str, representation_id: str, user_id: str):
    """
    Leave the waitlist for a specific offer and representation.
    """
    success = repo.leave_waitlist(user_id, offer_id, representation_id)
    return LeaveWaitlistResponse(
        message="Successfully left the waitlist",
        success=success,
    )
