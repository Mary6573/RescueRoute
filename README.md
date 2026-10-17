# RescueRoute
RescueRoute is an educational prototype that matches food donations from restaurants, grocery stores and community organizations. The system determines which donations have expiration times, recipient capacity, operating hours and volunteer availibilty that can be assigned to or unassigned to.

# Project Objectives
- Coordinate surplus food donations with compatible community organizations.
- Prioritize donations based on expiration deadlines.
- Match donations with recipients that accept the appropriate food categories.
- Respect recipient capacity, operating hours, and volunteer vehicle capacity.
- Compare FIFO and greedy scheduling using measurable performance metrics.
- Explain assignment decisions and unmatched donations.
- Test algorithm behavior under normal, invalid, and resource-constrained scenarios.
  
# Run
Python 3.10+. No extra packages required.

python main.py

python -m unittest discover -v

# Architecture and Data
- model.py: records, JSON loading, validation, travel times, and metrics.
- fifoalgorithm.py: FIFO ordering and shared matching checks.
- greedyalgorithm.py: urgency-first ordering.
- main.py: runs both strategies and prints explanations and comparisons.
- seed_data.py: recreates sample JSON files in data/.
- test_*.py: 21 automated tests.
  
# Data Input & Constraints
Donations contain:  IDs, food type, Quantity, Location, Ready time, and Shelf life. 

Recipients contain: Accepted foods, Capacity, Location, and Closing time.

Volunteers contain: Vehicle capacity, Location, Availability, and Pickup limits.

Lists preserve order; sets check foods and duplicate IDs; dictionaries store lookups, decisions, and metrics.

# Algorithms
* FIFO: Earlier ready times first; ties keep input order.
* Greedy: Earliest expiration first, then larger quantity, then earlier ready time. Expiration equals ready time plus shelf life.

Both select the first feasible recipient and volunteer. Checks include food acceptance, capacity, availability, pickup limits, travel, expiration, and closing time. Every outcome includes an explanation.

Greedy locally favors urgent donations. It may defer older donations and does not guarantee maximum rescued quantity.

Complexity: Both take O(D log D + D × R × V), where D, R, and V are donation, recipient, and volunteer counts.

# Results
Sample data: FIFO rescues 155 units; greedy rescues 175 units by also assigning D-105. See COMPARISON.md.

Metrics include assigned/unassigned counts, rescued/at-risk quantity, urgent rescue rate, and recipient/volunteer utilization.

# Limitations
One-day batch scheduling, indivisible donations, simulated travel, and no route optimization or fairness protection. This educational prototype is not approved for real food-handling or operational use.

# Team Members
- Mary Jonn Justiniano — Algorithm & Optimization Lead. Commits: 5
- Brandon Silva — Data & Matching Lead. Commits: 7
- Arianna Washington — Product & Quality Lead. Commits:
  
# References and Assistance
Uses Python’s standard library and generated data. ChatGPT assisted with code revisions, validation, matching, tests, documentation, and command-line formatting and explanations, guidance in testing.
