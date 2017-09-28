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
		self.stock_list = ['MMM','ABT','ABBV','ACN','ATVI','AYI','ADBE','AMD','AAP','AES','AET','AMG','AFL','A','APD','AKAM','ALK','ALB','ARE','ALXN','ALGN','ALLE','AGN','ADS','LNT','ALL','GOOGL','GOOG','MO','AMZN','AEE','AAL','AEP','AXP','AIG','AMT','AWK','AMP','ABC','AME','AMGN','APH','APC','ADI','ANDV','ANSS','ANTM','AON','AOS','APA','AIV','AAPL','AMAT','ADM','ARNC','AJG','AIZ','T','ADSK','ADP','AZO','AVB','AVY','BHGE','BLL','BAC','BK','BCR','BAX','BBT','BDX','BRK.B','BBY','BIIB','BLK','HRB','BA','BWA','BXP','BSX','BHF','BMY','AVGO','BF.B','CHRW','CA','COG','CDNS','CPB','COF','CAH','CBOE','KMX','CCL','CAT','CBG','CBS','CELG','CNC','CNP','CTL','CERN','CF','SCHW','CHTR','CHK','CVX','CMG','CB','CHD','CI','XEC','CINF','CTAS','CSCO','C','CFG','CTXS','CLX','CME','CMS','COH','KO','CTSH','CL','CMCSA','CMA','CAG','CXO','COP','ED','STZ','COO','GLW','COST','COTY','CCI','CSRA','CSX','CMI','CVS','DHI','DHR','DRI','DVA','DE','DLPH','DAL','XRAY','DVN','DLR','DFS','DISCA','DISCK','DISH','DG','DLTR','D','DOV','DWDP','DPS','DTE','DRE','DUK','DXC','ETFC','EMN','ETN','EBAY','ECL','EIX','EW','EA','EMR','ETR','EVHC','EOG','EQT','EFX','EQIX','EQR','ESS','EL','ES','RE','EXC','EXPE','EXPD','ESRX','EXR','XOM','FFIV','FB','FAST','FRT','FDX','FIS','FITB','FE','FISV','FLIR','FLS','FLR','FMC','FL','F','FTV','FBHS','BEN','FCX','GPS','GRMN','IT','GD','GE','GGP','GIS','GM','GPC','GILD','GPN','GS','GT','GWW','HAL','HBI','HOG','HRS','HIG','HAS','HCA','HCP','HP','HSIC','HSY','HES','HPE','HLT','HOLX','HD','HON','HRL','HST','HPQ','HUM','HBAN','IDXX','INFO','ITW','ILMN','IR','INTC','ICE','IBM','INCY','IP','IPG','IFF','INTU','ISRG','IVZ','IRM','JEC','JBHT','SJM','JNJ','JCI','JPM','JNPR','KSU','K','KEY','KMB','KIM','KMI','KLAC','KSS','KHC','KR','LB','LLL','LH','LRCX','LEG','LEN','LVLT','LUK','LLY','LNC','LKQ','LMT','L','LOW','LYB','MTB','MAC','M','MRO','MPC','MAR','MMC','MLM','MAS','MA','MAT','MKC','MCD','MCK','MDT','MRK','MET','MTD','MGM','KORS','MCHP','MU','MSFT','MAA','MHK','TAP','MDLZ','MON','MNST','MCO','MS','MOS','MSI','MYL','NDAQ','NOV','NAVI','NTAP','NFLX','NWL','NFX','NEM','NWSA','NWS','NEE','NLSN','NKE','NI','NBL','JWN','NSC','NTRS','NOC','NRG','NUE','NVDA','ORLY','OXY','OMC','OKE','ORCL','PCAR','PKG','PH','PDCO','PAYX','PYPL','PNR','PBCT','PEP','PKI','PRGO','PFE','PCG','PM','PSX','PNW','PXD','PNC','RL','PPG','PPL','PX','PCLN','PFG','PG','PGR','PLD','PRU','PEG','PSA','PHM','PVH','QRVO','PWR','QCOM','DGX','Q','RRC','RJF','RTN','O','RHT','REG','REGN','RF','RSG','RMD','RHI','ROK','COL','ROP','ROST','RCL','CRM','SBAC','SCG','SLB','SNI','STX','SEE','SRE','SHW','SIG','SPG','SWKS','SLG','SNA','SO','LUV','SPGI','SWK','SBUX','STT','SRCL','SYK','STI','SYMC','SYF','SNPS','SYY','TROW','TGT','TEL','FTI','TXN','TXT','TMO','TIF','TWX','TJX','TMK','TSS','TSCO','TDG','TRV','TRIP','FOXA','FOX','TSN','UDR','ULTA','USB','UA','UAA','UNP','UAL','UNH','UPS','URI','UTX','UHS','UNM','VFC','VLO','VAR','VTR','VRSN','VRSK','VZ','VRTX','VIAB','V','VNO','VMC','WMT','WBA','DIS','WM','WAT','WEC','WFC','HCN','WDC','WU','WRK','WY','WHR','WMB','WLTW','WYN','WYNN','XEL','XRX','XLNX','XL','XYL','YUM','ZBH','ZION','ZTS']

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

