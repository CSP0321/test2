# 載入必要函數
import indicator,sys,time,datetime,haohaninfo,order_shioaji
import talib
import lineTool

# 匯入 Shioaji 套件
import shioaji as sj

# 建立 Shioaji api 物件
api = sj.Shioaji(simulation=False)
api = sj.Shioaji(simulation=True)

# 登入帳號
api.login("", "")

KMinute= 1

## 下單或平倉口數的數量大於1者, 事實上還是 "逐口"進行交易
O_B_Qty = '3'
O_S_Qty = '3'
#C_S_Qty = '2'   ## 下列程式會以現有的在倉部位口數當作要出場交易的口數, C_S_Qty 為進場是多單, 出場要賣的口數
#C_B_Qty = '2'   ## 下列程式會以現有的在倉部位口數當作要出場交易的口數, C_B_Qty 為進場是空單, 出場要賣的口數
StopLoss = 30
StopLossPoint_B = 0
StopLossPoint_S = 100000000000

## Line token:
token='YR4ffglIphON1uMyDL40gYX3xwq1OG3WGUz8PHbenp7'

# 部位管理物件
RC=order_shioaji.Record()

# K棒物件     
Today = '20220713'        ##Today = time.strftime('%Y%m%d')   Today = '20210331'; Today = '20170803'
KBar = indicator.KBar(Today,KMinute) 
# 定義KD週期
RSVPeriod=5
KPeriod=3
DPeriod=3



"""## 訂閱及時 Tick 逐筆成交資料
官方文件：https://sinotrade.github.io/tutor/market_data/streaming/#tick
"""
## stock:
api.quote.subscribe(api.Contracts.Stocks["2609"], quote_type='tick',version = 'v1')

api.quote.subscribe(api.Contracts.Futures.TXF['TXF202207'],quote_type ='tick',version = 'v1')

#api.quote.subscribe(api.Contracts.Futures.MXF['MXF202207'],quote_type ='tick')
api.quote.subscribe(api.Contracts.Futures.MXF['MXF202207'],quote_type ='tick',version = 'v1')


## (2)
Tick_dic = {}
Product_list = []
DateTime_list = []
Close_list = []
Amount_list = []
AmountSum_list = []
Volume_list = []
VolSum_list = []
Buy_or_Sell_list = []
from shioaji import TickFOPv1, Exchange
@api.on_tick_fop_v1()
def quote_callback(exchange:Exchange, tick:TickFOPv1):
    global new_deal_price
    #quote_dic={"Topic": topic, "Quote": quote}
    #quote_dic = quote
    #print(f"{quote}")
    new_deal_price = float(tick.close)
    Product_list.append(tick.code)
    DateTime_list.append(tick.datetime)
    Close_list.append(float(tick.close))
    Amount_list.append(int(tick.amount))
    AmountSum_list.append(int(tick.total_amount))
    Volume_list.append(int(tick.volume))
    VolSum_list.append(int(tick.total_volume))
    Buy_or_Sell_list.append(tick.tick_type)
    Tick_dic['Product'] = Product_list
    Tick_dic['DateTime'] = DateTime_list
    Tick_dic['Close'] = Close_list
    Tick_dic['Amount'] = Amount_list
    Tick_dic['AmountSum'] = AmountSum_list
    Tick_dic['Volume'] = Volume_list
    Tick_dic['VolSum'] = VolSum_list
    Tick_dic['TickType'] = Buy_or_Sell_list  ## '1'=Buy, '2'=Sell



"""## 訂閱及時上下五檔成交資料
官方文件：https://sinotrade.github.io/tutor/market_data/streaming/#tick
"""
## stock:
#api.quote.subscribe(api.Contracts.Stocks["2330"], quote_type='bidask')
api.quote.subscribe(api.Contracts.Stocks["2330"], quote_type='bidask',version = 'v1')

#api.quote.subscribe(api.Contracts.Futures.TXF['TXF202207'],quote_type ='bidask')
api.quote.subscribe(api.Contracts.Futures.TXF['TXF202207'],quote_type ='bidask',version = 'v1')

#api.quote.subscribe(api.Contracts.Futures.MXF['MXF202207'],quote_type ='bidask')
api.quote.subscribe(api.Contracts.Futures.MXF['MXF202207'],quote_type ='bidask',version = 'v1')

