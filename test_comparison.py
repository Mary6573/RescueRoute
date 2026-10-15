"""Priority, fairness, and independent-state comparisons."""

import unittest
from model import Recipient, Volunteer, clone_state, calculate_metrics
from fifoalgorithm import fifo_sort
from greedyalgorithm import greedy_sort
from test_fifoalgo import donation


class ComparisonTests(unittest.TestCase):
    def test_fifo_vs_greedy_and_fairness_explanation(self):
        donations = [donation('D1', quantity=50, expiry_minutes=300),
                     donation('D2', quantity=50, expiry_minutes=30, ready_time='10:30')]
        recipients = [Recipient('R1', 'Pantry', {'meals'}, 50)]
        volunteers = [Volunteer('V1', 'Alex', 100)]
        results = []
        for algorithm in (fifo_sort, greedy_sort):
            r_copy, v_copy = clone_state(recipients, volunteers)
            assigned, unassigned = algorithm(donations, r_copy, v_copy)
            results.append((assigned, unassigned, calculate_metrics(donations, assigned, unassigned, recipients, volunteers)))
        self.assertEqual(results[0][0][0]['donation_id'], 'D1')
        self.assertEqual(results[1][0][0]['donation_id'], 'D2')
        self.assertEqual(results[0][1][0]['donation_id'], 'D2')
        self.assertEqual(results[1][1][0]['donation_id'], 'D1')
        self.assertIn('Deferred behind later-arriving D2', results[1][1][0]['decision_reason'])
        self.assertIn('recipient capacity', results[1][1][0]['decision_reason'])
        self.assertEqual(results[0][2]['Urgent Rescue Rate'], '0.0%')
        self.assertEqual(results[1][2]['Urgent Rescue Rate'], '100.0%')
        self.assertEqual(recipients[0].remaining_capacity, 50)
        self.assertEqual(volunteers[0].current_pickups, 0)

    def test_greedy_absolute_expiration_and_ties(self):
        # Same shelf life is not the same expiration when ready times differ.
        donations = [donation('late', ready_time='12:00', expiry_minutes=20),
                     donation('small', expiry_minutes=60, quantity=5),
                     donation('large', expiry_minutes=60, quantity=10),
                     donation('earlier', ready_time='09:30', expiry_minutes=90, quantity=10)]
        assigned, unassigned = greedy_sort(donations, [Recipient('R1', 'Pantry', {'meals'}, 100)],
                                           [Volunteer('V1', 'Alex', 50)])
        self.assertEqual(unassigned, [])
        self.assertEqual([a['donation_id'] for a in assigned], ['earlier', 'large', 'small', 'late'])

    def test_fifo_arrival_and_input_order_ties(self):
        assigned, _ = fifo_sort([donation('late', ready_time='11:00'), donation('first'), donation('second')],
                               [Recipient('R1', 'Pantry', {'meals'}, 100)], [Volunteer('V1', 'Alex', 50)])
        self.assertEqual([a['donation_id'] for a in assigned], ['first', 'second', 'late'])

    def test_first_feasible_recipient_and_volunteer(self):
        for algorithm in (fifo_sort, greedy_sort):
            recipients = [Recipient('bad', 'Bakery', {'bakery'}, 100),
                          Recipient('first', 'Pantry', {'meals'}, 100),
                          Recipient('second', 'Shelter', {'meals'}, 100)]
            volunteers = [Volunteer('small', 'Sam', 5), Volunteer('first', 'Alex', 50),
                          Volunteer('second', 'Pat', 50)]
            assigned, _ = algorithm([donation()], recipients, volunteers)
            self.assertEqual((assigned[0]['recipient_id'], assigned[0]['volunteer_id']), ('first', 'first'))


if __name__ == '__main__':
    unittest.main()
