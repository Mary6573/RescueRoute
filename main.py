"""Run both strategies on independent copies of the same simulated input."""

import argparse
from pathlib import Path
from model import load_data, load_travel_times, clone_state, calculate_metrics
from fifoalgorithm import fifo_sort
from greedyalgorithm import greedy_sort


def explain_comparison(fifo_assigned, greedy_assigned, fifo_metrics, greedy_metrics):
    fifo_ids = {a['donation_id'] for a in fifo_assigned}
    greedy_ids = {a['donation_id'] for a in greedy_assigned}
    print('\nComparison: FIFO uses arrival order; greedy uses earliest expiration,')
    print('then larger quantity and earlier arrival. Both use the same feasibility checks.')
    print('Only FIFO rescued:', ', '.join(sorted(fifo_ids - greedy_ids)) or 'None')
    print('Only greedy rescued:', ', '.join(sorted(greedy_ids - fifo_ids)) or 'None')
    delta = greedy_metrics['Food Rescued (units)'] - fifo_metrics['Food Rescued (units)']
    print(f'Greedy rescued {delta:+d} units compared with FIFO.')
    if fifo_ids != greedy_ids:
        print('Changing priority changes which donations consume limited capacity and pickup slots first.')
    elif [(a['donation_id'], a['recipient_id'], a['volunteer_id'], a['scheduled_time'], a['delivery_time'])
          for a in fifo_assigned] != [
              (a['donation_id'], a['recipient_id'], a['volunteer_id'], a['scheduled_time'], a['delivery_time'])
              for a in greedy_assigned]:
        print('Both rescued the same donations, but priority changed processing, times, or matches.')
    else:
        print('Priority did not change the outcome for this input.')
    print('Greedy is a local rule; it is not guaranteed to rescue the most food.')


def main():
    parser = argparse.ArgumentParser(description='RescueRoute: simulated food-donation matching')
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).parent / 'data')
    args = parser.parse_args()
    try:
        donations, recipients, volunteers = load_data(args.data_dir)
        travel_times = load_travel_times(args.data_dir)
    except (OSError, ValueError) as error:
        parser.exit(1, f'Input error: {error}\n')

    print('RescueRoute - educational simulation, not for operational food handling.')
    results = []
    for name, algorithm in [('FIFO', fifo_sort), ('Greedy', greedy_sort)]:
        recipient_copy, volunteer_copy = clone_state(recipients, volunteers)
        assigned, unassigned = algorithm(donations, recipient_copy, volunteer_copy, travel_times)
        metrics = calculate_metrics(donations, assigned, unassigned, recipients, volunteers)
        results.append((assigned, unassigned, metrics))
        print(f'\n{name}: {len(assigned)} assigned, {len(unassigned)} unassigned')
        for decision in assigned + unassigned:
            print('-', decision['decision_reason'])

    print(f'\n{"Metric":<30} {"FIFO":>12} {"Greedy":>12}')
    for key in results[0][2]:
        print(f'{key:<30} {str(results[0][2][key]):>12} {str(results[1][2][key]):>12}')
    explain_comparison(results[0][0], results[1][0], results[0][2], results[1][2])


if __name__ == '__main__':
    main()
