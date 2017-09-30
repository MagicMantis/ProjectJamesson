# Title: Stock Snapshot
# Author: Joseph Savold
# Collects stock info and saves to database

from Robinhood import Robinhood
import mysql.connector
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import time
import sys
from datetime import datetime, timedelta

class StockDriver:

	def __init__(self):
		self.update_stock_list()

	# open connection to the database
	def connect_to_db(self):
		conn = mysql.connector.connect(
			user = 'root', 
			password='f9nuF66m+', 
			unix_socket='/var/run/mysqld/mysqld.sock', 
			database='stock_info'
		)
		return conn

	# get list of stocks from the database
	def update_stock_list(self):	
	
		print("Updating Stock List...")

		conn = self.connect_to_db();
		cursor = conn.cursor()
		cursor.execute("SELECT stockKey FROM stocks;")

		# format them into a list
		self.stock_list = []
		for entry in cursor:
			self.stock_list.append(entry[0])

		conn.close()
	
	# get stock info from Robinhood module
	def get_stock_info(self):

		print("Getting stock data from Robinhood")

		trader = Robinhood()
		quotes = zip(self.stock_list, trader.quotes_data(self.stock_list))
		return quotes

	# take the data from all stocks in stock_list at the specified datetime
	def take_snapshot(self, target_date):
		data = self.get_stock_info()
		conn = self.connect_to_db()
		cursor = conn.cursor()
		for i in range(len(data)):
			if (data[i][1] == None):
				print ("No data for: data[i][0]")
				continue
			sql_string = ("INSERT INTO snapshots (stockKey, targetDateTime, stockAskPrice, stockAskSize, " + 
				"stockBidPrice, stockLastTradePrice, stockPreviousClosePrice, stockPreviousCloseDate, " + 
				"stockTradingHalted, stockHasTraded, stockLastTradePriceSource) VALUES ('{0}', '{1}', " + 
				"'{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}');")
			sql_string = sql_string.format(data[i][0],target_date,data[i][1]['ask_price'],
				data[i][1]['ask_size'],data[i][1]['bid_price'],data[i][1]['bid_size'],
				data[i][1]['last_trade_price'],data[i][1]['previous_close'],
				data[i][1]['previous_close_date'],data[i][1]['trading_halted'],
				data[i][1]['has_traded'],data[i][1]['last_trade_price_source'])
			cursor.execute(sql_string)
		conn.commit()
		conn.close()


class Runner:

	def __init__(self):
		
		logging.basicConfig()
		self.driver = StockDriver()
		self.sched = BackgroundScheduler()

		# run schedule daily jobs everyweek day at 8
		self.sched.add_job(self.plan_day, 'cron', day_of_week='0-4', hour='8', args=[])
		self.sched.start()

		# run plan day to catch any remaining (in case of late start)
		n = datetime.now()
		if (n.hour > 8 or (n.hour == 8 and (n.minute > 0 or n.second > 0))):
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
		print "Planning day for ", t
		first_time = datetime(t.year,t.month,t.day,9,30)
		delta = timedelta(minutes = 0)

		# update stock_list
		self.driver.update_stock_list()	

		# schedule a snapshot for every 5 minutes between 9:30 and 4:00
		for i in range(300):
			self.sched.add_job(self.driver.take_snapshot, 'date', 
				run_date=(first_time + delta), args=[(first_time+delta)])
			delta += timedelta(minutes = 5)

Runner()
