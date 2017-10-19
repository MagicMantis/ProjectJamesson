# Title: Stock Robot
# Author: Joseph Savold
# Purpose: A Robot that can play the stock market

from collections import defaultdict
import random
import time
from decimal import *
from src.ai import Genome
from src.config import Config

class Robot:
    def __init__(self, simulator, genome, name="Robot"):
        self.simulator = simulator
        self.name = name
        self.balance = Decimal(self.simulator.config['STOCK']['start_balance'])
        self.original_balance = self.balance
        self.cash = self.balance
        self.stocks = defaultdict(lambda: 0)
        self.genome = genome
        self.genome.status = 1

    def reset(self):
        self.balance = self.original_balance
        self.cash = self.balance
        self.stocks = defaultdict(lambda: 0)

    # buy as many shares of stock as can afford up to amount
    def buy(self, stock, amount):

        # get stock price
        price = self.simulator.get_ask_price(stock)

        # determine total price and buyability
        while amount * price > self.cash:
            amount -= 1

        # buy stocks
        if Config.is_debug_mode():
            print("Buying {} shares of {} for {} each, total {}".format(amount, stock, price, price * amount))
        self.stocks[stock] += amount
        self.cash -= amount * price

        # update balance
        self.update_balance()

    # sell up to amount of a given stock
    def sell(self, stock, amount):

        # get bid price
        price = self.simulator.get_bid_price(stock)

        while amount > self.stocks[stock]:
            amount -= 1

        # sell stocks
        if Config.is_debug_mode():
            print("Selling {} shares of {} for {} each, total {}".format(amount, stock, price, price * amount))
        self.stocks[stock] -= amount
        self.cash += price * amount

        # update balance
        self.update_balance()

    # recalcuate this robot's balance
    def update_balance(self):

        self.balance = self.cash

        for stock in self.stocks:
            price = self.simulator.get_bid_price(stock)
            self.balance += price * self.stocks[stock]

    # calculate the percent change between current balance and a given value
    def calculate_change(self):

        return (self.balance / self.original_balance) - 1

    # print details about this robot's performance and status
    def display(self):

        print("Name: ", self.name)
        print("Balance: ", self.balance)
        print("Percent Change: ", self.calculate_change(), "%")
        print("Cash: ", self.cash)
        for stock in self.stocks:
            print("\t{}: {}".format(stock, self.stocks[stock]))

    def get_positions(self, stock_list):
        # Update balance for accurate calculation of positions
        self.update_balance()

        positions = []
        for stock in stock_list:
            price = self.simulator.get_bid_price(stock)
            positions.append(float(price / self.balance))
        positions.append(float(self.cash / self.balance))
        return positions

    def simulate(self, stock_list):

        inputs = self.simulator.get_inputs()
        inputs += self.get_positions(stock_list)
        network = self.genome.generate_network()
        outputs = network.evaluate(inputs, Config.is_debug_mode())

        for i, stock in enumerate(stock_list):
            if outputs[i] < 0:
                self.sell(stock, 1)
            if outputs[i] > 0:
                self.buy(stock, 1)

    def is_alive(self):
        if self.genome and self.genome.status == 1:
            return True
        return False
