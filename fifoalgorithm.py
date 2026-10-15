"""Shared first-feasible matching, plus FIFO ordering."""

from model import (time_minutes, clock_time, get_travel_time, validate_ids)


def schedule(ordered_donations, recipients, volunteers, travel_matrix=None, strategy='FIFO'):
    """Mutate recipient/volunteer copies and return assignments and failures."""
    validate_ids(ordered_donations, recipients, volunteers)
    assignments, unassigned = [], []
    latest_arrival = None
    for donation in ordered_donations:
        ready = time_minutes(donation.ready_time)
        deadline = ready + donation.expiry_minutes
        priority_note = ''
        if strategy == 'Greedy':
            # Explain when a later arrival was considered before this donation.
            overtaker = latest_arrival
            if overtaker and time_minutes(overtaker.ready_time) > ready:
                priority_note = (f'Deferred behind later-arriving {overtaker.donation_id} '
                                 'under the greedy expiration/quantity priority rule. ')
        if latest_arrival is None or ready > time_minutes(latest_arrival.ready_time):
            latest_arrival = donation

        reasons = set()
        match = None
        if donation.expiry_minutes <= 0:
            reasons.add('already expired at ready time')
        else:
            for recipient in recipients:
                if donation.food_type not in recipient.accepted_food_types:
                    reasons.add('recipient does not accept this food type')
                    continue
                if donation.quantity > recipient.remaining_capacity:
                    reasons.add('insufficient recipient capacity')
                    continue
                delivery_drive = get_travel_time(donation.pickup_area, recipient.location, travel_matrix)
                if delivery_drive is None:
                    reasons.add('unknown route to recipient')
                    continue
                if not volunteers:
                    reasons.add('no volunteers supplied')
                for volunteer in volunteers:
                    if not volunteer.is_available or volunteer.current_pickups >= volunteer.max_pickups:
                        reasons.add('volunteer unavailable or pickup limit reached')
                        continue
                    if donation.quantity > volunteer.vehicle_capacity:
                        reasons.add('insufficient volunteer vehicle capacity')
                        continue
                    pickup_drive = get_travel_time(volunteer.location, donation.pickup_area, travel_matrix)
                    if pickup_drive is None:
                        reasons.add('unknown route from volunteer to donor')
                        continue
                    pickup = max(ready, time_minutes(volunteer.available_at) + pickup_drive)
                    delivery = pickup + delivery_drive
                    if delivery >= deadline:
                        reasons.add('delivery would reach or exceed expiration')
                        continue
                    if delivery >= time_minutes(recipient.closing_time):
                        reasons.add('recipient would be closed at delivery')
                        continue
                    match = recipient, volunteer, pickup, delivery
                    break
                if match:
                    break

        if match:
            recipient, volunteer, pickup, delivery = match
            assignments.append({
                'donation_id': donation.donation_id,
                'recipient_id': recipient.recipient_id,
                'volunteer_id': volunteer.volunteer_id,
                'scheduled_time': clock_time(pickup),
                'delivery_time': clock_time(delivery),
                'status': 'Assigned',
                'decision_reason': priority_note + (
                    f'Donation {donation.donation_id} assigned to {recipient.organization_name} '
                    f'with volunteer {volunteer.volunteer_id} ({volunteer.volunteer_name}) '
                    f'under {strategy}. Pickup {clock_time(pickup)}, delivery {clock_time(delivery)}, '
                    f'expiration {clock_time(deadline)}. Recipient accepts {donation.food_type}, '
                    f'has capacity for {donation.quantity} units, and closes at {recipient.closing_time}; '
                    'volunteer has vehicle capacity and a pickup slot.'),
            })
            recipient.remaining_capacity -= donation.quantity
            volunteer.current_pickups += 1
            volunteer.available_at = clock_time(delivery)
            volunteer.location = recipient.location
        else:
            if not recipients:
                reasons.add('no recipients supplied')
            unassigned.append({
                'donation_id': donation.donation_id,
                'status': 'Unassigned',
                'decision_reason': priority_note + (
                    f'Donation {donation.donation_id} unassigned: no feasible combination. '
                    f'Failed checks: {"; ".join(sorted(reasons))}.'),
            })
    return assignments, unassigned


def fifo_sort(donations, recipients, volunteers, travel_matrix=None):
    # ready_time represents arrival; stable sorting preserves input order on ties.
    ordered = sorted(donations, key=lambda d: time_minutes(d.ready_time))
    return schedule(ordered, recipients, volunteers, travel_matrix, 'FIFO')
