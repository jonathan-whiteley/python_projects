import sys
import random
import json
import requests

import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, date
from json.decoder import JSONDecodeError

class BitcoinAPI(): 
    """Connects to CoinDesk API for fetching bitcoin prices."""

    C_URL = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    H_URL = 'https://api.coindesk.com/v1/bpi/historical/close.json'
    today = date.today().strftime("%Y-%m-%d")
    # API powered by CoinDesk #
    
    def fetch_current_price(self, return_date = 0):
        """Fetch current price in USD using C_URL, 
        with return_date flag for flexible return value.
        """
        self.return_date = return_date
        bpi_current = requests.get(BitcoinAPI.C_URL).json()
        p = round(float(bpi_current["bpi"]["USD"]["rate"].replace(',','')),2)
        
        # Flag = 0: price, 1: date-price dictionary 
        if self.return_date == 0:
            return p
        
        if self.return_date == 1:
            #Parse and convert UTC long datetime format
            dt = datetime.strptime(bpi_current['time']['updated'],
                                   '%b %d, %Y %H:%M:%S %Z')
            d = dt.strftime('%Y-%m-%d')
            cur_price_dict = {d:p}
            return cur_price_dict
    
    def fetch_hist_price(self, start_date, end_date = today):
        """Return historical price series of bitcoin in USD, 
        date entry in YYYY-MM-DD format, data starts 2010-07-17.
        """
        self.start, self.end = start_date, end_date
        
        if self.start <= '2010-07-17':
            raise StartDateError
            
        #Uses date parameters in API call
        self.payload = {'start': self.start, 'end': self.end}
        self.bpi_hist = requests.get(BitcoinAPI.H_URL, 
                                     params = self.payload).json()
        
        return self.bpi_hist["bpi"]
        
class PriceChart(BitcoinAPI):
    """Plotting class for chart generation"""
    def __init__(self):
        super().__init__(self)
        
    def chart_btc_price(self, start_date, end_date = BitcoinAPI.today):
        """Plots historical price chart of bitcoin in USD"""
        self.start, self.end = start_date, end_date 
            
        data = self.fetch_hist_price(self.start, self.end)
    
        lists = sorted(data.items()) # Sorted list of tuples
        x, y = zip(*lists) # Unpack list into two tuples
        plt.plot(x, y)
        
        plt.xlabel('Date')
        plt.ylabel('Price per Bitcoin (USD)')
        plt.title('Price Trend of Bitcoin')
        plt.xticks([min(x), max(x)])
        
        plt.show()
        #\u20BF = unicode for Bitcoin symbol
        print("Current price/\u20BF: ${}"
              .format(self.fetch_current_price()))
        
class Account():
    """Stores account data for interacting with wallet class"""
    def __init__(self, name="satoshi nakamoto", cash=0):
        self.name = name
        self.cash = cash
        #Check starting cash is positive
        if self.cash <= 0:
            raise NegativeValueError
        self._key = str(round(
            random.random()*1000)) +'-'+ str(round(random.random()*1000))
        
class Wallet(BitcoinAPI):
    """Performs basic wallet functionality, initialized 
    with an Account object. Authentication is handled by key.
    """
    def __init__(self, account):
        self.account = account
        self.btc_balance = 0
        self.statement = []
        
    def add_cash(self, amount):
        """adds cash to account cash balance"""
        if amount <= 0:
            raise NegativeValueError
        
        self.account.cash += amount
        print('${:.2f} was added to your account cash balance.'
              .format(amount))
        print('${:.2f} is your current cash balance.'
              .format(self.account.cash))
        
    def buy_btc(self, amount_usd):
        """Purchase btc if sufficient funds"""
        
        self.amount_usd = amount_usd
        # Check if positive, then for sufficient funds 
        if self.amount_usd <= 0:
            raise NegativeValueError
        if self.amount_usd >= self.account.cash:
            raise InsufficientBalanceError
            
        # Precision is 8 decimals = smallest unit, one satoshi!
        self.account.cash -= self.amount_usd
        self.btc_purchased = round(self.amount_usd 
                                   / self.fetch_current_price(),8)
        self.btc_balance += self.btc_purchased
        
        # Append transaction to statement list
        self.statement.append(
            {"date":BitcoinAPI.today,
            "transaction":"PURCHASE", 
            "BTC": self.btc_purchased, 
            "USD": self.amount_usd *-1})
        
        print('{} \u20BF purchased for ${:.2f}'.format(
            self.btc_purchased, self.amount_usd))
        
    def sell_btc(self, amount_usd):
        """Sell btc for input amount of usd"""
        
        self.amount_usd = amount_usd
        if self.amount_usd <= 0:
            raise NegativeValueError
            
        self.btc_sold = round(self.amount_usd 
                              / self.fetch_current_price(),8)
        if self.btc_sold >= self.btc_balance:
            raise InsufficientBalanceError
            
        self.btc_balance -= self.btc_sold
        self.account.cash += self.amount_usd
        
        #append transaction to statement list
        self.statement.append(
            {"date":BitcoinAPI.today,
            "transaction":"SOLD", 
            "BTC": self.btc_sold *-1, 
            "USD": self.amount_usd})
        
        print('{} \u20BF sold for ${:.2f}'.format(
            self.btc_sold, self.amount_usd))
    
    def get_balance(self):
        print('\u20BF {} BTC balance \n$ {:.2f} USD balance'
              .format(self.btc_balance, self.account.cash))
        
    def get_statement(self):
        """Prints table containing list of transactions"""
        
        print("-"*50)
        table_title = ['date', 'transaction', '\u20BFitcoin', 'USD']
        print("{:<12s}  {:<15s}  {:<12s}  {:<12s}".format( 
          table_title[0],
          table_title[1],
          table_title[2],
          table_title[3]))

        print("-"*50)
        for item in self.statement:
            table = "{date:<12s} {tran:<15s} {btc:<12.8f} {usd:<12.2f}".format(
                date=item["date"], 
                tran=item["transaction"], 
                btc=item["BTC"],
                usd=item["USD"])
            print(table)
        print("-"*50)


