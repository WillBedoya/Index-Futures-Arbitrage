from ib_insync import IB, Future, Stock, LimitOrder, util, Order, OrderStatus, MarketOrder
from datetime import datetime
from math import isnan
import yfinance as yf
import numpy as np
import logging
import math

# Configure logging (optional)
#logging.basicConfig(level=logging.INFO)

# Define the contract (example: ES Future)
contracts = []
stock_contracts = []

# Initialize futures contract inventory
q = 0

def is_valid_price(price):
    return price is not None and not math.isnan(price)

def round_to_nearest_whole(n):
    return round(n * 1) / 1

def round_to_nearest_quarter(n):
    return round(n * 4) / 4

def round_to_nearest_cent(n):
    return round(n * 100) / 100

def front_month_futures_fair_value(cash_index, r, d, dte):
    return cash_index * (1 + (r / 100) * (dte / 360)) - d * cash_index * (dte / 360) # Assuming r is the 13-month T-bill rate

def second_month_futures_fair_value(cash_index, r, d, dte):
    return cash_index * (1 + (r / 100) * ((dte + 90) / 360)) - d * cash_index * ((dte + 90) / 360) # Assuming r is the 13-month T-bill rate

def days_until_expiration(expiration_date):
    # Current date
    current_date = datetime.now()
    
    # Convert expiration date string to datetime object
    expiration_datetime = datetime.strptime(expiration_date, "%Y-%m-%d")
    
    # Calculate the difference
    delta = expiration_datetime - current_date
    
    # Return the number of days left as a whole number
    return max(delta.days, 0)  # Return 0 if the expiration date has passed

def main():
    # Initialize and connect to IB
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)

    # Define the contract (example: ES Future)
    futures_contract = Future('YM', '202403', 'CBOT')
    contracts.append(futures_contract)
    
    for contract in contracts:
        # Request market data
        ib.reqMktData(contract, '', False, False)
        
        buy_order = None
        sell_order = None
        
        dow_stocks = ['AMZN', 'AXP', 'AMGN', 'AAPL', 'BA', 
                      'CAT', 'CSCO', 'CVX', 'GS', 'HD', 
                      'HON', 'IBM', 'INTC', 'JNJ', 'KO', 
                      'JPM', 'MCD', 'MMM', 'MRK', 'MSFT', 
                      'NKE', 'PG', 'TRV', 'UNH', 'CRM', 
                      'VZ', 'V', 'WMT', 'DIS', 'DOW']
        
        for stock in dow_stocks:
            stock_contract = Stock(stock, 'SMART', 'USD')
            ib.reqMktData(stock_contract, '', False, False)
            stock_contracts.append(stock_contract)

        try:
            while True:
                # Initialize index cash
                cash_index_bid = 0
                cash_index_ask = 0

                # Get the current market data
                ticker = ib.ticker(contract)

                # Ensure we have valid bid and ask prices
                if is_valid_price(ticker.bid) and is_valid_price(ticker.ask):

                    # Update inventory
                    positions = ib.reqPositions()
                    for position in positions:
                        if position.contract.symbol == contract.symbol and position.contract.secType == contract.secType:
                            q = position.position
                            print(f"\nPosition for {contract.symbol}: {q}")
    
                    # Get current 13-week T-bill rate
                    risk_free_rate = yf.Ticker("^IRX").history()['Close'].iloc[-1]

                    # Input current DJI dividend rate (IBKR does not provide)
                    DJI_dividend = 0.0176

                    for i in range(0, len(dow_stocks)):
                        price = ib.ticker(stock_contracts[i])
                        #if is_valid_price(price.bid) and is_valid_price(price.ask):
                        cash_index_bid += price.bid
                        cash_index_ask += price.ask
                            
                    if is_valid_price(price.bid) and is_valid_price(price.ask):
                        cash_index_bid /= 0.15265312230608
                        #print(f"{cash_index_bid}")
                        cash_index_ask /= 0.15265312230608
                        #print(f"{cash_index_ask}")
                        
                        # Calculcate futures fair value
                        expiration_date = "2024-03-15"
                        days_until_exp = days_until_expiration(expiration_date) # days left until expiration
                        futures_fair_value_bid = front_month_futures_fair_value(cash_index_bid, risk_free_rate, DJI_dividend, days_until_exp)
                        futures_fair_value_ask = front_month_futures_fair_value(cash_index_ask, risk_free_rate, DJI_dividend, days_until_exp)

                        # Obtain the list of open orders
                        open_orders = ib.openOrders()
                        # Cancel each order
                        for order in open_orders:
                            ib.cancelOrder(order)
                        
                        if is_valid_price(price.bid) and is_valid_price(price.ask):
                            # Print out current futures fair values and futures values
                            print(f"Futures real bid: {ticker.bid}")
                            print(f"Futures fair value ask: {futures_fair_value_ask}")
                            print(f"Futures real ask: {ticker.ask}")
                            print(f"Futures fair value bid: {futures_fair_value_bid}")

                            print(f"Back month futures fair value bid: {second_month_futures_fair_value(cash_index_bid, risk_free_rate, DJI_dividend, days_until_exp)}")
                            print(f"Back month futures fair value ask: {second_month_futures_fair_value(cash_index_ask, risk_free_rate, DJI_dividend, days_until_exp)}")

                            # Only offer to go short futures if we are currently long them or neutral
                            if q >= 0:
                                if ticker.bid - 3.50 > futures_fair_value_ask: # Slight buffer due to rounding errors plus transaction costs
                                    for i in range(0, len(dow_stocks)):
                                        price = ib.ticker(stock_contracts[i])
                                        buy_order = MarketOrder('BUY', 1)
                                        ib.placeOrder(stock_contracts[i], buy_order)

                                    sell_order = MarketOrder('SELL', 1)
                                    ib.placeOrder(contract, sell_order)
                                    
                            # Only offer to go long futures if we are currently short them or neutral
                            if q <= 0:
                                if futures_fair_value_bid - 3.50 > ticker.ask: # Slight buffer due to rounding errors plus transaction costs
                                    for i in range(0, len(dow_stocks)):
                                        price = ib.ticker(stock_contracts[i])
                                        sell_order = MarketOrder('SELL', 1)
                                        ib.placeOrder(stock_contracts[i], sell_order)

                                    buy_order = MarketOrder('BUY', 1)
                                    ib.placeOrder(contract, buy_order)
                
                # Sleep to throttle the loop (adjust as needed)
                ib.sleep(0.05)

        except KeyboardInterrupt:
            print("Disconnecting and exiting...")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            ib.disconnect()

if __name__ == '__main__':
    main()