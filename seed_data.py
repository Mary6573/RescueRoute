"""
seed_data.py - Seed data for RescueRoute
sample data generated through Codex
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

TRAVEL_TIMES_MINUTES = {
    "Fullerton": {
        "Fullerton": 5,
        "Anaheim": 10,
        "Santa Ana": 18,
        "Tustin": 20,
        "Irvine": 25,
    },
    "Santa Ana": {
        "Fullerton": 18,
        "Anaheim": 12,
        "Santa Ana": 5,
        "Tustin": 8,
        "Irvine": 15,
    },
    "Anaheim": {
        "Fullerton": 10,
        "Anaheim": 5,
        "Santa Ana": 12,
        "Tustin": 15,
        "Irvine": 22,
    },
    "Tustin": {
        "Fullerton": 20,
        "Anaheim": 15,
        "Santa Ana": 8,
        "Tustin": 5,
        "Irvine": 12,
    },
    "Irvine": {
        "Fullerton": 25,
        "Anaheim": 22,
        "Santa Ana": 15,
        "Tustin": 12,
        "Irvine": 5,
    },
}

SAMPLE_DONATIONS = [
    {
        "donation_id": "D-101",
        "donor_name": "Chipotle Mexican Grill",
        "food_type": "prepared_meals",
        "quantity": 35,
        "expiry_minutes": 240,
        "pickup_area": "Fullerton, CA",
        "ready_time": "11:00"
    },
    {
        "donation_id": "D-102",
        "donor_name": "Panera Bread",
        "food_type": "bakery",
        "quantity": 25,
        "expiry_minutes": 180,
        "pickup_area": "Anaheim, CA",
        "ready_time": "11:15"
    },
    {
        "donation_id": "D-103",
        "donor_name": "Campus Dining Hall",
        "food_type": "prepared_meals",
        "quantity": 35,
        "expiry_minutes": 35,
        "pickup_area": "Fullerton, CA",
        "ready_time": "11:30"
    },
    {
        "donation_id": "D-104",
        "donor_name": "Sprouts Farmers Market",
        "food_type": "produce",
        "quantity": 40,
        "expiry_minutes": 300,
        "pickup_area": "Santa Ana, CA",
        "ready_time": "11:45"
    },
    {
        "donation_id": "D-105",
        "donor_name": "Corner Cafe",
        "food_type": "prepared_meals",
        "quantity": 20,
        "expiry_minutes": 40,
        "pickup_area": "Fullerton, CA",
        "ready_time": "12:00"
    },
    {
        "donation_id": "D-106",
        "donor_name": "Local Ice Cream Shop",
        "food_type": "frozen_desserts",
        "quantity": 15,
        "expiry_minutes": 60,
        "pickup_area": "Anaheim, CA",
        "ready_time": "12:15"
    },
    {
        "donation_id": "D-107",
        "donor_name": "Grand Event Catering",
        "food_type": "prepared_meals",
        "quantity": 200,
        "expiry_minutes": 90,
        "pickup_area": "Tustin, CA",
        "ready_time": "12:20"
    },
    {
        "donation_id": "D-108",
        "donor_name": "Downtown French Bakery",
        "food_type": "bakery",
        "quantity": 20,
        "expiry_minutes": 90,
        "pickup_area": "Irvine, CA",
        "ready_time": "12:30"
    }
]

SAMPLE_RECIPIENTS = [
    {
        "recipient_id": "R-101",
        "organization_name": "Hillcrest Recreation Center",
        "accepted_food_types": ["prepared_meals"],
        "capacity": 50,
        "location": "Fullerton, CA",
        "closing_time": "22:00"
    },
    {
        "recipient_id": "R-102",
        "organization_name": "Orange County Rescue Mission",
        "accepted_food_types": ["prepared_meals", "bakery"],
        "capacity": 40,
        "location": "Tustin, CA",
        "closing_time": "18:00"
    },
    {
        "recipient_id": "R-103",
        "organization_name": "Second Harvest Food Bank",
        "accepted_food_types": ["produce", "bakery"],
        "capacity": 80,
        "location": "Irvine, CA",
        "closing_time": "17:00"
    },
    {
        "recipient_id": "R-104",
        "organization_name": "Hope Community Fridge",
        "accepted_food_types": ["produce"],
        "capacity": 20,
        "location": "Fullerton, CA",
        "closing_time": "20:00"
    },
    {
        "recipient_id": "R-105",
        "organization_name": "Santa Ana Food Pantry",
        "accepted_food_types": ["prepared_meals"],
        "capacity": 50,
        "location": "Santa Ana, CA",
        "closing_time": "19:00"
    }
]

SAMPLE_VOLUNTEERS = [
    {
        "volunteer_id": "V-101",
        "volunteer_name": "Alex Nguyen",
        "vehicle_capacity": 60,
        "location": "Fullerton",
        "is_available": True,
        "maximum_pickups": 2
    },
    {
        "volunteer_id": "V-102",
        "volunteer_name": "Maria Garcia",
        "vehicle_capacity": 50,
        "location": "Fullerton",
        "is_available": True,
        "maximum_pickups": 2
    },
    {
        "volunteer_id": "V-103",
        "volunteer_name": "David Kim",
        "vehicle_capacity": 90,
        "location": "Irvine",
        "is_available": True,
        "maximum_pickups": 2
    },
    {
        "volunteer_id": "V-104",
        "volunteer_name": "Sarah Jenkins",
        "vehicle_capacity": 50,
        "location": "Anaheim",
        "is_available": False,
        "maximum_pickups": 2
    }
]


def seed():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "donations.json", "w", encoding="utf-8") as f:
        json.dump(SAMPLE_DONATIONS, f, indent=4)

    with open(DATA_DIR / "recipients.json", "w", encoding="utf-8") as f:
        json.dump(SAMPLE_RECIPIENTS, f, indent=4)

    with open(DATA_DIR / "volunteers.json", "w", encoding="utf-8") as f:
        json.dump(SAMPLE_VOLUNTEERS, f, indent=4)

    with open(DATA_DIR / "travel_times.json", "w", encoding="utf-8") as f:
        json.dump(TRAVEL_TIMES_MINUTES, f, indent=4)

    print(f"Seed data successfully generated in '{DATA_DIR}':")
    print(f"  - {len(SAMPLE_DONATIONS)} donations")
    print(f"  - {len(SAMPLE_RECIPIENTS)} recipients")
    print(f"  - {len(SAMPLE_VOLUNTEERS)} volunteers")
    print(f"  - Travel time matrix for {len(TRAVEL_TIMES_MINUTES)} cities")


if __name__ == "__main__":
    seed()
