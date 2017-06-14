# encoding: UTF-8

'''
实现读取wind行情历史数据.mat格式
'''

import scipy.io as sio
import pandas as pd
import datetime, re

class LoadMatFile(object):

    def __init__(self, matFile):
        self.matFile = matFile
        self.data = sio.loadmat(self.matFile)
        self.dfData = self.convert2df()

    def convert2df(self):
        colNames = ['vtSymbol','symbol','date','time','lastPrice','lastVolume','lastTurnover','matchItems','openInterest','tradeFlag','bsFlag','volume','turnover'
                    ,'highPrice','lowPrice','openPrice','preClosePrice','settlementPrice','position','curDelta','preSettlementPrice','prePosition','askPrice1'
                    ,'askVolume1','bidPrice1','bidVolume1','askAvPrice','bidAvPrice','totalAskVolume','totalBidVolume','index','stocks','ups','downs','holdLines']

        seriesNames = locals()
        for k,v in enumerate(self.data['temp'][0][0].tolist()):
            if colNames[k] in ['askPrice1','askVolume1','bidPrice1','bidVolume1']:
                v = v[:,0]
            if v.ndim  == 1:
                seriesNames['SN_%s' % k] = pd.Series(v, name = colNames[k])
            elif v.ndim > 1:
                v = v.ravel()
                seriesNames['SN_%s' % k] = pd.Series(v, name=colNames[k])
            else:
                print ("index = %d, dim = %d" %(k, v.ndim))

        df_data = pd.concat([seriesNames[a] for a in seriesNames if 'SN_' in a], axis = 1)
        df_data = df_data.dropna(axis=0,how='any')
        dfData = self.normalizeData(df_data)
        return dfData

    def normalizeData(self, df):
        f = lambda x:str(int(x))
        df["date"] = df["date"].map(f)
        df["time"] = df["time"].map(f)
        vtSymbol = self.matFile.split('\\')[-1].split('_')[0]
        symbol = re.findall(r"[a-zA-Z]", vtSymbol)[0].lower()
        date = self.matFile.split('\\')[-1].split('_')[-1][:-4]
        df["vtSymbol"] = vtSymbol
        df["symbol"] = symbol
        df["DT"] = df["date"] + ' ' + df["time"]
        df["datetime"] = df["DT"].map(lambda x:datetime.datetime.strptime(x, "%Y%m%d %H%M%S%f"))
        del df["DT"]
        df["date"] = date
        return df
