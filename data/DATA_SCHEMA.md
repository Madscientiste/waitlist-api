# Sample Data Schema Documentation

This document describes the structure and relationships of the sample data provided for the waiting list feature
implementation.

**Context:** Each of our events has one or many representations. Each event has also one or many offers. An offer
represents an item sold for the event. In this exercise, we only have one type of offer which is "ticket". Each offer
has an inventory which represents the number of tickets available for a given representation. Our users can join a
waiting list for specific representation/offer combinations.

## Files Overview

- `events.csv` - Event information
- `representations.csv` - Show times/performances for events
- `offers.csv` - Ticket offers available for events
- `inventory.csv` - Stock levels for specific offers and representations

## Schema Details

### events.csv

| Column          | Type   | Description                              |
|-----------------|--------|------------------------------------------|
| id              | string | Unique event identifier (e.g., "ev_001") |
| title           | string | Event name/title                         |
| description     | string | Event description                        |
| thumbnail_url   | string | URL to event image                       |
| organization_id | string | Organizing entity (mostly "BILLY")       |
| venue_name      | string | Venue name                               |
| venue_address   | string | Venue address                            |
| timezone        | string | Event timezone (e.g., "Europe/Paris")    |

### representations.csv

| Column         | Type         | Description                                        |
|----------------|--------------|----------------------------------------------------|
| id             | string       | Unique representation identifier (e.g., "rep_001") |
| event_id       | string       | Key to events.id                                   |
| start_datetime | ISO datetime | Performance start time with timezone               |
| end_datetime   | ISO datetime | Performance end time with timezone                 |

### offers.csv

| Column                 | Type    | Description                                           |
|------------------------|---------|-------------------------------------------------------|
| offer_id               | string  | Unique offer identifier (e.g., "off_001")             |
| event_id               | string  | Key to events.id                                      |
| name                   | string  | Offer name (e.g., "General Admission", "VIP Package") |
| type                   | string  | Offer type (typically "ticket")                       |
| max_quantity_per_order | integer | Maximum tickets per purchase                          |
| description            | string  | Offer description                                     |

### inventory.csv

| Column            | Type    | Description                                   |
|-------------------|---------|-----------------------------------------------|
| inventory_id      | string  | Unique inventory identifier (e.g., "inv_001") |
| offer_id          | string  | Key to offers.offer_id                        |
| representation_id | string  | Key to representations.id                     |
| total_stock       | integer | Total tickets available for this offer/show   |
| available_stock   | integer | Currently available tickets                   |

## Relationships

```
events (1) ──→ (many) representations
events (1) ──→ (many) offers  
offers (1) ──→ (many) inventory
representations (1) ──→ (many) inventory
```

## Key Notes

- **Inventory is specific to both offer AND representation** - each show time has separate stock
- **Some inventory records have 0 available_stock** - perfect for testing waiting lists
- **Events span different dates and times** - realistic scheduling
- **Multiple representations per event** - festivals and multi-day events
- **Various offers** - General, VIP, Meet & Greet, etc. with different quantity limits

## Waiting List Context

For the waiting list feature:

- Users join waiting lists for specific `representation_id` + `offer_id` combinations
- A user can be on multiple waiting lists but only once per representation/offer combination