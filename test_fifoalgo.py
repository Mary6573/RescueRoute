"""Behavior tests for validation, feasibility, and state updates (standard library)."""

import json
from pathlib import Path
import tempfile
import unittest
from model import Donation, Recipient, Volunteer, load_data, load_travel_times, clone_state, calculate_metrics
from fifoalgorithm import fifo_sort
from greedyalgorithm import greedy_sort


def donation(identifier='D1', **changes):
    values = dict(donation_id=identifier, donor_name='Cafe', food_type='meals',
                  quantity=10, expiry_minutes=60, pickup_area='Zone A', ready_time='10:00')
    values.update(changes)
    return Donation(**values)


class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.recipients = [Recipient('R1', 'Pantry', {'meals'}, 20)]
        self.volunteers = [Volunteer('V1', 'Alex', 20)]

    def run_both(self, donations):
        for algorithm in (fifo_sort, greedy_sort):
            recipients, volunteers = clone_state(self.recipients, self.volunteers)
            yield algorithm(donations, recipients, volunteers)

    def test_normal_match(self):
        for assigned, unassigned in self.run_both([donation()]):
            self.assertEqual(len(assigned), 1)
            self.assertEqual(unassigned, [])
            self.assertEqual(assigned[0]['recipient_id'], 'R1')
            self.assertEqual(assigned[0]['scheduled_time'], '10:00')
            self.assertIn('accepts meals', assigned[0]['decision_reason'])

    def test_duplicate_ids(self):
        cases = [([donation(), donation()], self.recipients, self.volunteers),
                 ([donation()], self.recipients * 2, self.volunteers),
                 ([donation()], self.recipients, self.volunteers * 2)]
        for algorithm in (fifo_sort, greedy_sort):
            for donations, recipients, volunteers in cases:
                with self.assertRaisesRegex(ValueError, 'Duplicate'):
                    algorithm(donations, recipients, volunteers)

    def test_expired_donation(self):
        for life in (0, -1):
            for assigned, unassigned in self.run_both([donation(expiry_minutes=life)]):
                self.assertEqual(assigned, [])
                self.assertIn('already expired', unassigned[0]['decision_reason'])

    def test_nearly_expired_still_feasible(self):
        for assigned, unassigned in self.run_both([donation(expiry_minutes=1)]):
            self.assertEqual(len(assigned), 1)
            self.assertEqual(unassigned, [])

    def test_incompatible_food(self):
        for assigned, unassigned in self.run_both([donation(food_type='bakery')]):
            self.assertEqual(assigned, [])
            self.assertIn('food type', unassigned[0]['decision_reason'])

    def test_insufficient_recipient_capacity(self):
        for assigned, unassigned in self.run_both([donation(quantity=21)]):
            self.assertEqual(assigned, [])
            self.assertIn('recipient capacity', unassigned[0]['decision_reason'])

    def test_no_capable_or_available_volunteer(self):
        for volunteer in (Volunteer('V1', 'Alex', 5), Volunteer('V1', 'Alex', 20, is_available=False),
                          Volunteer('V1', 'Alex', 20, max_pickups=0)):
            self.volunteers = [volunteer]
            for assigned, unassigned in self.run_both([donation()]):
                self.assertEqual(assigned, [])
                self.assertIn('volunteer', unassigned[0]['decision_reason'])

    def test_competing_capacity(self):
        for assigned, unassigned in self.run_both([donation(quantity=15), donation('D2', quantity=15)]):
            self.assertEqual([a['donation_id'] for a in assigned], ['D1'])
            self.assertEqual([u['donation_id'] for u in unassigned], ['D2'])

    def test_empty_lists(self):
        for assigned, unassigned in self.run_both([]):
            self.assertEqual((assigned, unassigned), ([], []))
        for algorithm in (fifo_sort, greedy_sort):
            assigned, unassigned = algorithm([donation()], [], [])
            self.assertEqual(assigned, [])
            self.assertIn('no recipients', unassigned[0]['decision_reason'])

    def test_delivery_before_expiration_and_closing(self):
        matrix = {'Zone A': {'Zone A': 5}}
        for algorithm in (fifo_sort, greedy_sort):
            for life, closing, reason in ((5, '23:59', 'expiration'), (60, '10:05', 'closed')):
                recipients = [Recipient('R1', 'Pantry', {'meals'}, 20, closing_time=closing)]
                volunteers = [Volunteer('V1', 'Alex', 20)]
                assigned, unassigned = algorithm([donation(expiry_minutes=life)], recipients, volunteers, matrix)
                self.assertEqual(assigned, [])
                self.assertIn(reason, unassigned[0]['decision_reason'])

    def test_unknown_route(self):
        for assigned, unassigned in self.run_both([donation(pickup_area='Zone B')]):
            self.assertEqual(assigned, [])
            self.assertIn('unknown route', unassigned[0]['decision_reason'])

    def test_volunteer_travel_availability_and_no_overlap(self):
        for algorithm in (fifo_sort, greedy_sort):
            recipients = [Recipient('R1', 'Pantry', {'meals'}, 30, location='B')]
            volunteers = [Volunteer('V1', 'Alex', 20, location='A', available_at='10:00')]
            matrix = {'A': {'A': 0, 'B': 10}, 'B': {'A': 10, 'B': 0}}
            assigned, unassigned = algorithm([donation(pickup_area='A'), donation('D2', pickup_area='A')],
                                             recipients, volunteers, matrix)
            self.assertEqual(unassigned, [])
            self.assertEqual([a['delivery_time'] for a in assigned], ['10:10', '10:30'])
            self.assertEqual(assigned[1]['scheduled_time'], '10:20')
            self.assertEqual(volunteers[0].current_pickups, 2)
            self.assertEqual(recipients[0].remaining_capacity, 10)

    def test_pickup_limit(self):
        self.volunteers[0].max_pickups = 1
        for assigned, unassigned in self.run_both([donation(), donation('D2')]):
            self.assertEqual(len(assigned), 1)
            self.assertIn('pickup limit', unassigned[0]['decision_reason'])

    def test_zero_remaining_capacity_is_preserved(self):
        self.recipients = [Recipient('R1', 'Pantry', {'meals'}, 20, remaining_capacity=0)]
        for assigned, unassigned in self.run_both([donation()]):
            self.assertEqual(assigned, [])
            self.assertIn('capacity', unassigned[0]['decision_reason'])

    def test_invalid_values(self):
        for values in ({'quantity': 0}, {'quantity': -1}, {'quantity': True},
                       {'donation_id': ''}, {'food_type': ''}, {'pickup_area': ''},
                       {'ready_time': '25:00'}, {'ready_time': '9:00'}, {'expiry_minutes': '60'}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                donation(**values)
        for values in ({'is_available': 'false'}, {'vehicle_capacity': 0}, {'max_pickups': -1},
                       {'location': ''}, {'available_at': '10:99'}, {'current_pickups': 6}):
            defaults = dict(volunteer_id='V1', volunteer_name='Alex', vehicle_capacity=20)
            defaults.update(values)
            with self.subTest(values=values), self.assertRaises(ValueError):
                Volunteer(**defaults)
        for values in ({'capacity': -1}, {'accepted_food_types': 'meals'},
                       {'closing_time': '24:00'}, {'remaining_capacity': 30}, {'location': ''}):
            defaults = dict(recipient_id='R1', organization_name='Pantry', accepted_food_types={'meals'}, capacity=20)
            defaults.update(values)
            with self.subTest(values=values), self.assertRaises(ValueError):
                Recipient(**defaults)

    def test_json_loading_and_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for name in ('donations', 'recipients', 'volunteers'):
                (base / f'{name}.json').write_text('[]', encoding='utf-8')
            self.assertEqual(load_data(base), ([], [], []))
            row = vars(donation())
            (base / 'donations.json').write_text(json.dumps([row, row]), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                load_data(base)
            row['quantity'] = '10'
            (base / 'donations.json').write_text(json.dumps([row]), encoding='utf-8')
            with self.assertRaises(ValueError):
                load_data(base)
            (base / 'donations.json').write_text('[]', encoding='utf-8')
            incomplete = dict(recipient_id='R1', organization_name='Pantry',
                              accepted_food_types=['meals'], capacity=20)
            (base / 'recipients.json').write_text(json.dumps([incomplete]), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Missing required fields'):
                load_data(base)
            (base / 'recipients.json').write_text('[]', encoding='utf-8')
            (base / 'donations.json').write_text('{}', encoding='utf-8')
            with self.assertRaises(ValueError):
                load_data(base)
            (base / 'travel_times.json').write_text('{"A": {"B": -1}}', encoding='utf-8')
            with self.assertRaises(ValueError):
                load_travel_times(base)

    def test_metrics_reusable_vehicle_and_empty_case(self):
        donations = [donation(), donation('D2')]
        recipients, volunteers = clone_state(self.recipients, self.volunteers)
        assigned, unassigned = fifo_sort(donations, recipients, volunteers)
        metrics = calculate_metrics(donations, assigned, unassigned, self.recipients, self.volunteers)
        self.assertEqual(metrics['Food Rescued (units)'], 20)
        self.assertEqual(metrics['Food at Risk (units)'], 0)
        self.assertEqual(metrics['Urgent Rescue Rate'], '100.0%')
        self.assertEqual(metrics['Recipient Capacity Util'], '100.0%')
        self.assertEqual(metrics['Volunteer Capacity Util'], '20.0%')
        empty = calculate_metrics([], [], [], [], [])
        self.assertEqual(empty['Donations Received'], 0)
        self.assertEqual(empty['Urgent Rescue Rate'], 'N/A')


if __name__ == '__main__':
    unittest.main()
