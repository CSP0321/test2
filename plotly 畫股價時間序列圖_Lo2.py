import pandas as pd
import csv,os,time,twstock

#pip install plotly 
from plotly.graph_objs import Scatter,Layout
from plotly.offline import plot

import matplotlib.pyplot as plt
import matplotlib


filepath = 'testdata.csv'

# 如果檔案不存在就建立檔案
if not os.path.isfile(filepath):
    title = ["日期", "成交股數", "成交金額", "開盤價", "最高價", "最低價", "收盤價", "漲跌價差", "成交筆數"]
    with open(filepath, 'a', newline='', encoding='utf-8') as outputfile:
        outputwriter = csv.writer(outputfile)
        for year in range(2020, 2025):
            for month in range(1, 13):
                if year == 2024 and month > 4:
                    break
                stock = twstock.Stock('2609')
                stocklist = stock.fetch(year, month)
                data = []
                for stock_data in stocklist:
                    strdate = stock_data.date.strftime("%Y-%m-%d")
                    li = [strdate, stock_data.capacity, stock_data.turnover, stock_data.open, stock_data.high, stock_data.low,
                          stock_data.close, stock_data.change, stock_data.transaction]
                    data.append(li)
                if year == 20120 and month == 1:
                    outputwriter.writerow(title)
                for dataline in data:
                    outputwriter.writerow(dataline)
                time.sleep(1)  # 延遲1秒, 否則有時會有錯誤

# 以pandas讀取檔案
pdstock = pd.read_csv(filepath, encoding='utf-8')

# 確保日期列解析為日期類型
pdstock['日期'] = pd.to_datetime(pdstock['日期'])

# 繪製圖表
data = [
    Scatter(x=pdstock['日期'], y=pdstock['收盤價'], name='收盤價'),
    Scatter(x=pdstock['日期'], y=pdstock['最低價'], name='最低價'),
    Scatter(x=pdstock['日期'], y=pdstock['最高價'], name='最高價')
]

# 設置 matplotlib 支持中文的字體
matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 使用 plotly 繪圖
plot({"data": data, "layout": Layout(title='2020~2024年4月個股統計圖')}, auto_open=True)