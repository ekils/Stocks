import yfinance as yf
import pandas as pd
import numpy as np 
from datetime import date
import os 

today = date.today()
start = "2009-01-01"
end = today.strftime("%Y-%m-%d")

my_env = os.environ.copy()
if 'stock' in my_env:
    stock = my_env["stock"]
else:
    stock = input('輸入股票代號:') # APPL
stock = stock.upper()
print('STOCK:' ,stock)

def get_price(stock, start, end, path_price):
    data = yf.download(stock, start, end)
    data = data.iloc[::-1] # row reverse
    # print(data['Close'])
    print('產出股價資料中......')
    data['Close'].to_csv(path_price)  
    return 

path_price = './price_{}.csv'.format(stock)
get_price(stock, start, end, path_price)