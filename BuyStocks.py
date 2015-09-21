import sys
import json
import sqlite3
from googlefinance import getQuotes

def buy_stocks(con):
	ticker = raw_input("\nEnter the ticker symbol of the stock you wish to purchase: ").upper()
	price = getPrice(ticker)
	goahead = raw_input("\nThe last trade price of this stock was " + str(price) + ".  Do you wish to purchase shares of this stock? ")
	if goahead != 'y' and goahead != 'yes':
		print "No stocks will be purchased."
		return
	number = int(raw_input("How many shares do you wish to purchase? "))
	total_price = float(number) * price

	with con:
		cur = con.cursor()
		cur.execute("SELECT TotalCashOnHand FROM Money ORDER BY ID DESC LIMIT 1") 
		current_cash = float(cur.fetchone()[0])
		if (current_cash - total_price) < 0.0:
			print "\nYou cannot make this purchase.  You are trying to purchase $" + str(total_price) + " worth of stocks, but you only have $" + str(current_cash) + " on hand."
			return
		current_price = getPrice(ticker)
		current_value = current_price * float(number)
		cur.execute("INSERT INTO Purchases(TickerSymbol, PurchasePrice, NumberOfShares, TotalPurchasePrice, CurrentPrice, CurrentTotalValue) VALUES (?, ?, ?, ?, ?, ?)", (ticker, price, number, total_price, current_price, current_value,))
		total_money = current_cash - total_price
		cur.execute("INSERT INTO Money(TotalCashOnHand) VALUES (?)", (total_money,))
		print "\nStock successfully purchased."

def getPrice(ticker):
	parse = json.loads(json.dumps(getQuotes(str(ticker)), indent=2))
	return float(parse[0]['LastTradePrice'])
