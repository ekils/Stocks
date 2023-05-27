import plotly.graph_objects as go
import dateutil.parser as dparser
import matplotlib.pyplot as plt 
import plotly.express as px
import numpy as np
import datetime as dt
from scipy import stats
import pandas as pd
import math
import os


"""
--------------------------
|  指定顯示過去?年的紀錄：   |
--------------------------
"""
slide = 4 * 4 #  4: 切成四季 ; 2: 兩年

my_env = os.environ.copy()
if 'stock' in my_env:
    stock = my_env["stock"]
else:
    stock = input('輸入股票代號:') # APPL
stock = stock.upper()

print('產生美股:{} 的圖檔中...'.format(stock))

# EPS:
path_eps = 'eps.xlsx'
eps_data = pd.read_excel(path_eps) 
eps_data = eps_data[[stock,'{}_EPS'.format(stock)]]
eps_data[stock] = pd.to_datetime(eps_data[stock], dayfirst=True, format="%m/%d/%Y")
# print(eps_data.head())

# P/E:
path_pe = './pe_ratio_{}.xlsx'.format(stock)
data = pd.read_excel(path_pe)  
data['P/E_LOG'] = np.log10(data['P/E_TTM'])
data = data[['Date', 'P/E_LOG','Price']]
data['Price'] = data['Price'].astype(float)
data['Date'] = pd.to_datetime(data.Date)
# print(data.head())

# 拆三個月為一組：
eps_group = []
for index in range(len(eps_data)):
    if index == 0:
        newest = eps_data.iloc[index][stock]
        mask = (data['Date'] > newest) 
    else:
        newest = eps_data.iloc[index-1][stock]
        last = eps_data.iloc[index][stock]
        mask = (data['Date'] > last) & (data['Date'] <= newest)
    temp = data.loc[mask]
    eps_list = temp.index.tolist()
    eps_group.append(eps_list)

# 找過去?年股價歷史高點：
temp_max_price_list = []
temp_index_list = []
temp_max_eps_list = []
temp_eps_index = []
temp_eps_list = []
temp_max_pe_list = []
temp_max_pe_to_log_list =[]

# 取得 高點的index, price
for i in range(slide):
    temp_group = eps_group[1+i:slide+i]
    temp_group_list = [item for sublist in temp_group for item in sublist]
    temp_group_data = data.iloc[temp_group_list]
    temp_max_price = temp_group_data['Price'].max()
    temp_max_price_list.append(temp_max_price)
    temp_index = temp_group_data.index[temp_group_data['Price']==temp_max_price][0]
    temp_index_list.append(temp_index)

# 再取得過去?年的 eps:
temp_eps_list = eps_data['{}_EPS'.format(stock)][0:slide].tolist()
# 取得過去?年的 日期:
temp_date_list_datetime = eps_data[stock].iloc[0:slide].tolist()
temp_date_list = [str(i) for i in temp_date_list_datetime]
# 取得下一個到期 日期：
dayDistance = (temp_date_list_datetime[0] - temp_date_list_datetime[1])
new_date = temp_date_list_datetime[0] + pd.Timedelta(dayDistance, unit="m")
temp_date_list.insert(0, str(new_date))

# 轉換eps , eps_log: 
for a, b in zip(temp_max_price_list, temp_eps_list):
    temp_max_pe_list.append(a/b)
temp_max_pe_to_log_list = [ np.log10(i) for i in temp_max_pe_list] 

# 取得顯示資料的開始年份：
now_year = str(pd.Timestamp.now()).split('-')[0]
five_year_start= str(int(now_year) - 5 - 1)
five_year_end= str(int(now_year) - 5)
t1 = (dparser.parse("{}-12-28".format(five_year_start),fuzzy=True))
t2 = (dparser.parse("{}-01-03".format(five_year_end),fuzzy=True))
masks = (data['Date'] >= t1) & (data['Date'] <= t2)
masks = [ index for index, true_false in enumerate(masks) if true_false == True][0]

# print('temp_index_list:', temp_index_list) # index
# print('temp_eps_list:', temp_eps_list) # EPS 
# print('temp_date_list:', temp_date_list) # EPS 對應時間 slide + 1個
# print('temp_max_price_list:',temp_max_price_list) # price
# print('temp_max_pe_list:', temp_max_pe_list) # PE
# print('temp_max_pe_to_log_list:', temp_max_pe_to_log_list) # PE LOG

#取得 資料的趨勢線斜率: 
data['date_ordinal'] = pd.to_datetime(data['Date']).map(dt.datetime.toordinal)
slope, intercept, r_value, p_value, std_err = stats.linregress(data['date_ordinal'][:masks], data['P/E_LOG'][:masks])
# print('slope:',slope)

# data std: 
std = round(data[:masks]['P/E_LOG'].std(),3)
print('std:', std)

# Interval slope:
interval_data = []
for i in range(len(temp_max_pe_to_log_list)):
    y1 = (temp_max_pe_to_log_list[i] + slope * 45)
    y0 = (temp_max_pe_to_log_list[i] - slope * 45)
    interval_data.append((y0,y1))
print('最高本益比區間:', interval_data)

def plot_interval_slope(fig, index,y0,y1):
    for std_count in range(4):
        if std_count == 0:
            fillcolor='rgba(150,26,65,0.4)' # r
        elif std_count == 1 :
            fillcolor='rgba(30,90,250,0.4)' # b
        elif std_count == 2:
            fillcolor='rgba(255,255,51,0.2)' # y
        elif std_count == 3:
            fillcolor='rgba(26,190,65,0.2)' # g
        
        fig.add_trace(go.Scatter(
            x=[str(temp_date_list[index+1]), str(temp_date_list[index])],
            y=[y0 - ((std/2)*std_count), y1 - ((std/2)*std_count)],
            fill=None,
            mode='lines',
        ))
        fig.add_trace(go.Scatter(
            x=[str(temp_date_list[index+1]), str(temp_date_list[index])],
            y=[y0 - ((std/2)*(std_count+1)), y1 - ((std/2)*(std_count+1))],
            fill='tonexty',
            fillcolor=fillcolor,
            mode='lines',
        ))

# 畫圖：
fig = go.Figure()
fig.add_trace(go.Scatter(mode='markers', x=data[:masks]["Date"], y=data[:masks]["P/E_LOG"],
                            marker=dict(
                                        color='LightSkyBlue',
                                        size=4,
                                        line=dict(
                                            color='MediumPurple',
                                            width=1
                                        )
                                    )
))
for x_date in temp_date_list: 
    fig.add_vline(x=x_date, line_width=2, line_dash="dash", line_color="green")

for index in range(slide-1):
    y0 = interval_data[index][0]
    y1 = interval_data[index][1]
    plot_interval_slope(fig, index,y0,y1)  
fig.update_layout(showlegend=False, yaxis={'side': 'right'})        
# fig.show()
fig.write_html("./PE_Trend_{}.html".format(stock))

