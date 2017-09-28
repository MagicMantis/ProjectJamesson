# Title: Stock Snapshot
# Author: Joseph Savold
# Collects stock info and saves to database

from Robinhood import Robinhood
import mysql.connector
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import time
from datetime import datetime, timedelta

class stock_sql_driver:

	def __init__(self):
		self.stock_list = ['ABT', 'ABBV', 'ACN', 'ACE', 'ADBE', 'ADT', 'AAP', 'AES', 'AET', 'AFL', 'AMG', 'A', 'GAS', 'APD', 'ARG', 'AKAM', 'AA', 'AGN', 'ALXN', 'ALLE', 'ADS', 'ALL', 'ALTR', 'MO', 'AMZN', 'AEE', 'AAL', 'AEP', 'AXP', 'AIG', 'AMT', 'AMP', 'ABC', 'AME', 'AMGN', 'APH', 'APC', 'ADI', 'AON', 'APA', 'AIV', 'AMAT', 'ADM', 'AIZ', 'T', 'ADSK', 'ADP', 'AN', 'AZO', 'AVGO']

	def get_stock_info(self):

		trader = Robinhood()
		quotes = zip(self.stock_list, trader.quotes_data(self.stock_list))
		return quotes


	def take_snapshot(self, target_date):
		data = self.get_stock_info()
		conn = mysql.connector.connect(user = 'root', password='f9nuF66m+', unix_socket='/var/run/mysqld/mysqld.sock', database='stock_info')
		cursor = conn.cursor()
		for i in range(len(data)):
			if (data[i][1] == None):
				print data[i][0]
				continue
			sql_string = "INSERT INTO snapshots (stockKey, targetDateTime, stockAskPrice, stockAskSize, stockBidPrice, stockLastTradePrice, stockPreviousClosePrice, stockPreviousCloseDate, stockTradingHalted, stockHasTraded, stockLastTradePriceSource) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}');".format(data[i][0],target_date,data[i][1]['ask_price'],data[i][1]['ask_size'],data[i][1]['bid_price'],data[i][1]['bid_size'],data[i][1]['last_trade_price'],data[i][1]['previous_close'],data[i][1]['previous_close_date'],data[i][1]['trading_halted'],data[i][1]['has_traded'],data[i][1]['last_trade_price_source'])
			cursor.execute(sql_string)
			print("executed for " + data[i][0])
		conn.commit()
		conn.close()

def snap(target_date):
	snap.driver.take_snapshot(target_date)
snap.driver = stock_sql_driver()

def plan_day():
	t = datetime.today()

	#do no schedule snapshots for weekends
	if (t.weekday() >= 5): return
	
	sched = BlockingScheduler()

	first_time = datetime(t.year,t.month,t.day,8)
	delta = timedelta(minutes = 0)
	for i in range(108):
		sched.add_job(snap, 'date', run_date=(first_time + delta), args=[(first_time+delta)])
		delta += timedelta(minutes = 5)
	sched.start()

logging.basicConfig()
plan_day()

