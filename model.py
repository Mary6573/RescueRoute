"""Data, validation, travel lookup, and metrics for the simulated RescueRoute app."""

from dataclasses import dataclass
import copy
import json
from pathlib import Path


def require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be nonempty text")


def require_int(value, field, minimum=0):
    if type(value) is not int or (minimum is not None and value < minimum):
        raise ValueError(f"{field} must be an integer >= {minimum}" if minimum is not None
                         else f"{field} must be an integer")


def time_minutes(value):
    """Accept same-day times in exactly HH:MM format."""
    if not isinstance(value, str) or len(value) != 5 or value[2] != ':':
        raise ValueError(f"Invalid time {value!r}; use HH:MM")
    if not (value[:2].isdigit() and value[3:].isdigit()):
        raise ValueError(f"Invalid time {value!r}; use HH:MM")
    hour, minute = int(value[:2]), int(value[3:])
    if hour > 23 or minute > 59:
        raise ValueError(f"Invalid time {value!r}; use HH:MM")
    return hour * 60 + minute


def clock_time(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass
class Donation:
    donation_id: str
    donor_name: str
    food_type: str
    quantity: int
    expiry_minutes: int
    pickup_area: str
    ready_time: str

    def __post_init__(self):
        for field in ('donation_id', 'donor_name', 'food_type', 'pickup_area'):
            require_text(getattr(self, field), field)
        require_int(self.quantity, 'quantity', 1)
        # Zero/negative shelf life is valid input, but cannot be assigned.
        require_int(self.expiry_minutes, 'expiry_minutes', None)
        time_minutes(self.ready_time)


@dataclass
class Recipient:
    recipient_id: str
    organization_name: str
    accepted_food_types: set[str]
    capacity: int
    remaining_capacity: int | None = None
    location: str = 'Zone A'
    closing_time: str = '23:59'

    def __post_init__(self):
        for field in ('recipient_id', 'organization_name', 'location'):
            require_text(getattr(self, field), field)
        if not isinstance(self.accepted_food_types, (set, list, tuple)) or not self.accepted_food_types:
            raise ValueError('accepted_food_types must be a nonempty collection')
        for food in self.accepted_food_types:
            require_text(food, 'accepted_food_types item')
        self.accepted_food_types = set(self.accepted_food_types)
        require_int(self.capacity, 'capacity')
        if self.remaining_capacity is None:
            self.remaining_capacity = self.capacity
        require_int(self.remaining_capacity, 'remaining_capacity')
        if self.remaining_capacity > self.capacity:
            raise ValueError('remaining_capacity cannot exceed capacity')
        time_minutes(self.closing_time)


@dataclass
class Volunteer:
    volunteer_id: str
    volunteer_name: str
    vehicle_capacity: int
    location: str = 'Zone A'
    is_available: bool = True
    max_pickups: int = 5
    current_pickups: int = 0
    available_at: str = '00:00'

    def __post_init__(self):
        for field in ('volunteer_id', 'volunteer_name', 'location'):
            require_text(getattr(self, field), field)
        require_int(self.vehicle_capacity, 'vehicle_capacity', 1)
        require_int(self.max_pickups, 'max_pickups')
        require_int(self.current_pickups, 'current_pickups')
        if self.current_pickups > self.max_pickups:
            raise ValueError('current_pickups cannot exceed max_pickups')
        if type(self.is_available) is not bool:
            raise ValueError('is_available must be true or false')
        time_minutes(self.available_at)


def validate_ids(donations, recipients, volunteers):
    for items, field in ((donations, 'donation_id'), (recipients, 'recipient_id'),
                         (volunteers, 'volunteer_id')):
        seen = set()
        for item in items:
            identifier = getattr(item, field)
            if identifier in seen:
                raise ValueError(f'Duplicate {field}: {identifier}')
            seen.add(identifier)


def read_rows(path):
    with open(path, encoding='utf-8') as stream:
        rows = json.load(stream)
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f'{path.name} must contain a JSON list of objects')
    return rows


def require_fields(rows, fields):
    for row in rows:
        missing = set(fields) - row.keys()
        if missing:
            raise ValueError(f'Missing required fields: {", ".join(sorted(missing))}')
    return rows


def load_data(data_dir='data'):
    base = Path(data_dir)
    try:
        donations = [Donation(**row) for row in read_rows(base / 'donations.json')]
        recipient_rows = require_fields(read_rows(base / 'recipients.json'),
                                        ('location', 'closing_time'))
        recipients = [Recipient(**row) for row in recipient_rows]
        volunteers = []
        for row in read_rows(base / 'volunteers.json'):
            # Keep the field name already used by the sample JSON.
            if 'maximum_pickups' in row:
                row['max_pickups'] = row.pop('maximum_pickups')
            require_fields([row], ('location', 'is_available', 'max_pickups'))
            volunteers.append(Volunteer(**row))
    except TypeError as error:
        raise ValueError(f'Missing or unexpected data field: {error}') from error
    validate_ids(donations, recipients, volunteers)
    return donations, recipients, volunteers


def load_travel_times(data_dir='data'):
    path = Path(data_dir) / 'travel_times.json'
    if not path.exists():
        return {}
    with open(path, encoding='utf-8') as stream:
        matrix = json.load(stream)
    if not isinstance(matrix, dict):
        raise ValueError('travel_times.json must contain an object')
    for origin, destinations in matrix.items():
        require_text(origin, 'travel origin')
        if not isinstance(destinations, dict):
            raise ValueError('Each travel origin must contain a destination object')
        for destination, minutes in destinations.items():
            require_text(destination, 'travel destination')
            require_int(minutes, 'travel minutes')
    return matrix


def get_travel_time(origin_area, dest_area, travel_matrix=None):
    """Use city labels before the comma. An unknown route is infeasible."""
    origin = origin_area.split(',')[0].strip()
    destination = dest_area.split(',')[0].strip()
    if travel_matrix:
        return travel_matrix.get(origin, {}).get(destination)
    # Without a matrix, only identical areas can be matched (instant transfer).
    return 0 if origin == destination else None


def clone_state(recipients, volunteers):
    return copy.deepcopy(recipients), copy.deepcopy(volunteers)


def calculate_metrics(donations, assignments, unassigned, recipients, volunteers):
    lookup = {donation.donation_id: donation for donation in donations}
    rescued = sum(lookup[item['donation_id']].quantity for item in assignments)
    at_risk = sum(lookup[item['donation_id']].quantity for item in unassigned)
    urgent = {d.donation_id for d in donations if d.expiry_minutes <= 120}
    urgent_rescued = sum(item['donation_id'] in urgent for item in assignments)
    recipient_capacity = sum(r.remaining_capacity for r in recipients)
    # A vehicle is reusable; count its remaining trip slots, not just one load.
    volunteer_capacity = sum(v.vehicle_capacity * (v.max_pickups - v.current_pickups)
                             for v in volunteers if v.is_available)

    def percent(used, total):
        return f'{used / total * 100:.1f}%' if total else 'N/A'

    return {
        'Donations Received': len(donations),
        'Donations Assigned': len(assignments),
        'Donations Unassigned': len(unassigned),
        'Food Rescued (units)': rescued,
        'Food at Risk (units)': at_risk,
        'Urgent Rescue Rate': percent(urgent_rescued, len(urgent)),
        'Recipient Capacity Util': percent(rescued, recipient_capacity),
        'Volunteer Capacity Util': percent(rescued, volunteer_capacity),
    }
