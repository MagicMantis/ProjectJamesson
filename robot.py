# Title: Stock Robot
# Author: Joseph Savold
# Purpose: A Robot that can play the stock market

from collections import defaultdict
import random
import time

class Robot:

	def __init__(self, simulator, name = "Robot"):
		self.simulator = simulator
		self.name = name
		self.balance  = 1000
		self.original_balance = self.balance
		self.cash = self.balance
		self.stocks = defaultdict(lambda: 0)

		random.seed(time.time())

	# buy as many shares of stock as can afford up to amount
	def buy(self, stock, amount):
		
		# get stock price
		price = self.simulator.get_ask_price(stock)

		# determine total price and buyability
		while amount*price > self.balance: 
			amount -= 1
		
		# buy stocks
		print "Buying {} shares of {} for {} each, total {}".format(amount, stock, price, price*amount)
		self.stocks[stock] += amount
		self.cash -= amount*price

		# update balance
		self.update_balance()

	# sell up to amount of a given stock
	def sell(self, stock, amount):

		# get bid price
		price = self.simulator.get_bid_price(stock)

		while (amount > self.stocks[stock]): amount -= 1

		# sell stocks
		print "Selling {} shares of {} for {} each, total {}".format(amount, stock, price, price *amount)
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
		
		return ((self.balance / self.original_balance) - 1)

	# print details about this robot's performance and status
	def display(self):

		print "Name: ", self.name
		print "Balance: ", self.balance
		print "Percent Change: ", self.calculate_change(), "%"
		print "Cash: ", self.cash
		for stock in self.stocks:
			print "\t{}: {}".format(stock,self.stocks[stock])

	def simulate(self, stock_list):

		for stock in stock_list:
			amt = random.randint(-2,2)
			if amt < -1: self.sell(stock, 1)
			if amt > 1: self.buy(stock, 1)
