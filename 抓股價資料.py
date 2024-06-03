import twstock
import pandas as pd
import time

# 以陽明的股票代號建立 Stock 物件
stock = twstock.Stock('2609')

# 設定開始日期和結束日期
start_year, start_month = 2019, 1
end_year, end_month = 2024, 4

# 建立一個空的 DataFrame 來儲存所有的股價資料
columns = ["time", "open", "low", "high", "close", "volume", "amount", "product"]
all_data = pd.DataFrame(columns=columns)

# 迴圈遍歷每個月，並獲取該月份的股價資料
current_year, current_month = start_year, start_month

while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
    # 獲取當前月份的股價資料
    stock_data = stock.fetch(current_year, current_month)
    
    # 將資料轉換為 DataFrame 並追加到 all_data
    for record in stock_data:
        row = {
            "time": record.date.strftime("%Y-%m-%d"),
            "open": record.open,
            "low": record.low,
            "high": record.high,
            "close": record.close,
            "volume": record.capacity,
            "amount": record.turnover,
            "product": '2609'
        }
        all_data = all_data.append(row, ignore_index=True)
    
    # 移動到下一個月
    if current_month == 12:
        current_month = 1
        current_year += 1
    else:
        current_month += 1
    
    # 為了避免被伺服器拒絕，延遲1秒
    time.sleep(1)


all_data.to_excel('testdata.xlsx', index=False)
df_original = pd.read_excel('testdata.xlsx')
# ## 保存为Pickle文件:
df_original.to_pickle('testdata.pkl')

df = pd.read_pickle('testdata.pkl')
df.to_pickle('testdata.pkl')

print("DataFrame 已成功导出为 pickle 文件。")