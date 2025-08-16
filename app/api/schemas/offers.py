from typing import List

from pydantic import BaseModel


class PageInfo(BaseModel):
    """Information about pagination in a connection."""

    has_next_page: bool
    has_previous_page: bool
    total_count: int
    page: int
    page_size: int
    total_pages: int


class WaitlistEntryResponse(BaseModel):
    id: str
    user_id: str
    offer_id: str
    representation_id: str
    position: int
    requested_quantity: int
    created: str  # ISO datetime string


class WaitlistEntriesResponse(BaseModel):
    """Paginated response for waitlist entries."""

    items: List[WaitlistEntryResponse]
    page_info: PageInfo


class UserPositionResponse(BaseModel):
    user_id: str
    offer_id: str
    representation_id: str
    position: int
    requested_quantity: int


class JoinWaitlistResponse(BaseModel):
    id: str
    user_id: str
    offer_id: str
    representation_id: str
    position: int
    requested_quantity: int
    message: str


class LeaveWaitlistResponse(BaseModel):
    message: str
    success: bool
