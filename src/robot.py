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
        self.overbuy = 0

    def reset(self):
        self.balance = self.original_balance
        self.cash = self.balance
        self.stocks = defaultdict(lambda: 0)
        self.overbuy = 0

    # buy as many shares of stock as can afford up to amount
    def buy(self, stock, amount):

        # get stock price
        price = self.simulator.get_ask_price(stock)

        # calculate buy amount based on price
        buy_cash = Decimal(amount) * self.balance
        buy_amount = int(buy_cash / price)

        # determine total price and buyability
        while buy_amount > 0 and buy_amount * price > self.cash:
            buy_amount -= 1
            self.overbuy += 1

        # buy stocks
        if Config.is_debug_mode() and buy_amount != 0:
            print("Buying {} shares of {} for {} each, total {}".format(buy_amount, stock, price, price * buy_amount))
        self.stocks[stock] += buy_amount
        self.cash -= buy_amount * price

        # update balance
        self.update_balance()

    # sell up to amount of a given stock
    def sell(self, stock, amount):

        # get bid price
        price = self.simulator.get_bid_price(stock)

        # calculate sell amount based on price and balance
        sell_value = Decimal(amount) * self.balance
        sell_amount = int(sell_value / price)

        while sell_amount > 0 and sell_amount > self.stocks[stock]:
            sell_amount -= 1
            self.overbuy += 1

        # sell stocks
        if Config.is_debug_mode() and sell_amount != 0:
            print("Selling {} shares of {} for {} each, total {}".format(sell_amount, stock, price, price * sell_amount))
        self.stocks[stock] -= sell_amount
        self.cash += price * sell_amount

        # update balance
        self.update_balance()

    # recalculate this robot's balance
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
        print("Percent Change: ", self.calculate_change()*100, "%")
        print("Cash: ", self.cash)
        print("Overbuy: ", self.overbuy)
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

        self.update_balance()

        for i, stock in enumerate(stock_list):
            if outputs[i] < 0:
                self.sell(stock, abs(outputs[i]))
            if outputs[i] > 0:
                self.buy(stock, outputs[i])

    def is_alive(self):
        if self.genome and self.genome.status == 1:
            return True
        return False
