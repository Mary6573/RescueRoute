"""Earliest expiration first; ties: larger quantity, then earlier ready time."""

from fifoalgorithm import schedule
from model import time_minutes


def greedy_sort(donations, recipients, volunteers, travel_matrix=None):
    ordered = sorted(donations, key=lambda d: (
        time_minutes(d.ready_time) + d.expiry_minutes,
        -d.quantity,
        time_minutes(d.ready_time),
    ))
    return schedule(ordered, recipients, volunteers, travel_matrix, 'Greedy')
