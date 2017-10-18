# Title: Simulate
# Author: Joseph Savold
# Purpose: Simulate robot trading stocks over a given period

from collections import defaultdict
from datetime import date, time, datetime, timedelta
import csv
import random

from src.stock import StockDriver
from src.robot import Robot
from src.ai import Pool


class Simulator:
    def __init__(self):

        # Get date and time information
        today = date.today()
        self.current_datetime = datetime(today.year, today.month, today.day, 9, 30)

        # Define subset of stocks to use for simulation
        self.stock_list_string = "('NVDA', 'ABBV', 'DISCA')"
        self.stock_list = ['NVDA', 'ABBV', 'DISCA']
        self.stock_data = defaultdict(lambda: {})
        self.stock_data_clean = defaultdict(lambda: {})
        self.driver = StockDriver()

        # Get stock data for the day
        self.get_stock_data()
        
        # Get names for robots
        with open("res/names.csv", "r") as namefile:
            name_reader = csv.reader(namefile, delimiter=',')
            self.names = [x[0] for x in list(name_reader)]

        # Create pool of species of robot brains
        self.pool = Pool()
        self.pool.basic_generation()

        # Create robot bodies for brains
        self.robot_list = []
        for i, genome in enumerate(self.pool.all_genomes()):
            self.add_robot(random.choice(self.names)+str(i), genome)

        self.simulate()

    def add_robot(self, genome, name="Robot"):

        self.robot_list.append(Robot(self, genome, name))

    def set_datetime(self, datetime):

        self.current_datetime = datetime

    def get_stock_data(self):

        self.stock_data = defaultdict(lambda: {})
        conn = self.driver.connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM snapshots WHERE targetDateTime LIKE '" +
                       self.current_datetime.strftime("%Y-%m-%d") + "%' AND stockKey IN " +
                       self.stock_list_string + " ORDER BY stockKey, targetDateTime;")
        results = cursor.fetchall()
        conn.close()
        for result in results:
            self.stock_data[result[2]][result[1].time()] = result

        self.clean_data()

    def clean_data(self):
        lasttime = self.current_datetime
        cleantime = lasttime+timedelta(minutes=5)
        for stock in self.stock_data:
            while cleantime.time() < time(16):
                last_price = self.stock_data[stock][lasttime.time()][3]
                print(last_price)
                price = self.stock_data[stock][cleantime.time()][3]
                delta = price - last_price
                self.stock_data_clean[stock][cleantime] = delta / last_price
                lasttime = cleantime
                cleantime += timedelta(minutes=5)

    def simulate(self):

        while self.current_datetime.time() < time(16):
            for robot in self.robot_list:
                robot.simulate(self.stock_list)

            self.current_datetime += timedelta(minutes=5)

        total = []
        for robot in self.robot_list:
            robot.display()
            total += [robot.calculate_change()]
        total.sort()

        for i in total:
            print(i)

    def get_stock_info(self, stock):

        return self.stock_data[stock][self.current_datetime.time()]

    def get_ask_price(self, stock):

        return self.stock_data[stock][self.current_datetime.time()][3]

    def get_bid_price(self, stock):

        return self.stock_data[stock][self.current_datetime.time()][5]


s = Simulator()
