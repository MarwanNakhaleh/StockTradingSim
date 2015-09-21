#!/usr/bin/python

import sqlite3
import sys

remove = raw_input('Are you sure you want to reset your database?\n')
if remove != 'yes' and remove != 'y':
	print "Nothing will be deleted."
	sys.exit()

con = sqlite3.connect('stock_info.db')

with con:
	cur = con.cursor()

	cur.execute("DROP TABLE IF EXISTS Watchlist")
	cur.execute("CREATE TABLE Watchlist(Id INTEGER PRIMARY KEY AUTOINCREMENT, \
			 TickerSymbol TEXT, \
			 CurrentPrice NUMERIC, \
			 ChangeFromYesterday NUMERIC)")

	cur.execute("DROP TABLE IF EXISTS Purchases")
	cur.execute("CREATE TABLE Purchases(Id INTEGER PRIMARY KEY, \
			TickerSymbol TEXT, \
			PurchasePrice NUMERIC, \
			NumberOfShares INTEGER, \
			TotalPurchasePrice NUMERIC, \
			CurrentPrice NUMERIC, \
			CurrentTotalValue NUMERIC)")
	
	cur.execute("DROP TABLE IF EXISTS Money")
	cur.execute("CREATE TABLE Money(Id INT PRIMARY KEY, TotalCashOnHand NUMERIC)")
	cur.execute("INSERT INTO Money(TotalCashOnHand) VALUES (10000)")

	print "Database, watchlist, and initial investment reset."
