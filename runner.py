# Title: Robot Market
# Author: Joseph Savold
# Purpose: The main launch point and scheduler for stock data gathering and managaing list of robots

import logging
import sys
import time
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from src.stock import StockDriver


class Runner:
    def __init__(self):

        print("Launching Stock Saver")

        logging.basicConfig()
        self.driver = StockDriver()
        self.sched = BackgroundScheduler()

        # run schedule daily jobs every weekday at 8
        self.sched.add_job(self.plan_day, 'cron', day_of_week='0-4', hour='8', args=[], misfire_grace_time=60*60)  
        self.sched.start()

        # run plan day to catch any remaining (in case of late start)
        n = datetime.now()
        if n.hour > 8 or (n.hour == 8 and (n.minute > 0 or n.second > 0)):
            self.plan_day()

        # keep program running
        while True:
            sys.stdout.flush()
            time.sleep(60)

    # clean up on shutdown
    def __del__(self):
        self.sched.shutdown()

    # schedule all jobs for the current day
    def plan_day(self):

        # setup variables to do time calculations
        t = datetime.today()
        print("Planning day for ", t)
        first_time = datetime(t.year, t.month, t.day, 9, 30)
        delta = timedelta(minutes=0)

        # update stock_list
        self.driver.update_stock_list()

        # schedule a snapshot for every 5 minutes between 9:30 and 4:00
        for i in range(78):
            self.sched.add_job(self.driver.take_snapshot, 'date',
                               run_date=(first_time + delta), args=[(first_time + delta)],
                               misfire_grace_time=60, max_instances=3)
            delta += timedelta(minutes=5)

Runner()
