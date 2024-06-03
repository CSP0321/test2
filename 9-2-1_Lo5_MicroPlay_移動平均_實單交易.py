# 載入必要函數
import indicator,sys,time,datetime,haohaninfo,order_Lo3_test4
from haohaninfo import MicroPlay
import lineTool
from haohaninfo.MicroTest import microtest_db
#import numpy as np

Broker = 'Test'
Prod = 'MXFH9'   ## 'MXFD1', 'MXFH7'
KMinute= 1
ShortMAPeriod=2
LongMAPeriod=3
#Qty = '2'

## 下單或平倉口數的數量大於1者, 事實上還是 "逐口"進行交易
O_B_Qty = '3'
O_S_Qty = '3'
#C_S_Qty = '2'   ## 下列程式會以現有的在倉部位口數當作要出場交易的口數, C_S_Qty 為進場是多單, 出場要賣的口數
#C_B_Qty = '2'   ## 下列程式會以現有的在倉部位口數當作要出場交易的口數, C_B_Qty 為進場是空單, 出場要賣的口數
StopLoss = 30
StopLossPoint_B = 0
StopLossPoint_S = 100000000000
wait_O = 20 #單位: 秒
wait_C = 6000  #單位: 秒
 
## Line token:
token='YR4ffglIphON1uMyDL40gYX3xwq1OG3WGUz8PHbenp7'

# 部位管理物件
RC=order_Lo3_test4.Record()

# K棒物件     
Today = '20190731'        ##Today = time.strftime('%Y%m%d')   Today = '20210331'; Today = '20170803'
KBar = indicator.KBar(Today,KMinute) 