class StartDateError(Exception):
    """Raised when start date < history available via API"""
    pass

class NegativeValueError(Exception):
    """Raised when negative cash """
    pass

class InsufficientBalanceError(Exception):
    """Raised when not enough cash or Bitcoin to cover transaction"""
    pass

class KeyAuthenticationError(Exception):
    """Raised when key entered does not match account key"""
    pass

class Menu(Wallet, PriceChart):
    """Intiates menu of options."""
    
    def __init__(self):
        print("\n")
        print("\u20BF - "*12 + '\u20BF')
        print("Welcome to the \u20BFitcoin Wallet.")
        super().__init__(self)

    def print_menu(self):
        print("-"*50)
        print("\nPlease select from the following options:\n",
                "Enter 1 to: Fetch \u20BFitcoin Price Chart\n", 
                "Enter 2 to: Create Account\n", 
                "Enter 3 to: Access Wallet\n",
                "Enter Q to: Quit the Program\n")
        print("-"*50)
    
    def print_wallet_menu(self):
        print("-"*50)
        print("\nPlease select a Wallet option:\n",
                "Enter 1 to: Add Cash\n", 
                "Enter 2 to: Buy \u20BFitcoin\n", 
                "Enter 3 to: Sell \u20BFitcoin\n",
                "Enter 4 to: Get Statment\n",
                "Enter R to: Return to Main Menu\n")
        print("-"*50)
    
# Run from terminal
class Main:
    """Main program to launch menu UI and wallet functionality"""

    x = Menu()
    quit = False
    while quit == False:
        try:
            x.print_menu()  #MAIN MENU#
            option1 = input("What would you like to do? \n").upper()
            while option1 not in("1", "2", "3", "4", "Q"):
                option1 = input("Invalid selection. "
                                " Please select an option above: ").upper()
            if option1 == "1":   #plot price chart
                date = input("Please input a start date (YYYY-MM-DD): ")
                x.chart_btc_price(date)
                
            elif option1 == "2":  #Create account
                name = input("Please input your name: ").title()
                cash = float(input("Please input starting cash (w/o commas): "))
                a = Account(name, cash)
                print("\nWelcome {}! Your wallet key is: {}"
                      .format(a.name, a._key))
                print("Copy or save this key to access your Wallet")
                w = Wallet(a)
                
            elif option1 == "3":  #WALLET MENU#
                #Try, except in order to stay in loop if key incorrect
                try: 
                    wkey = input("Please enter you wallet key: ")
                    if wkey == a._key:
                        print("\nWelcome back {}!".format(a.name))
                        x.print_wallet_menu()
                        quit2 = False
                        while quit2 == False:
                            try:
                                option2 = input("\nPlease select a " 
                                                "Wallet option: ").upper()
                                if option2 == "1": #Add cash
                                    cash_add = float(input("\nAdd how much cash? \n"))
                                    w.add_cash(cash_add)
                                elif option2 == "2":  #Buy btc
                                    w.get_balance()
                                    amt = float(input("\nBuy \u20BFitcoin:"
                                                      " Amount in USD? \n"))
                                    w.buy_btc(amt)
                                elif option2 == "3":  #Sell btc
                                    w.get_balance()
                                    amt = float(input("\nSell \u20BFitcoin:"
                                                      " Amount in USD? \n"))
                                    w.sell_btc(amt)
                                elif option2 == "4":  #Get statement
                                    w.get_statement()
                                    w.get_balance()
                                elif option2 == "R":  #Return to main menu
                                    quit2 = True
                            except ValueError:
                                print("\nInput error! Please input a valid cash amount")
                            except InsufficientBalanceError: 
                                print("Insufficient balance to cover transaction!"
                                      "\nPlease increase balance or try again.")
                            except NegativeValueError:
                                print("\nPlease enter a positive cash amount.")
                    else:
                        raise KeyAuthenticationError
                except KeyAuthenticationError:
                    print("Incorrect key entered! Please try again or buzz off")
            elif option1 == "Q":
                quit = True
        except StartDateError:
            print("\nData coverage begins on 2010-07-17.\n" 
                  "Please alter your start date and try again.")
        except NegativeValueError:
            print("\nPlease enter a positive cash amount.")
        except JSONDecodeError:
            print("\nInput error! Please enter using proper date format" 
                  "(YYYY-MM-DD)")
        except ValueError:
            print("\nInput error! Please input a valid cash amount")
        
    print("\nThank you for using the \u20BFitcoin Wallet.  Goodbye!")
    print("\u20BF - "*12 + '\u20BF')
    sys.exit()
        
if __name__ == '__main__':
    main = Main()
