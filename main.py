#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 19:04:48 2021

@author: crc9
"""
import sys
import csv
import datetime 

class ExchangeRate:
    symbol: str
    list_of_rates : []
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.list_of_rates = []
    
    def __repr__(self):
        return self.symbol
        
    def add_rate(self,rate_date,rate):
        self.list_of_rates.append(self.RateAtDate(rate_date,rate))
    
    def get_previous_date_rate(self,rate_date):
        if (len(self.list_of_rates)>1):
            self.list_of_rates.sort(key=lambda x: x.rate_date)
        previous_date_rate = 0
        for rate_at_date in self.list_of_rates:
            if (rate_at_date.rate_date>=rate_date):
                #print("0",rate_at_date.rate_date, previous_date_rate)
                if (previous_date_rate != 0):
                    
                    return previous_date_rate
                else:
                    sys.exit("rate " + str(rate_date) + " don't exist in csv")
                    return "rate not available"
                    
            else:
                previous_date_rate=rate_at_date.rate
                #print("1",rate_at_date.rate_date, previous_date_rate)   
    
    class RateAtDate:
        rate_date: datetime.date
        rate: float
        
        def __init__(self, rate_date,rate):
            self.rate=rate
            self.rate_date = rate_date
            
        def __repr__(self):
            return self.rate_date.strftime("%Y %m %d") + " " + str(self.rate)
            

class TransactionRecord:
    id_nr : int
    account_id : str
    symbol : str
    operation : str
    date_time : datetime 
    amount : float
    amount_eur : float
    currency : str
    comment : str
    currency_rate_day_before : float

    def __init__(self, id_nr, symbol, operation, 
                 date_time, amount, currency, amount_eur, account_id = '', comment = ''):
        self.id_nr = id_nr
        self.symbol = symbol
        self.operation = operation
        self.date_time = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
        self.amount = amount
        self.amount_eur = amount_eur
        self.account_id = account_id
        self.currency = currency
        self.comment = comment
        self.currency_rate_day_before = 0.0

    def __repr__(self):
        return self.date_time.strftime("%y-%m-%d %H:%M:%S") + " ID " + str(self.id_nr) + " " + self.operation + " " + \
    " " + self.symbol + " " + \
    str(self.amount) + " " + self.currency + " " + str(self.currency_rate_day_before)
        
class PositionSummary:
    symbol: str
    currency : str
    transactions : []
    dividends : []
    actual_positions : []
    tax : []
    
    def __init__(self, symbol, currency):
        self.symbol = symbol
        self.currency = currency
        self.transactions = []
        self.dividends = []
        self.actual_positions = []
        self.tax = []
        
    def __repr__(self):
        return "\n" + self.symbol + " " + self.currency + ":\n" + str(self.transactions).replace(", ",'\n').replace("[","").replace("]","")
    
    def __str__(self):
        return self.symbol
    
    
    def add_transaction(self,transaction_record : TransactionRecord):
        if (transaction_record.symbol == self.symbol):
            position_found = 0
            for position in self.transactions:
                if (position.date_time == transaction_record.date_time):
                    position_found = 1
                    if (transaction_record.operation == "TRADE"):
                        if (transaction_record.currency == self.symbol):
                            position.amount = transaction_record.amount
                        else:
                            position.price = transaction_record.amount
                            if (self.currency == ""):
                                self.currency = transaction_record.currency
                            position.rate = transaction_record.currency_rate_day_before
                    elif (transaction_record.operation == "COMMISSION"):
                        position.fee = transaction_record.amount
                    break
            for position in self.dividends:
                if (position.date_time == transaction_record.date_time):
                    position_found = 1
                    if (transaction_record.operation == "TAX"):
                        position.fee = transaction_record.amount
                    elif (transaction_record.operation == "DIVIDEND"):
                        position.amount = transaction_record.amount

            if (position_found == 0):
                if (transaction_record.operation == "TRADE"):
                    if (transaction_record.currency == self.symbol):
                        self.transactions.append(self.Transaction(transaction_record.date_time,transaction_record.amount,0,0,0))
                    else:
                        self.transactions.append(self.Transaction(transaction_record.date_time,0,transaction_record.amount,0,transaction_record.currency_rate_day_before))
                elif (transaction_record.operation == "COMMISSION"):
                    self.transactions.append(self.Transaction(transaction.date_time,0,0,transaction_record.amount,transaction_record.currency_rate_day_before))
                elif (transaction_record.operation == "TAX"):
                    self.dividends.append(self.Transaction(transaction_record.date_time,0,0,transaction_record.amount,transaction_record.currency_rate_day_before))
                elif (transaction_record.operation == "DIVIDEND"):
                    self.dividends.append(self.Transaction(transaction_record.date_time,transaction_record.amount,0,0,transaction_record.currency_rate_day_before))
 
    def calculate_actual_position(self):        
        self.tax=[]
        for transaction in self.transactions:
            if (transaction.amount > 0):
                self.actual_positions.append(self.Position(transaction.date_time,transaction.amount,transaction.price,transaction.rate, transaction.fee))
            elif (transaction.amount < 0):
                if (transaction.fee < 0):
                    self.tax.append((str(transaction.date_time),\
                                     round(transaction.fee*transaction.rate,4),\
                                     "koszt przy zbyciu"))
                    log.append("Koszt przy sprzedarzy " + self.symbol + " dnia " + str(transaction.date_time.date()) +\
                               " o kwocie " + str(transaction.fee) + " " + self.currency + " po kursie " + str(transaction.rate) +\
                               " co daje " + str(round(transaction.fee*transaction.rate,4)) + " PLN")
                temp_amount = -transaction.amount
                for position in self.actual_positions:
                    if (position.amount >= temp_amount):
                        #print(1, position.amount, temp_amount)
                        self.tax.append((str(transaction.date_time),\
  #  (transaction.price,transaction.rate,position.price,position.rate,temp_amount),\
                                         round(((transaction.price/transaction.amount)*transaction.rate*(-1.0)\
                                          -(position.price/position.amount)*position.rate*(-1.0))\
                                          *temp_amount,4),"zysk/strata ze zbycia"))
                        log.append("Sprzedarz " + str(temp_amount) + " " + self.symbol +\
                                   " dnia " + str(transaction.date_time.date()) +\
                               " o wartości " + str(transaction.price/transaction.amount*temp_amount) + " " + self.currency + " "\
                               " po kursie " + str(transaction.rate) +\
                               " kupionych " + str(position.date_time.date()) +\
                               " po cenie " + str(round(position.price/position.amount,4)) + " za akcję po kursie " + str(position.rate) + \
                               " co daje " + str(round(((transaction.price/transaction.amount)*transaction.rate*(-1.0)\
                                          -(position.price/position.amount)*position.rate*(-1.0))\
                                          *temp_amount,4)) + " PLN zysku")                            
                        if (position.amount > temp_amount):
                            ratio = temp_amount/position.amount
                            self.tax.append((str(transaction.date_time),\
                                             round(position.fee*ratio*position.rate,2),\
                                             "koszt przy zakupie"))
                            log.append("Koszt przy zakupie " + self.symbol + " dnia " + str(transaction.date_time.date()) +\
                               " o kwocie " + str(position.fee*ratio) + " " + self.currency + " po kursie " + str(position.rate) +\
                               " co daje " + str(round(position.fee*ratio*position.rate,4)) + " PLN")
                            position.fee = position.fee - position.fee * ratio
                        else:
                            self.tax.append((str(transaction.date_time),\
                                             round(position.fee*position.rate,4),\
                                             "koszt przy zakupie"))
                            log.append("Koszt przy zakupie " + self.symbol + " dnia " + str(transaction.date_time.date()) +\
                               " o kwocie " + str(position.fee) + " " + self.currency + " po kursie " + str(position.rate) +\
                               " co daje " + str(round(position.fee*position.rate,4)) + " PLN")
                            position.fee = 0
                        position.price = position.price/position.amount*temp_amount
                        position.amount = position.amount - temp_amount
                        temp_amount = 0.0
                        ## place to calculate tax
                    elif (position.amount < temp_amount):
                        #print(3, (transaction.price/transaction.amount)*transaction.rate*(-1.0),(position.price/position.amount)*position.rate*(-1.0))
                        self.tax.append((str(transaction.date_time),\
  # (transaction.price,transaction.rate,position.price,position.rate,position.amount),\
                                         round(((transaction.price/transaction.amount)*transaction.rate*(-1.0) \
                                           -(position.price/position.amount)*position.rate*(-1.0)) \
                                            *position.amount,4),"zysk/strata ze zbycia"))
                        log.append("Sprzedarz " + str(position.amount) + " " + self.symbol +\
                                   " dnia " + str(transaction.date_time.date()) +\
                               " o wartości " + str(position.amount/transaction.amount*transaction.price) + " " + self.currency + " "\
                               " po kursie " + str(transaction.rate) +\
                               " kupionych " + str(position.date_time.date()) +\
                               " za kwotę " + str(position.price) + " po kursie " + str(position.rate) + \
                               " co daje " + str(round(((transaction.price/transaction.amount)*transaction.rate*(-1.0) \
                                           -(position.price/position.amount)*position.rate*(-1.0)) \
                                            *position.amount,4)) + " PLN zysku")  
                        self.tax.append((str(transaction.date_time),\
                                         round(position.fee*position.rate,4),\
                                         "koszt przy zakupie"))                        
                        position.fee = 0
                        temp_amount = temp_amount - position.amount
                        position.amount = 0.0
                    if (temp_amount == 0.0):
                        break
        for position in self.dividends:
            self.tax.append((str(position.date_time),round((position.amount)*position.rate,4),'zysk z dywidendy'))
            self.tax.append((str(position.date_time),round((position.fee)*position.rate,4),'podatek u źródła'))
                
    class Transaction:
        date_time : datetime
        amount : float
        price : float
        fee : float   
        rate : float
        
        def __init__(self,date_time, amount, price, fee, rate):
            self.date_time = date_time
            self.amount=amount
            self.price=price
            self.fee=fee
            self.rate=rate
        def __repr__(self):
            return self.date_time.strftime("%y-%m-%d %H:%M:%S \t") + str(self.amount) + "\t" + str(self.price) + "\t" + str(self.fee) + "\t" + str(self.rate)
    
    class Position:
        date_time : datetime
        amount : float
        price : float
        fee : float
        rate : float
        
        def __init__(self,date_time, amount, price, rate, fee):
            self.date_time = date_time
            self.amount = amount
            self.price = price
            self.fee = fee
            self.rate = rate

        def __repr__(self):
            return self.date_time.strftime("%y-%m-%d %H:%M:%S \t") + str(self.amount) + "\t" + str(self.price) + "\t fee:" + str(self.fee)
    
        
transactions = []
positions = []
list_of_currencies = []
exchange_rates = []
# load csv file with transaction

with open('/home/crc9/Programming/ex.csv', encoding='utf16') as csv_file:
    rows = csv.reader(csv_file, delimiter='\t')
    for row in rows:
        if (row[0].isdigit()):
            transactions.insert(0,TransactionRecord(int(row[0]),row[2],row[3],row[4],float(row[5]),row[6],float(row[7]),row[1],row[8]))
            if (len(row[6]) == 3):
                if [row[6],0] not in list_of_currencies:
                    exchange_rates.append(ExchangeRate(row[6]))
                    list_of_currencies.append([row[6],0])

with open('/home/crc9/Programming/rates2020.csv') as csv_file:
    rows = csv.reader(csv_file, delimiter=';')
    first_row = 1
    for row in rows:
        if (first_row == 1):
            first_row = 0
            actual_col = 0
            for col in row:
                for currency in list_of_currencies:
                    if (col[-3:] == currency[0]):
                        currency[1]=actual_col
                actual_col=actual_col+1
        else:
            if (row[0].isdigit()):
                for i in range(len(exchange_rates)):
                    exchange_rates[i].add_rate(datetime.datetime.strptime(row[0],'%Y%m%d').date(),float(row[list_of_currencies[i][1]].replace(",",".")))

for transaction in transactions:
    if (len(transaction.currency) == 3):
        for exchange_rate in exchange_rates:
            if (exchange_rate.symbol == transaction.currency):
                transaction.currency_rate_day_before = exchange_rate.get_previous_date_rate(transaction.date_time.date())
                break
            
for transaction in transactions:
    if ((transaction.symbol.find(".EXANTE") == -1) and (transaction.symbol.find("None") == -1)): 
        position_found = 0
        for position in positions:
            if (str(position) == transaction.symbol):
                position_found = 1
                position.add_transaction(transaction)
                break
        if (position_found == 0):
            if (transaction.symbol == transaction.currency):
                positions.insert(0,PositionSummary(transaction.symbol,""))
                positions[0].add_transaction(transaction)
            else:
                positions.insert(0,PositionSummary(transaction.symbol,transaction.currency))
                positions[0].add_transaction(transaction)
suma = 0      
log=[]
      
for position in positions:
    position.calculate_actual_position()
    if len(position.tax)>0:
        for tax in position.tax:
            suma = suma + tax[1]
        print(position.symbol,position.tax)
print("suma:",round(suma,2))

with open('/home/crc9/Programming/ex_out.csv', 'w') as csv_file:
    writer = csv.writer(csv_file, delimiter='\t')
    for transaction in transactions:
        
        writer.writerow()
    
    
#class TaxReturnCalculation():
#   " def __init__(self):
#       def load_exante_csv(self):
#           with open('/home/crc9/Programming/ex.csv', encoding='utf16') as csv_file:
#               rows = csv.reader(csv_file, delimiter='\t')
#               for row in rows:
#                   print(row)
               
