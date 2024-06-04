# 載入必要套件
import matplotlib.pyplot as plt
import time
import talib
# 下單部位管理物件
class Record():
    def __init__(self ):
        # 儲存績效
        self.Profit=[]
        # 未平倉
        self.OpenInterestQty=0
        self.OpenInterest=[]
        # 交易紀錄總計
        self.TradeRecord=[]
    # 進場紀錄
    def Order(self, BS,Product,OrderTime,OrderPrice,OrderQty):
        if BS=='B' or BS=='Buy':
            for i in range(int(OrderQty)):
                self.OpenInterest.append([1,Product,OrderTime,OrderPrice])  ## OpenInterest 中的每一個記錄都是一口
                self.OpenInterestQty +=1
        elif BS=='S' or BS=='Sell':
            for i in range(int(OrderQty)):
                self.OpenInterest.append([-1,Product,OrderTime,OrderPrice])  ## OpenInterest 中的每一個記錄都是一口
                self.OpenInterestQty -=1
    # 出場紀錄(買賣別需與進場相反，多單進場則空單出場)
    def Cover(self, BS,Product,CoverTime,CoverPrice,CoverQty):
        if BS=='S' or BS=='Sell':
            for i in range(int(CoverQty)):
                # 取得多單未平倉部位
                TmpInterest=[ j for j in self.OpenInterest if j[0]==1 ][0]
                if TmpInterest != []:
                    # 清除未平倉紀錄
                    self.OpenInterest.remove(TmpInterest)
                    self.OpenInterestQty -=1
                    # 新增交易紀錄(已經平倉), TradeRecord 中的每一個記錄都是一口
                    self.TradeRecord.append(['B',TmpInterest[1],TmpInterest[2],TmpInterest[3],CoverTime,CoverPrice])  ## 'B' 代表進場是多單 ##TmpInterest[1]:Product, TmpInterest[2]:OrderTime, TmpInterest[3]:OrderPrice 
                    self.Profit.append(CoverPrice-TmpInterest[3])
                else:
                    print('尚無進場')
        elif BS=='B' or BS=='Buy':
            for i in range(int(CoverQty)):
                # 取得空單未平倉部位
                TmpInterest=[ k for k in self.OpenInterest if k[0]==-1 ][0]
                if TmpInterest != []:
                    # 清除未平倉紀錄
                    self.OpenInterest.remove(TmpInterest)
                    self.OpenInterestQty +=1
                    # 新增交易紀錄
                    self.TradeRecord.append(['S',TmpInterest[1],TmpInterest[2],TmpInterest[3],CoverTime,CoverPrice])  ## 'S' 代表進場是空單
                    self.Profit.append(TmpInterest[3]-CoverPrice)
                else:
                    print('尚無進場')
    # 取得當前未平倉量
    def GetOpenInterest(self):               
        return self.OpenInterestQty
    # 取得交易紀錄
    def GetTradeRecord(self):               
        return self.TradeRecord   
    # 取得交易績效
    def GetProfit(self):       
        return self.Profit  

    
    # 取得交易績效
    def GetTotalProfit(self):  
        return sum(self.Profit)
    # 取得平均交易績效
    def GetAverageProfit(self): 
        return sum(self.Profit)/len(self.Profit)
        
    # 取得勝率
    def GetWinRate(self):
        WinProfit = [ i for i in self.Profit if i > 0 ]
        return len(WinProfit)/len(self.Profit)
    # 最大連續虧損
    def GetAccLoss(self):
        AccLoss = 0
        MaxAccLoss = 0
        for p in self.Profit:
            if p <= 0:
                AccLoss+=p
                if AccLoss < MaxAccLoss:
                    MaxAccLoss=AccLoss
            else:
                AccLoss=0  ##因為是要計算 "連續" 虧損,一旦中間有賺錢，就中斷連續虧損
        return MaxAccLoss
    # 最大資金(績效)回落(MDD)
    def GetMDD(self):
        MDD,Capital,MaxCapital = 0,0,0
        for p in self.Profit:
            Capital += p
            MaxCapital = max(MaxCapital,Capital)
            DD = MaxCapital - Capital
            MDD = max(MDD,DD)
        return MDD
    # 平均獲利 
    def GetAverEarn(self):
        WinProfit = [ i for i in self.Profit if i > 0 ]
        if len(WinProfit)>0:
           return sum(WinProfit)/len(WinProfit)
        if len(WinProfit)==0:
           return '沒有賺錢記錄'
    # 平均虧損
    def GetAverLoss(self):
        FailProfit = [ i for i in self.Profit if i < 0 ]
        if len(FailProfit)>0:
           return sum(FailProfit)/len(FailProfit)
        if len(FailProfit)==0:
           return '沒有賠錢記錄'
            
    # 產出交易績效圖
    def GeneratorProfitChart(self,StrategyName='Strategy'):
        # 定義圖表
        ax1 = plt.subplot(111)
        # 計算累計績效
        TotalProfit=[0]
        for i in self.Profit:
            TotalProfit.append(TotalProfit[-1]+i)
        # 繪製圖形
        ax1.plot( TotalProfit  , '-', linewidth=1 )
        #定義標頭
        ax1.set_title('Accumulated Profit(累計淨績效)')
        plt.show()    # 顯示繪製圖表
        # plt.savefig(StrategyName+'.png') #儲存繪製圖表
    

