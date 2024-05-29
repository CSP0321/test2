import os
import numpy as np
import indicator_f_Lo2_short, datetime, indicator_forKBar_short
import pandas as pd
import streamlit as st 
import streamlit.components.v1 as stc 
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 設定金融看板標題
html_temp = """
		<div style="background-color:#3872fb;padding:10px;border-radius:10px">
		<h1 style="color:white;text-align:center;">金融資料視覺化呈現 (金融看板) </h1>
		<h2 style="color:white;text-align:center;">Financial Dashboard </h2>
		</div>
		"""
stc.html(html_temp)

@st.cache_data(ttl=3600, show_spinner="正在加載資料...")
def load_data(url):
    df = pd.read_pickle(url)
    return df

# 讀取Pickle文件
df_original = load_data('testdata.pkl')

# 檢查並刪除 'Unnamed: 0' 列
if 'Unnamed: 0' in df_original.columns:
    df_original = df_original.drop('Unnamed: 0', axis=1)
else:
    st.warning("'Unnamed: 0' 列不存在，跳過刪除該列")

st.subheader("選擇開始與結束的日期, 區間:2019-01-02 至 2024-04-30")
start_date = st.text_input('選擇開始日期 (日期格式: 2019-01-02)', '2019-01-02')
end_date = st.text_input('選擇結束日期 (日期格式: 2024-04-30)')

# 確保日期格式正確
try:
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
except ValueError:
    st.error("日期格式不正確，請使用 YYYY-MM-DD 格式")
    st.stop()

# 使用條件篩選選擇時間區間的數據
df = df_original[(df_original['time'] >= start_date) & (df_original['time'] <= end_date)]

###### (2) 轉化為字典 ######:
KBar_dic = df.to_dict()
KBar_dic['open'] = np.array(list(KBar_dic['open'].values()))
KBar_dic['product'] = np.repeat('tsmc', KBar_dic['open'].size)
KBar_dic['time'] = np.array([i.to_pydatetime() for i in list(KBar_dic['time'].values())])
KBar_dic['low'] = np.array(list(KBar_dic['low'].values()))
KBar_dic['high'] = np.array(list(KBar_dic['high'].values()))
KBar_dic['close'] = np.array(list(KBar_dic['close'].values()))
KBar_dic['volume'] = np.array(list(KBar_dic['volume'].values()))
KBar_dic['amount'] = np.array(list(KBar_dic['amount'].values()))

###### (3) 改變 KBar 時間長度 (以下)  ########
Date = start_date.strftime("%Y-%m-%d")
st.subheader("設定一根 K 棒的時間長度(日)")
cycle_duration = st.number_input('輸入一根 K 棒的時間長度(單位:日)', key="KBar_duration")
cycle_duration = int(cycle_duration)

KBar = indicator_forKBar_short.KBar(Date, cycle_duration * 1440)  # 將天數轉換為分鐘數

for i in range(KBar_dic['time'].size):
    time = KBar_dic['time'][i]
    open_price = KBar_dic['open'][i]
    close_price = KBar_dic['close'][i]
    low_price = KBar_dic['low'][i]
    high_price = KBar_dic['high'][i]
    qty = KBar_dic['volume'][i]
    amount = KBar_dic['amount'][i]
    tag = KBar.AddPrice(time, open_price, close_price, low_price, high_price, qty)

## 形成 KBar 字典 (新週期的):
KBar_dic = {}
KBar_dic['time'] = KBar.TAKBar['time']
KBar_dic['product'] = np.repeat('tsmc', KBar_dic['time'].size)
KBar_dic['open'] = KBar.TAKBar['open']
KBar_dic['high'] = KBar.TAKBar['high']
KBar_dic['low'] = KBar.TAKBar['low']
KBar_dic['close'] = KBar.TAKBar['close']
KBar_dic['volume'] = KBar.TAKBar['volume']

###### (4) 計算各種技術指標 ######
KBar_df = pd.DataFrame(KBar_dic)

