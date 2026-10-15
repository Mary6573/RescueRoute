# FIFO versus greedy: supplied sample data

Both strategies received the same eight donations, five recipients, and four
volunteers. Each strategy started with independent copies of the same capacities,
locations, and pickup counts. Three volunteers were available; each had two trips.

| Metric | FIFO | Greedy |
| --- | ---: | ---: |
| Donations received | 8 | 8 |
| Donations assigned | 5 | 6 |
| Donations unassigned | 3 | 2 |
| Food rescued (units) | 155 | 175 |
| Food at risk (units) | 235 | 215 |
| Urgent rescue rate | 40.0% | 60.0% |
| Recipient capacity utilization | 64.6% | 72.9% |
| Volunteer capacity utilization | 38.8% | 43.8% |

FIFO processes earlier arrivals first. D-101 takes 35 units at Hillcrest and
D-102 takes 25 at Orange County Rescue Mission. D-103 then takes 35 at Santa Ana.
Only 15 units remain at each compatible meal recipient, so the 20-unit D-105
cannot fit.

Greedy considers D-103 first because it expires at 12:05, then D-105 because it
expires at 12:40. D-103 uses Hillcrest and D-105 uses 20 units at Orange County
Rescue Mission. Later D-108 uses that mission's other 20 units, D-102 moves to
Second Harvest, and D-101 moves to Santa Ana. All five donations rescued by FIFO
are still rescued, plus D-105. Thus greedy rescues one additional donation and
20 additional units; three of five urgent donations are rescued instead of two.

D-106 remains unassigned under both strategies because no recipient accepts
frozen desserts. D-107 has 200 units and exceeds every compatible recipient's
capacity; donations cannot be split.

Greedy is not guaranteed to be better on other inputs. In the automated fairness
example, a single recipient can hold only 50 units. FIFO gives that space to an
older 50-unit donation, while greedy gives it to a later 50-unit donation that
expires sooner. Total rescued quantity ties, but the urgent rescue rate changes
from 0% to 100%. The older donation is explicitly deferred and left unmatched.
Repeated preference for urgent arrivals can starve less urgent donations in a
repeated-use setting. This batch prototype does not add a fairness rule.

Reproduce these results with `python main.py`; run the 21 behavior tests with
`python -m unittest discover -v`. These results apply only to simulated input.
