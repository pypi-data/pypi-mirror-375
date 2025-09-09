from ...interface import IPacker
import datetime


class OHLCDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (str(self._obj.ExchangeID), str(self._obj.InstrumentID), str(self._obj.TradingDay), str(self._obj.ActionDay),
                str(self._obj.ActionTime), int(self._obj.Period), float(self._obj.OpenPrice), float(self._obj.HighestPrice),
                float(self._obj.LowestPrice), float(self._obj.ClosePrice), int(self._obj.CloseVolume),
                float(self._obj.CloseBidPrice), float(self._obj.CloseAskPrice), int(self._obj.CloseBidVolume), int(self._obj.CloseAskVolume),
                float(self._obj.TotalTurnover), int(self._obj.TotalVolume), int(self._obj.OpenInterest), int(self._obj.ActionTimeSpan))

    def tuple_to_obj(self, t):
        if len(t) >= 19:
            self._obj.ExchangeID = t[0]
            self._obj.InstrumentID = t[1]
            self._obj.TradingDay = t[2]
            self._obj.ActionDay = t[3]
            self._obj.ActionTime = t[4]
            self._obj.Period = t[5]
            self._obj.OpenPrice = t[6]
            self._obj.HighestPrice = t[7]
            self._obj.LowestPrice = t[8]
            self._obj.ClosePrice = t[9]
            self._obj.CloseVolume = t[10]
            self._obj.CloseBidPrice = t[11]
            self._obj.CloseAskPrice = t[12]
            self._obj.CloseBidVolume = t[13]
            self._obj.CloseAskVolume = t[14]
            self._obj.TotalTurnover = t[15]
            self._obj.TotalVolume = t[16]
            self._obj.OpenInterest = t[17]
            self._obj.ActionTimeSpan = t[18]

            return True
        return False