##### 移動平均線策略 #####
st.subheader("設定計算長移動平均線(MA)的 K 棒數目(整數, 例如 10)")
LongMAPeriod = st.slider('選擇一個整數', 0, 100, 10)
st.subheader("設定計算短移動平均線(MA)的 K 棒數目(整數, 例如 2)")
ShortMAPeriod = st.slider('選擇一個整數', 0, 100, 2)

KBar_df['MA_long'] = KBar_df['close'].rolling(window=LongMAPeriod).mean()
KBar_df['MA_short'] = KBar_df['close'].rolling(window=ShortMAPeriod).mean()

# 防止移動平均線計算初期值缺失
last_nan_index_MA = KBar_df['MA_long'][::-1].index[KBar_df['MA_long'][::-1].apply(pd.isna)].tolist()[0] if KBar_df['MA_long'].isna().any() else -1

##### RSI 策略 #####
st.subheader("設定計算長RSI的 K 棒數目(整數, 例如 10)")
LongRSIPeriod = st.slider('選擇一個整數', 0, 1000, 10)
st.subheader("設定計算短RSI的 K 棒數目(整數, 例如 2)")
ShortRSIPeriod = st.slider('選擇一個整數', 0, 1000, 2)

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

KBar_df['RSI_long'] = calculate_rsi(KBar_df, LongRSIPeriod)
KBar_df['RSI_short'] = calculate_rsi(KBar_df, ShortRSIPeriod)
KBar_df['RSI_Middle'] = np.array([50] * len(KBar_dic['time']))

# 防止 RSI 計算初期值缺失
last_nan_index_RSI = KBar_df['RSI_long'][::-1].index[KBar_df['RSI_long'][::-1].apply(pd.isna)].tolist()[0] if KBar_df['RSI_long'].isna().any() else -1

###### (5) 將 Dataframe 欄位名稱轉換  ###### 
KBar_df.columns = [i[0].upper() + i[1:] for i in KBar_df.columns]

###### (6) 畫圖 ######
st.subheader("畫圖")

##### K線圖, 移動平均線 MA #####
with st.expander("K線圖, 移動平均線"):
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig1.add_trace(go.Candlestick(x=KBar_df['Time'],
                    open=KBar_df['Open'], high=KBar_df['High'],
                    low=KBar_df['Low'], close=KBar_df['Close'], name='K線'),
                   secondary_y=True)
    
    fig1.add_trace(go.Bar(x=KBar_df['Time'], y=KBar_df['Volume'], name='成交量', marker=dict(color='black')), secondary_y=False)
    fig1.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_MA+1:], y=KBar_df['MA_long'][last_nan_index_MA+1:], mode='lines', line=dict(color='orange', width=2), name=f'{LongMAPeriod}-根 K棒 移動平均線'), secondary_y=True)
    fig1.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_MA+1:], y=KBar_df['MA_short'][last_nan_index_MA+1:], mode='lines', line=dict(color='pink', width=2), name=f'{ShortMAPeriod}-根 K棒 移動平均線'), secondary_y=True)

    fig1.layout.yaxis2.showgrid = True
    st.plotly_chart(fig1, use_container_width=True)

##### K線圖, RSI #####
with st.expander("K線圖, 長短 RSI"):
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig2.add_trace(go.Candlestick(x=KBar_df['Time'],
                    open=KBar_df['Open'], high=KBar_df['High'],
                    low=KBar_df['Low'], close=KBar_df['Close'], name='K線'),
                   secondary_y=True)
    
    fig2.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_RSI+1:], y=KBar_df['RSI_long'][last_nan_index_RSI+1:], mode='lines', line=dict(color='red', width=2), name=f'{LongRSIPeriod}-根 K棒 移動 RSI'), secondary_y=False)
    fig2.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_RSI+1:], y=KBar_df['RSI_short'][last_nan_index_RSI+1:], mode='lines', line=dict(color='blue', width=2), name=f'{ShortRSIPeriod}-根 K棒 移動 RSI'), secondary_y=False)
    
    fig2.layout.yaxis2.showgrid = True
    st.plotly_chart(fig2, use_container_width=True)
