# Title: Stock Robot
# Author: Joseph Savold
# Purpose: A Robot that can play the stock market

from collections import defaultdict
from stock import StockDriver

class Robot:

	def __init__(self, name = "Robot"):
		self.name = name
		self.balance  = 25000
		self.cash = self.balance
		self.stocks = defaultdict(lambda: 0)
		self.driver = StockDriver()
	
	# buy as many shares of stock as can afford up to amount
	def buy(self, stock, amount):
		
		# get stock price
		price = self.driver.get_ask_price(stock)
		if (price == None):
			print "Could not find price for " , stock
			return

		# determine total price and buyability
		while amount*price > self.balance: 
			amount -= 1
		
		# buy stocks
		self.stocks[stock] += amount
		self.cash -= amount*price

	# sell up to amount of a given stock
	def sell(self, stock, amount):

		# get bid price
		price = self.driver.get_bid_price(stock)

		while (amount > self.stocks[stock]): amount -= 1

		# sell stocks
		self.stocks[stock] -= amount
		self.cash += price * amount
		
		# update balance
		self.update_balance()

	# recalcuate this robot's balance
	def update_balance(self):
		
		self.balance = self.cash

		for stock in self.stocks:
			price = self.driver.get_bid_price(stock)
			self.balance += price * self.stocks[stock]

	# calculate the percent change between current balance and a given value
	def calculate_change(self, compare_val):
		
		return ((self.balance / compare_val) - 1)

	# print details about this robot's performance and status
	def display(self):

		print "Name: ", self.name
		print "Balance: ", self.balance
		print "Percent Change: ", self.calculate_change(25000), "%"
		print "Cash: ", self.cash
		for stock in self.stocks:
			print "\t{}: {}".format(stock,self.stocks[stock])


r = Robot()
r.buy('NVDA', 10)
r.sell('NVDA',2)
r.display()
