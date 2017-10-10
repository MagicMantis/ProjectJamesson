# Title: Stock Driver
# Author: Joseph Savold
# Collects stock info and saves to database, acts as primary interface for the database

from Robinhood import Robinhood
import mysql.connector
from datetime import datetime


class StockDriver:
    def __init__(self):
        self.stock_list = []

    # open connection to the database
    def connect_to_db(self):
        conn = mysql.connector.connect(
            user='python',
            password='PyPass999!',
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

    def get_ask_price(self, stock):

        conn = self.connect_to_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT stockAskPrice FROM snapshots WHERE stockKey = '{}' ORDER BY targetDateTime DESC LIMIT 1;".format(
                stock))
        price = cursor.fetchone()[0]
        conn.close()
        return price

    def get_bid_price(self, stock):

        conn = self.connect_to_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT stockBidPrice FROM snapshots WHERE stockKey = '{}' ORDER BY targetDateTime DESC LIMIT 1;".format(
                stock))
        price = cursor.fetchone()[0]
        conn.close()
        return price

    # take the data from all stocks in stock_list at the specified datetime
    def take_snapshot(self, target_date):
        data = self.get_stock_info()
        conn = self.connect_to_db()
        cursor = conn.cursor()
        for i in range(len(data)):
            if (data[i][1] == None):
                print("No data for: data[i][0]")
                continue
            sql_string = ("INSERT INTO snapshots (stockKey, targetDateTime, stockAskPrice, stockAskSize, " +
                          "stockBidPrice, stockBidSize, stockLastTradePrice, stockPreviousClosePrice, "
                          "stockPreviousCloseDate, " +
                          "stockTradingHalted, stockHasTraded, stockLastTradePriceSource) VALUES ('{0}', '{1}', " +
                          "'{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}');")
            sql_string = sql_string.format(data[i][0], target_date, data[i][1]['ask_price'],
                                           data[i][1]['ask_size'], data[i][1]['bid_price'], data[i][1]['bid_size'],
                                           data[i][1]['last_trade_price'], data[i][1]['previous_close'],
                                           data[i][1]['previous_close_date'], data[i][1]['trading_halted'],
                                           data[i][1]['has_traded'], data[i][1]['last_trade_price_source'])
            cursor.execute(sql_string)
        conn.commit()
        conn.close()
