# Title: Simulate
# Author: Joseph Savold
# Purpose: Simulate robot trading stocks over a given period

from collections import defaultdict
from datetime import date, time, datetime, timedelta
import csv
import random

from src.config import Config
from src.stock import StockDriver
from src.robot import Robot
from src.ai import Pool


class Simulator:
    def __init__(self):

        # Get date and time information
        today = date.today()
        self.current_datetime = datetime(today.year, today.month, today.day-3, 9, 30)
        random.seed(datetime.now())

        # Load config file
        self.config = Config.get_config()

        # Define subset of stocks to use for simulation
        self.stock_list_string = "('NVDA', 'ABBV', 'DISCA')"
        self.stock_list = ['NVDA', 'ABBV', 'DISCA']
        self.stock_data = defaultdict(lambda: {})
        self.stock_data_clean = defaultdict(lambda: {})
        self.driver = StockDriver()
        self.inputs = []

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
            self.add_robot(genome, random.choice(self.names) + str(i))

        self.simulate()

    def add_robot(self, genome, name="Robot"):

        self.robot_list.append(Robot(self, genome, name))

    def set_datetime(self, current_datetime):

        self.current_datetime = current_datetime

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
        for stock in self.stock_data:
            last_time = self.current_datetime
            clean_time = last_time + timedelta(minutes=5)
            while clean_time.time() < time(16):
                last_price = self.stock_data[stock][last_time.time()][3]
                price = self.stock_data[stock][clean_time.time()][3]
                delta = price - last_price
                self.stock_data_clean[stock][clean_time.time()] = delta / last_price
                last_time = clean_time
                clean_time += timedelta(minutes=5)

    def simulate(self):

        total = []

        for generation in range(Config.get_config()['POPULATION'].getint('generations')):
            # TO-DO: remove this duplicate code
            today = date.today()
            self.current_datetime = datetime(today.year, today.month, today.day, 9, 30)
            self.current_datetime += timedelta(hours=1, minutes=5)

            while self.current_datetime.time() < time(16):
                self.update_inputs()
                for robot in self.robot_list:
                    robot.simulate(self.stock_list)

                self.current_datetime += timedelta(minutes=5)

            total = []
            for robot in self.robot_list:
                robot.display()
                robot.genome.fitness = float(robot.balance)
                total += [(robot.name, robot.balance)]
            total.sort(key=lambda x: x[1])
            # Testing value
            best_was = total[-1][0]

            self.pool.generation_stats()
            self.pool.new_generation()
            new_genomes = self.pool.all_genomes()
            self.robot_list = [robot for robot in self.robot_list if robot.is_alive()]
            for robot in self.robot_list:
                robot.reset()
            for i in range(len(new_genomes)):
                if new_genomes[i].status == 0:
                    self.add_robot(new_genomes[i], random.choice(self.names)+str(i))

        # ------------------------------------
        # Testing
        self.current_datetime = datetime(today.year, today.month, today.day-2, 9, 30)
        self.current_datetime -= timedelta(days=1)
        self.get_stock_data()
        self.current_datetime += timedelta(hours=1, minutes=5)

        while self.current_datetime.time() < time(16):
            self.update_inputs()
            for robot in self.robot_list:
                robot.simulate(self.stock_list)

            self.current_datetime += timedelta(minutes=5)

        total = []
        for robot in self.robot_list:
            #robot.display()
            robot.genome.fitness = float(robot.balance)
            total += [(robot.name, robot.balance)]
        total.sort(key=lambda x: x[1])

        # ------------------------------------

        self.pool.generation_stats()
        for i in total:
            print(i)
        # Testing value
        print(best_was)

    def get_inputs(self):
        return self.inputs[:]

    def update_inputs(self):
        self.inputs = []
        quick_time = self.current_datetime - timedelta(hours=1)
        for stock in self.stock_list:
            for _ in range(12):
                self.inputs.append(float(self.stock_data_clean[stock][quick_time.time()]))

    def get_stock_info(self, stock):

        return self.stock_data[stock][self.current_datetime.time()]

    def get_ask_price(self, stock):

        return self.stock_data[stock][self.current_datetime.time()][3]

    def get_bid_price(self, stock):

        return self.stock_data[stock][self.current_datetime.time()][5]


s = Simulator()
