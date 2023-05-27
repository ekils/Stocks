import os
import yfinance as yf
import pandas as pd
import numpy as np 
import os 

eps_data = 'eps.xlsx' # 手動增加: https://www.financecharts.com/stocks/AAPL/value/pe-ratio

my_env = os.environ.copy()
if 'stock' in my_env:
    stock = my_env["stock"]
else:
    stock = input('輸入股票代號:') # APPL
stock = stock.upper()

path_price = './price_{}.csv'.format(stock)
path_pe = './pe_ratio_{}.csv'.format(stock)


def process_eps(eps_data):
    df_eps = pd.read_excel(eps_data)
    column_datetime = df_eps.columns.tolist()
    column_datetime = [i for i in column_datetime if not '_' in i]
    for company_name in column_datetime:
        df_eps[company_name] = pd.to_datetime(df_eps[company_name], dayfirst=True)
        df_eps[company_name] = pd.to_datetime(df_eps[company_name])
    print('計算 EPS 與 產出 PE 中.......')
    # print(df_eps)
    return df_eps


def to_final_report(stock, path_price):
    # Get EPS_TTM:
    df_eps = process_eps(eps_data)

    # Get Price:
    data = pd.read_csv(path_price)  
    data.rename(columns={'Date': 'Date', 'Close': 'Price'}, inplace=True)
    data['Date'] = pd.to_datetime(data['Date'])

    # Add EPS_TTM to Dataframe
    for index in range(len(df_eps)):
        if index == 0:
            newest = df_eps.iloc[index][stock]
            mask = (data['Date'] > newest) 
        else:
            newest = df_eps.iloc[index-1][stock]
            last = df_eps.iloc[index][stock]
            mask = (data['Date'] > last) & (data['Date'] <= newest)
        temp = data.loc[mask]
        eps_list = temp.index.tolist()
        eps_ttm = df_eps.iloc[index][stock +'_EPS']
        if index == 0:
            data.insert(2, "EPS_TTM", pd.Series([eps_ttm]*len(eps_list), index=eps_list))
        else:
            new_df = pd.DataFrame({'EPS_TTM': pd.Series([eps_ttm]*len(eps_list),index=eps_list)})
            data.update(new_df)

    data['P/E_TTM'] = data['Price']/data['EPS_TTM']
    data.to_csv(path_pe) 
    read_file = pd.read_csv (path_pe)
    final_path = '.' + path_pe.strip('.csv')+'.xlsx'
    read_file.to_excel(final_path, index = None, header=True)
    os.remove(path_pe)
    return 

to_final_report(stock, path_price)



