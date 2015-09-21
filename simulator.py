from googlefinance import getQuotes
from yahoo_finance import Share
from datetime import date, timedelta
import json
import sys
import sqlite3

from BuyStocks import buy_stocks
from SellStocks import sell_stocks

version = "0.1"
db_name = "stock_info.db"

def main():
	# Connect to database
	con = sqlite3.connect(db_name)
	# Give the user some choices
	choice = raw_input("\nThis is StockSim v%s.  What would you like to do?  \nType 'pw' to print your watched stocks\nType 'aw' to add to your watched stocks\nType 'rw' to remove from your watched stocks\nType 'ps' to print your purchased stocks\nType 'bs' to buy a stock\nType 'ss' to sell a stock\nType 'm' to print how much cash you have left to buy stocks\nType 'a' to see how much you have in total assets\nType 'q' or 'exit' to exit: " % version).lower()
	# Choices
	if choice == 'pw':	# Print watchlist
		print_watch(con)
	elif choice == 'aw':	# Add to watchlist
		add_watch(con)
	elif choice == 'rw':	# Remove from watchlist
		remove_watch(con)
	elif choice == 'ps':	# Print stock list
		print_stocks(con)
	elif choice == 'bs':	# Buy stocks
		buy_stocks(con)
	elif choice == 'ss':	# Sell stocks
		sell_stocks(con)
	elif choice == 'm':
		print_money(con)
	elif choice == 'a':
		print_assets(con)
	elif choice == 'q' or choice == 'exit':				# Quit
		print "\nThank you.  Have a good day!\n"
		sys.exit()
	else:
		print "\nThat choice is not recognized.  Try again.\n"	# Error
		main()
	main()
	
def print_watch(con):
	with con:
		# Create rows
		con.row_factory = sqlite3.Row
		cur = con.cursor()
		cur.execute("SELECT * FROM Watchlist")
		# Get all rows		
		rows = cur.fetchall()
		print ""
		for r in rows:
			# Print the watchlist
			price = getPrice(r["TickerSymbol"])
			delta = price - getYesterdayPrice(r["TickerSymbol"])
			cur.execute("UPDATE Watchlist SET CurrentPrice=? WHERE TickerSymbol=?", (price, r["TickerSymbol"]))
			cur.execute("UPDATE Watchlist SET ChangeFromYesterday=? WHERE TickerSymbol=?", (delta, r["TickerSymbol"]))
			con.commit()	# Commit updates
			print "%s\t%s\t%s\t" % (r["TickerSymbol"], r["CurrentPrice"], r["ChangeFromYesterday"])
		# Go back to main()
		main()

def add_watch(con):
	# Create a list of stocks to add
	additions = list()
	# Prompt for ticker symbols
	add = raw_input("\nEnter ticker symbols to add to your watchlist here, ending with '0': ")
	while add != '0':
		additions.append(add)
		add = raw_input()
	print ""	
	# Add each ticker to the watchlist
	for x in xrange(0, len(additions)):
		ticker = additions[x] 
		price = getPrice(ticker)			# This would be a good place for a try/catch block
		# Get change since yesterday		
		delta = price - getYesterdayPrice(ticker)	
		with con:
			cur = con.cursor()
			# Make sure there isn't already a watchlist entry for that ticker symbol
			cur.execute("SELECT * FROM Watchlist WHERE TickerSymbol=?", (ticker,))
			data = cur.fetchall()
			if len(data) == 0:
				# Put ticker symbol in watchlist if it wasn't already in there
				cur.execute("INSERT INTO Watchlist (TickerSymbol, CurrentPrice, ChangeFromYesterday) VALUES (?, ?, ?)", (ticker, price, delta))
				con.commit()
				print "Stock %s successfully added to watchlist." % ticker
			else:
				print "\nThat ticker symbol is already in the table.\n"
				main()
	main()

def remove_watch(con):
	# Create a list of ticker symbols to remove
	removals = list()
	# Prompt for user input
	delete = raw_input("\nEnter ticker symbols to delete from your watchlist here, ending with '0': ")
	while delete != '0':
		removals.append(delete)
		delete = raw_input()
	print ""	
	# Remove each ticker symbol entry in the entered list
	for x in xrange(0, len(removals)):
		with con:
			cur = con.cursor()
			# Search for a row in Watchlist with the ticker symbol
			cur.execute("SELECT * FROM Watchlist WHERE TickerSymbol=?", (removals[x],))
			data = cur.fetchall()
			# Only remove if there is actually something to remove
			if len(data) == 1:
				cur.execute("DELETE FROM Watchlist WHERE TickerSymbol=?", (removals[x],))
				con.commit()
				print "Stock %s successfully removed from watchlist." % removals[x]
	# Go back to main()
	main()

def print_stocks(con):
	with con:
		con.row_factory = sqlite3.Row
		cur = con.cursor()
		cur.execute("SELECT * FROM Purchases")
		rows = cur.fetchall()
		print ""
		for r in rows:
			cur.execute("SELECT NumberOfShares FROM Purchases WHERE Id=?", (r["Id"],)) 
			nos = float(cur.fetchone()[0])
			ctv = getPrice(r["TickerSymbol"]) * nos
			cur.execute("UPDATE Purchases SET CurrentPrice=? WHERE TickerSymbol=?", (getPrice(r["TickerSymbol"]), r["TickerSymbol"]))
			cur.execute("UPDATE Purchases SET CurrentTotalValue=? WHERE Id=?", (ctv, r["Id"]))
			con.commit()
			print "%s\t%s\t%s\t%s\t%s\t%s" % (r["TickerSymbol"], r["PurchasePrice"], r["NumberOfShares"], r["TotalPurchasePrice"], r["CurrentPrice"], r["CurrentTotalValue"])

		main()

def print_money(con):
	with con:
		cur = con.cursor()
		cur.execute("SELECT TotalCashOnHand FROM Money ORDER BY ID DESC LIMIT 1")
		print "\nYou have $" + str(cur.fetchone()[0]) + " left to purchase stocks."
	main()

def print_assets(con):
	with con:
		con.row_factory = sqlite3.Row
		cur = con.cursor()
		cur.execute("SELECT TotalCashOnHand FROM Money ORDER BY ID DESC LIMIT 1")
		coh = cur.fetchone()[0]
		print "\nYou have $" + str(coh) + " left to purchase stocks."
		cur.execute("SELECT CurrentTotalValue from Purchases")
		assets = cur.fetchall()
		total_stocks = 0
		for a in assets:
			total_stocks += float(a[0])
		print "You have $" + str(total_stocks) + " in stocks."
		total = coh + total_stocks
		print "You have $" + str(total) + " in total assets."
	main()

def getYesterdayPrice(ticker):
	yesterday = date.today() - timedelta(1)
	yes = str(yesterday.strftime('%Y-%m-%d'))
	stock = Share(ticker)
	parse = stock.get_historical(yes, yes)
	return float(parse[0]['Close'])

def getPrice(ticker):
	parse = json.loads(json.dumps(getQuotes(str(ticker)), indent=2))
	return float(parse[0]['LastTradePrice'])

main()

