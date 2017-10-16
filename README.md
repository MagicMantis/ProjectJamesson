Project Roadmap:
- Fix (allow negative outputs (why is it only positive))
- Use genetic algorithm to improve population each day

Bonus:
- Add visualization on website
- Include bloomberg in inputs
- Decrease interval of snapshot collection

Completed
- Create database for snapshots and stock info
- Create interface for getting stock info from Robinhood
- Setup scheduled snapshots of stock info
- Get correct list of stocks
- Fix project runtimes to match trading hours
- Switch scheduler to Background and clean up times
- Make it try to run plan_day() at startup in case of restart
- Make stock_sql_driver get stock list from stocks table instead of hard-coded
- Set the project up to run automatically everyday
- Create interface for buying, selling, balance, cash robot
- Create simulator that simulates a robot buying and selling stocks
- Fix sql query to include bid size
- Give robot a brain (neural network)
	- Define initial inputs
	- Define initial outputs