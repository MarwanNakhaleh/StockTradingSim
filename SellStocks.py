import sys
import json
import sqlite3
from googlefinance import getQuotes

def sell_stocks(con):
	# You can only sell one stock at a time
	ticker = raw_input("\nEnter the ticker symbol of the stock you wish to sell: ").upper()
	stocks = json.loads(json.dumps(getQuotes(ticker), indent=2))
	with con:
		con.row_factory = sqlite3.Row
		cur = con.cursor()
		# Search for the ticker symbol
		cur.execute("SELECT * FROM Purchases WHERE TickerSymbol=?", (ticker,))
		ticker_stocks = cur.fetchall()
		# Declare idee for use outside of the following block		
		idee = 0
		# If there is more than one lot
		if len(ticker_stocks) > 1:
			print "You have multiple lots of " + ticker + ".  Which lot do you want to sell from?"
			print ""
			# Get the current price of the stock
			price = getPrice(ticker)
			for r in ticker_stocks:
				# Get the number of shares for each lot
				cur.execute("SELECT NumberOfShares FROM Purchases WHERE TickerSymbol=?", (ticker,)) 
				nos = float(cur.fetchone()[0])
				# Get the current total value of each lot
				ctv = price * nos
				# Update the current price and the current total value to reflect differences since last time they were checked
				cur.execute("UPDATE Purchases SET CurrentPrice=? WHERE TickerSymbol=?", (price, r["TickerSymbol"],))
				cur.execute("UPDATE Purchases SET CurrentTotalValue=? WHERE TickerSymbol=?", (ctv, r["TickerSymbol"],))
				# Save changes
				con.commit()
				# Print the row, including the ID, so the user can select which lot they wanna sell from
				print "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (r["Id"], r["TickerSymbol"], r["PurchasePrice"], r["NumberOfShares"], r["TotalPurchasePrice"], r["CurrentPrice"], r["CurrentTotalValue"])
				# Prompt user for ID
			idee = int(raw_input("\nType in the ID number of the lot you want to sell from: "))
		# Or if there are no lots of the ticker symbol		
		elif len(ticker_stocks) == 0:
			print "\nYou do not have any shares of " + ticker + "."
			return
		# Get the current price of the stock
		price = getPrice(ticker)
		goahead = raw_input("\nThe last trade price of this stock was " + str(price) + ".  Do you wish to sell shares of this stock? ")
		if goahead != 'y' and goahead != 'yes':
			print "No stocks will be sold."
			return
		# Prompt for the number of shares to sell
		number_sell = int(raw_input("How many shares do you wish to sell? "))	
		# Search by ID if the number of lots of that ticker is more than one
		if len(ticker_stocks) > 1:
			cur.execute("SELECT NumberOfShares FROM Purchases WHERE Id=? AND TickerSymbol=?", (idee, ticker,))
		# Just select by ticker symbol if there is only one lot 
		else:
			cur.execute("SELECT NumberOfShares FROM Purchases WHERE TickerSymbol=?", (ticker,))
		# Get the number of shares from the query		
		nos = float(cur.fetchone()[0])
		# Don't sell if you're trying to sell more shares than you have
		if int(nos) < number_sell:
			print "\nYou cannot sell more shares of a stock than you have in a lot!"
			return
		# Change the number of shares
		total_shares = int(nos) - number_sell
		# Make sure you're updating the right lot if you have multiple lots
		if len(ticker_stocks) > 1:
			cur.execute("UPDATE Purchases SET NumberOfShares=? WHERE Id=? AND TickerSymbol=?", (total_shares, idee, ticker,))
		else:
			cur.execute("UPDATE Purchases SET NumberOfShares=? WHERE TickerSymbol=?", (total_shares, ticker,))
		# Calculate how much money you have
		cur.execute("SELECT TotalCashOnHand FROM Money ORDER BY Id DESC LIMIT 1") 
		current_cash = float(cur.fetchone()[0])
		total_cash = current_cash + float(getPrice(ticker)) * number_sell
		# Update the amount in your Money table
		cur.execute("INSERT INTO Money(TotalCashOnHand) VALUES (?)", (total_cash,)) 
		# Delete the row if there are no shares in the lot
		if total_shares == 0:
			# Delete the correct row if there is more than one lot of a ticker symbol
			if len(ticker_stocks) > 1:
				cur.execute("DELETE FROM Purchases WHERE Id=? AND TickerSymbol=?", (idee, ticker,))
			else:
				cur.execute("DELETE FROM Purchases WHERE TickerSymbol=?", (ticker,))
			# Save changes
			con.commit()
		else:
			# If there are still shares, update the info in the correct row
			if len(ticker_stocks) > 1:
				# Get the price you paid for each stock
				cur.execute("SELECT PurchasePrice FROM Purchases WHERE Id=? AND TickerSymbol=?", (idee, ticker,)) 
				old_price = float(cur.fetchone()[0])
				# Change the total purchase value to reflect the number of shares you still have
				total_value_old = old_price * float(total_shares)
				# Change the current total value to reflect the number of shares you still have
				ctv = getPrice(ticker) * float(total_shares)
				cur.execute("UPDATE Purchases SET TotalPurchasePrice=?, CurrentTotalValue=? WHERE Id=? AND TickerSymbol=?", (total_value_old, ctv, idee, ticker,))
			else:
				cur.execute("SELECT PurchasePrice FROM Purchases WHERE TickerSymbol=?", (ticker,)) 
				old_price = float(cur.fetchone()[0])
				total_value_old = old_price * float(total_shares)
				ctv = getPrice(ticker) * float(total_shares)
				cur.execute("UPDATE Purchases SET TotalPurchasePrice=?, CurrentTotalValue=? WHERE TickerSymbol=?", (total_value_old, ctv, ticker,))
			# Save changes
			con.commit()
		print "\nStock %s successfully sold." % ticker

def getPrice(ticker):
	parse = json.loads(json.dumps(getQuotes(str(ticker)), indent=2))
	return float(parse[0]['LastTradePrice'])