## (2)
UpDown_dic = {}
Product_list = []
DateTime_list = []
UpPrice_list = []
UpVolume_list = []
UpVolSum_list = []
DownPrice_list = []
DownVolume_list = []
DownVolSum_list = []
from shioaji import BidAskFOPv1, Exchange
@api.on_bidask_fop_v1()
def quote_callback(exchange:Exchange, bidask:BidAskFOPv1):
    UpPrice_list.append(bidask.ask_price) 
    UpVolume_list.append(bidask.ask_volume)
    UpVolSum_list.append(bidask.ask_total_vol)
    DownPrice_list.append(bidask.bid_price) 
    DownVolume_list.append(bidask.bid_volume)
    DownVolSum_list.append(bidask.bid_total_vol)
    UpDown_dic['UpPrice'] = UpPrice_list
    UpDown_dic['UpVolume'] = UpVolume_list
    UpDown_dic['UpVolSum'] = UpVolSum_list
    UpDown_dic['DownPrice'] = DownPrice_list
    UpDown_dic['DownVolume'] = DownVolume_list
    UpDown_dic['DownVolSum'] = DownVolSum_list


while True:
    # 定義時間
    #CTime = datetime.datetime.strptime(str(Tick_dic['DateTime'][-1]),'%Y-%m-%d %H:%M:%S.%f')
    CTime = Tick_dic['DateTime'][-1]
    # 定義成交價、成交量
    CPrice=float(Tick_dic['Close'][-1])
    CQty=int(Tick_dic['Volume'][-1])
    #print('CTime: ',CTime,' CPrice: ',CPrice,' CQty: ',CQty)
    # 更新K棒 若新增K棒則判斷開始判斷 策略
    if KBar.AddPrice(CTime,CPrice,CQty) == 1:
        CloseList=KBar.GetClose()
        # 取得KD
        K,D=KBar.GetKD(RSVPeriod,KPeriod,DPeriod)
        #print('CloseList:', CloseList, 'K list:',K, 'D list:', D)
        # 判斷是否有KD值
        if len(K) >= RSVPeriod+KPeriod+1:
            LastK=K[-2]
            LastD=D[-2]
        #if len(CloseList) >= LongMAPeriod+2:
            #LongMAList = KBar.GetEMA(LongMAPeriod)
            #ShortMAList=KBar.GetEMA(ShortMAPeriod)
            ClosePrice=CloseList[-2]
            #LongMA=LongMAList[-2]
            #ShortMA=ShortMAList[-2]
            #LastClosePrice=CloseList[-3]
            #LastLongMA=LongMAList[-3]
            #LastShortMA=ShortMAList[-3]
            print('目前在倉部位口數:',RC.GetOpenInterest(),'目前成交報價資料時間:',CTime,'最新收盤價:',ClosePrice,'最新 K 值:',LastK,'最新 D 值:',LastD)
            print()
            # 判斷進場的部分
            if RC.GetOpenInterest() == 0:
                ## K值大於D值,買進多單
                if LastK > LastD:
                   
                    # 多單進場
                    # 寫入紀錄至部位管理物件 
                    OrderInfoTime=datetime.datetime.strptime(str(Tick_dic['DateTime'][-1]),'%Y-%m-%d %H:%M:%S.%f')
                    OrderInfoPrice=UpDown_dic['UpPrice'][-1][2]
                    OrderProd = Tick_dic['Product'][-1]
                    OrderQty = O_B_Qty
                    RC.Order('B',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                    # 紀錄移動停損停利價位
                    StopLossPoint_B= max(OrderInfoPrice-StopLoss,StopLossPoint_B)  ## 還有小問題
                    print('產品:', OrderProd,', 多單進場買進時間:',OrderInfoTime,', 買進價格:',OrderInfoPrice,', 停損價位:',StopLossPoint_B,', 多單買進口數:',OrderQty)
                    print()
                    msg='產品: '+OrderProd+'; 多單買進時間: '+str(OrderInfoTime)+'; 買進價格: '+str(OrderInfoPrice)+'; 多單買進口數: '+str(OrderQty)
                    lineTool.lineNotify(token,msg)
                        
                # K值小於D值,買進空單
                elif LastK < LastD:
                   
                    # 空單進場
                    # 寫入紀錄至部位管理物件 
                    OrderInfoTime=datetime.datetime.strptime(str(Tick_dic['DateTime'][-1]),'%Y-%m-%d %H:%M:%S.%f')
                    OrderInfoPrice=UpDown_dic['DownPrice'][-1][2]
                    OrderProd = Tick_dic['Product'][-1]
                    OrderQty = O_S_Qty
                    RC.Order('S',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                    # 紀錄移動停損停利價位
                    StopLossPoint_S= min(OrderInfoPrice+StopLoss,StopLossPoint_S)  ## 還有小問題
                    print('產品:',OrderProd,', 空單買進時間:',OrderInfoTime,', 買進價格:',OrderInfoPrice,', 停損價位:',StopLossPoint_S,', 空單買進口數:',OrderQty)
                    print()
                    msg='產品: '+OrderProd+'; 空單買進時間: '+str(OrderInfoTime)+'; 買進價格: '+str(OrderInfoPrice)+'; 空單買進口數: '+str(OrderQty)
                    lineTool.lineNotify(token,msg)
    
    
            # 判斷多單出場的部分
            elif RC.GetOpenInterest() > 0:    ## == 1
                # 移動停損判斷
                if ClosePrice-StopLoss > StopLossPoint_B:
                    StopLossPoint_B=ClosePrice-StopLoss 
                if ClosePrice <= StopLossPoint_B or LastK < LastD:
                    # 成交則寫入紀錄至部位管理物件 
                    C_S_Qty = RC.GetOpenInterest()   ## 以現有的在倉部位口數當作要出場交易的口數
                    OrderInfoTime=datetime.datetime.strptime(str(Tick_dic['DateTime'][-1]),'%Y-%m-%d %H:%M:%S.%f')
                    OrderInfoPrice=UpDown_dic['DownPrice'][-1][2]
                    OrderProd = Tick_dic['Product'][-1]
                    OrderQty = C_S_Qty
                    RC.Cover('S',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
               
                    ## 紀錄移動停損停利價位
                    #StopLossPoint= OrderInfoPrice-StopLoss
                    print('產品:',OrderProd,', 多單平倉時間:',OrderInfoTime,', 平倉價格:',OrderInfoPrice,', 多單平倉口數:',OrderQty)
                    print()
                    msg='產品: '+OrderProd+'; 多單平倉時間: '+str(OrderInfoTime)+'; 平倉價格: '+str(OrderInfoPrice)+'; 多單平倉口數: '+str(OrderQty)
                    lineTool.lineNotify(token,msg)
                    break
            # 判斷空單出場的部分
            elif RC.GetOpenInterest() < 0:     ## == -1
                # 移動停損判斷
                if ClosePrice+StopLoss < StopLossPoint_S:
                    StopLossPoint_S=ClosePrice+StopLoss 
                if ClosePrice >= StopLossPoint_S or LastK > LastD:
                    # 成交則寫入紀錄至部位管理物件 
                    C_B_Qty = -(RC.GetOpenInterest())   ## 以現有的在倉部位口數當作要出場交易的口數
                    OrderInfoTime=datetime.datetime.strptime(str(Tick_dic['DateTime'][-1]),'%Y-%m-%d %H:%M:%S.%f')
                    OrderInfoPrice=UpDown_dic['UpPrice'][-1][2]
                    OrderProd = Tick_dic['Product'][-1]
                    OrderQty = C_B_Qty
                    RC.Cover('B',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
    
                    ## 紀錄移動停損停利價位
                    #StopLossPoint= OrderInfoPrice-StopLoss
                    print('產品:',OrderProd,', 空單平倉時間:',OrderInfoTime,', 平倉價格:',OrderInfoPrice,', 空單平倉口數:',OrderQty)
                    print()
                    msg='產品: '+OrderProd+'; 空單平倉時間: '+str(OrderInfoTime)+'; 平倉價格: '+str(OrderInfoPrice)+'; 空單平倉口數: '+str(OrderQty)
                    lineTool.lineNotify(token,msg)
                    break


#print('交易紀錄:',RC.TradeRecord)
print('交易紀錄:',RC.GetTradeRecord())
print('在倉部位數量:',RC.GetOpenInterest())  
print('在倉部位清單:',RC.OpenInterest)
print('績效記錄清單:',RC.GetProfit())
print('淨交易績效:', RC.GetTotalProfit(), ', 平均每次交易績效(包含盈虧):',RC.GetAverageProfit(), ', 勝率(賺錢次數占總次數比例):',RC.GetWinRate(),', 最大連續虧損:', RC.GetAccLoss(), ', 最大資金(績效profit)回落(MDD):',RC.GetMDD(),', 平均每次獲利(只算賺錢的):',RC.GetAverEarn(),', 平均每次虧損(只算賠錢的):',RC.GetAverLoss())

## 產出累積績效圖(包含盈虧):
RC.GeneratorProfitChart()