# 訂閱報價物件
#GO = haohaninfo.GOrder.GOQuote()
a = MicroPlay.MicroPlayQuote()
# 訂閱報價
#for row in GO.Subscribe(Broker, 'match', Prod):
for row in a.Subscribe(Broker, 'match', Prod):
    # 定義時間
    CTime = datetime.datetime.strptime(row[0],'%Y/%m/%d %H:%M:%S.%f')
    # 定義成交價、成交量
    CPrice=float(row[2])
    CQty=int(row[3])
    # 更新K棒 若新增K棒則判斷開始判斷 策略
    if KBar.AddPrice(CTime,CPrice,CQty) == 1:
        CloseList=KBar.GetClose()
        #print('CloseList:', CloseList)
        # 如果 長MA 計算出值 則開始判斷進出場
        if len(CloseList) >= LongMAPeriod+2:
            LongMAList = KBar.GetEMA(LongMAPeriod)
            ShortMAList=KBar.GetEMA(ShortMAPeriod)
            ClosePrice=CloseList[-2]
            LongMA=LongMAList[-2]
            ShortMA=ShortMAList[-2]
            LastClosePrice=CloseList[-3]
            LastLongMA=LongMAList[-3]
            LastShortMA=ShortMAList[-3]
            print('目前在倉部位口數:',RC.GetOpenInterest(),'目前成交報價資料時間:',CTime,'最新收盤價:',ClosePrice,'上一筆收盤價:',LastClosePrice,'最新短MA:',ShortMA,'上一筆短MA:',LastShortMA,'最新長MA:',LongMA,'上一筆長MA:',LastLongMA)
            print()
            # 判斷進場的部分
            if RC.GetOpenInterest() == 0:
                # 黃金交叉 買進多單
                if LastShortMA <= LastLongMA and ShortMA > LongMA:
                    # 透過上兩檔價委託多單(範圍市價單 委託三次 若未成交則當日不交易)
                    #OrderInfo=order.RangeMKTDeal(Broker,Prod,'B',Qty,'0','A',2,10)
                    OrderInfo=order_Lo3_test4.RangeMKTDeal(Broker,Prod,'B',O_B_Qty,'0',2,wait_O)   ## OrderInfo: ['SNVS:113,N,MXFD1,Sell,16456,1,ROD,2021-03-31 10:30:55.11,T0001,1']
                    # 如果沒有成交則關閉程序
                    if OrderInfo == False: 
                        #GO.EndSubscribe()
                        a.EndSubscribe()
                    else:
                        for i in OrderInfo:
                           # 成交則寫入紀錄至部位管理物件 
                           OrderInfoTime=datetime.datetime.strptime(i.split(',')[7],'%Y-%m-%d %H:%M:%S.%f')
                           OrderInfoPrice=float(i.split(',')[4])
                           OrderProd = i.split(',')[2]
                           OrderQty = i.split(',')[5]
                           RC.Order('B',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                           # 紀錄移動停損停利價位
                           StopLossPoint_B= max(OrderInfoPrice-StopLoss,StopLossPoint_B)  ## 還有小問題
                           print('交易編號:',i.split(',')[0] ,', 產品:', OrderProd,', 多單進場買進時間:',OrderInfoTime,', 買進價格:',OrderInfoPrice,', 停損價位:',StopLossPoint_B,', 多單成交買進口數:',OrderQty,', 多單委託買進口數:',O_B_Qty)
                           print()
                           msg='交易編號: '+i.split(',')[0]+'; 產品: '+OrderProd+'; 多單買進時間: '+str(OrderInfoTime)+'; 買進價格: '+str(OrderInfoPrice)+'; 多單成交買進口數: '+str(OrderQty)+'; 多單委託買進口數: '+str(O_B_Qty)
                           lineTool.lineNotify(token,msg)
                        #GO.EndSubscribe()
                        #a.EndSubscribe()
                # 死亡交叉 買進空單
                elif LastShortMA >= LastLongMA and ShortMA < LongMA:
                    # 透過下兩檔價委託空單(範圍市價單 委託三次 若未成交則當日不交易)
                    #OrderInfo=order_Lo2.RangeMKTDeal(Broker,Prod,'S',Qty,'0','A',2,10)
                    OrderInfo=order_Lo3_test4.RangeMKTDeal(Broker,Prod,'S',O_S_Qty,'0',2,wait_O)
                    # 如果沒有成交則關閉程序
                    if OrderInfo == False:
                        #GO.EndSubscribe()
                        a.EndSubscribe()
                    else:
                        for i in OrderInfo:
                           # 成交則寫入紀錄至部位管理物件 
                           OrderInfoTime=datetime.datetime.strptime(i.split(',')[7],'%Y-%m-%d %H:%M:%S.%f')
                           OrderInfoPrice=float(i.split(',')[4])
                           OrderProd = i.split(',')[2]
                           OrderQty = i.split(',')[5]
                           RC.Order('S',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                           # 紀錄移動停損停利價位
                           StopLossPoint_S= min(OrderInfoPrice+StopLoss,StopLossPoint_S)  ## 還有小問題
                           print('交易編號:',i.split(',')[0] ,', 產品:',OrderProd,', 空單買進時間:',OrderInfoTime,', 買進價格:',OrderInfoPrice,', 停損價位:',StopLossPoint_S,', 空單成交買進口數:',OrderQty,', 空單委託買進口數:',O_S_Qty)
                           print()
                           msg='交易編號: '+i.split(',')[0]+'; 產品: '+OrderProd+'; 空單買進時間: '+str(OrderInfoTime)+'; 買進價格: '+str(OrderInfoPrice)+'; 空單成交買進口數: '+str(OrderQty)+'; 空單委託買進口數: '+str(O_S_Qty)
                           lineTool.lineNotify(token,msg)
                        #GO.EndSubscribe()
                        #a.EndSubscribe()
            # 判斷多單出場的部分
            elif RC.GetOpenInterest() > 0:    ## == 1
                # 移動停損判斷
                if ClosePrice-StopLoss > StopLossPoint_B:
                    StopLossPoint_B=ClosePrice-StopLoss 
                elif ClosePrice <= StopLossPoint_B:
                    # 透過下兩檔價委託空單(範圍市價單 委託三次 若未成交則當日不交易)
                    #OrderInfo=order_Lo2.RangeMKTDeal(Broker,Prod,'S',Qty,'0','A',2,10)
                    C_S_Qty = RC.GetOpenInterest()   ## 以現有的在倉部位口數當作要出場交易的口數
                    OrderInfo=order_Lo3_test4.RangeMKTDeal(Broker,Prod,'S',C_S_Qty,'0',2,wait_C)
                    
                    # 如果沒有成交則關閉程序
                    if OrderInfo == False:
                        #GO.EndSubscribe()
                        a.EndSubscribe()
                    else:
                        for i in OrderInfo:
                           # 成交則寫入紀錄至部位管理物件 
                           OrderInfoTime=datetime.datetime.strptime(i.split(',')[7],'%Y-%m-%d %H:%M:%S.%f')
                           OrderInfoPrice=float(i.split(',')[4])
                           OrderProd = i.split(',')[2]
                           OrderQty = i.split(',')[5]
                           MicroTest_Qty = OrderQty
                           RC.Cover('S',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                           ## 紀錄移動停損停利價位
                           #StopLossPoint= OrderInfoPrice-StopLoss
                           print('交易編號:',i.split(',')[0] ,', 產品:',OrderProd,', 多單平倉時間:',OrderInfoTime,', 平倉價格:',OrderInfoPrice,', 多單成交平倉口數:',OrderQty,', 多單委託平倉口數:',C_S_Qty)
                           print()
                           msg='交易編號: '+i.split(',')[0]+'; 產品: '+OrderProd+'; 多單平倉時間: '+str(OrderInfoTime)+'; 平倉價格: '+str(OrderInfoPrice)+'; 多單成交平倉口數: '+str(OrderQty)+'; 多單委託平倉口數: '+str(C_S_Qty)
                           lineTool.lineNotify(token,msg)
                        #GO.EndSubscribe()
                        a.EndSubscribe()
            # 判斷空單出場的部分
            elif RC.GetOpenInterest() < 0:     ## == -1
                # 移動停損判斷
                if ClosePrice+StopLoss < StopLossPoint_S:
                    StopLossPoint_S=ClosePrice+StopLoss 
                elif ClosePrice >= StopLossPoint_S:
                    # 透過下兩檔價委託空單(範圍市價單 委託三次 若未成交則當日不交易)
                    #OrderInfo=order_Lo2.RangeMKTDeal(Broker,Prod,'B',Qty,'0','A',2,10)
                    C_B_Qty = -(RC.GetOpenInterest())   ## 以現有的在倉部位口數當作要出場交易的口數
                    OrderInfo=order_Lo3_test4.RangeMKTDeal(Broker,Prod,'B',C_B_Qty,'0',2,wait_C)
                    
                    # 如果沒有成交則關閉程序
                    if OrderInfo == False:
                        #GO.EndSubscribe()
                        a.EndSubscribe()
                    else:
                        for i in OrderInfo:
                           # 成交則寫入紀錄至部位管理物件 
                           OrderInfoTime=datetime.datetime.strptime(i.split(',')[7],'%Y-%m-%d %H:%M:%S.%f')
                           OrderInfoPrice=float(i.split(',')[4])
                           OrderProd = i.split(',')[2]
                           OrderQty = i.split(',')[5]
                           MicroTest_Qty = OrderQty
                           RC.Cover('B',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                           ## 紀錄移動停損停利價位
                           #StopLossPoint= OrderInfoPrice-StopLoss
                           print('交易編號:',i.split(',')[0] ,', 產品:',OrderProd,', 空單平倉時間:',OrderInfoTime,', 平倉價格:',OrderInfoPrice,', 空單成交平倉口數:',OrderQty,', 空單委託平倉口數:',C_B_Qty)
                           print()
                           msg='交易編號: '+i.split(',')[0]+'; 產品: '+OrderProd+'; 空單平倉時間: '+str(OrderInfoTime)+'; 平倉價格: '+str(OrderInfoPrice)+'; 空單成交平倉口數: '+str(OrderQty)+'; 空單委託平倉口數: '+str(C_B_Qty)
                           lineTool.lineNotify(token,msg)
                        #GO.EndSubscribe()
                        a.EndSubscribe()
                

#print('交易紀錄:',RC.TradeRecord)
print('交易紀錄:',RC.GetTradeRecord())
print('在倉部位數量:',RC.GetOpenInterest())  
print('在倉部位清單:',RC.OpenInterest)
print('績效記錄清單:',RC.GetProfit())
print('淨交易績效:', RC.GetTotalProfit(), ', 平均每次交易績效(包含盈虧):',RC.GetAverageProfit(), ', 勝率(賺錢次數占總次數比例):',RC.GetWinRate(),', 最大連續虧損:', RC.GetAccLoss(), ', 最大資金(績效profit)回落(MDD):',RC.GetMDD(),', 平均每次獲利(只算賺錢的):',RC.GetAverEarn(),', 平均每次虧損(只算賠錢的):',RC.GetAverLoss())

## 產出累積績效圖(包含盈虧):
RC.GeneratorProfitChart()

## MicroTest:
## 方法 (1):
RC.FutureMicroTestRecord(StrategyName='MA',ProductValue=50,Fee=100,volume=MicroTest_Qty,account='pu25',password='pu25')  

## 方法 (2):
def FutureMicroTestRecord(StrategyName,ProductValue,Fee,volume,account,password):
        #microtest_db.login('jack','1234','ftserver.haohaninfo.com')
        microtest_db.login(account,password,'140.128.36.207')
        #microtest_db.login(account,password,'140.128.36.207')
        for row in RC.TradeRecord:
            Tax=(row[3]+row[5])*ProductValue*0.00002
            microtest_db.insert_to_server_db(row[1],row[2].strftime('%Y-%m-%d'),row[2].strftime('%H:%M:%S'),str(int(row[3])),str(row[0]),str(volume),row[4].strftime('%Y-%m-%d'),row[4].strftime('%H:%M:%S'),str(row[5]),str(int(Tax)),str(int(Fee)),StrategyName) 
        microtest_db.commit()

FutureMicroTestRecord(StrategyName='MA',ProductValue=50,Fee=100,volume=MicroTest_Qty,account='pu25',password='pu25')

