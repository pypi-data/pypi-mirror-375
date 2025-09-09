from ...interface import IData
from ...packer.market.ohlc_data_packer import OHLCDataPacker
import datetime


class OHLCData(IData):
    def __init__(self, exchange_id: str = '', instrument_id: str = '', trading_day: str = '', action_day: str = '',
                 action_time: str = '', period: int = 60, open_price: float = 0.0, highest_price: float = 0.0, lowest_price: float = 0.0,
                 close_price: float = 0.0, close_volume: int = 0, close_bid_price: float = 0.0, close_ask_price: float = 0.0, close_bid_volume: int = 0,
                 close_ask_volume: int = 0, total_turnover: float = 0.0, total_volume: int = 0, open_interest: int = 0, action_time_span: int = 0):
        super().__init__(OHLCDataPacker(self))
        self._ExchangeID: str = exchange_id
        self._InstrumentID: str = instrument_id
        self._TradingDay: str = trading_day
        self._ActionDay: str = action_day
        self._ActionTime: str = action_time
        self._ActionTimeSpan: int = action_time_span
        self._Period: int = period
        self._OpenPrice: float = open_price
        self._HighestPrice: float = highest_price
        self._LowestPrice: float = lowest_price
        self._ClosePrice: float = close_price
        self._CloseVolume: int = close_volume
        self._CloseBidPrice: float = close_bid_price
        self._CloseAskPrice: float = close_ask_price
        self._CloseBidVolume: int = close_bid_volume
        self._CloseAskVolume: int = close_ask_volume
        self._TotalTurnover: float = total_turnover
        self._TotalVolume: int = total_volume
        self._OpenInterest: float = open_interest

    @property
    def ExchangeID(self):
        return self._ExchangeID

    @ExchangeID.setter
    def ExchangeID(self, value: str):
        self._ExchangeID = value

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def TradingDay(self):
        return self._TradingDay

    @TradingDay.setter
    def TradingDay(self, value: str):
        self._TradingDay = value

    @property
    def ActionDay(self):
        return self._ActionDay

    @ActionDay.setter
    def ActionDay(self, value: str):
        self._ActionDay = value

    @property
    def ActionTime(self):
        return self._ActionTime

    @ActionTime.setter
    def ActionTime(self, value: str):
        self._ActionTime = value

    @property
    def ActionTimeSpan(self):
        return self._ActionTimeSpan

    @ActionTimeSpan.setter
    def ActionTimeSpan(self, value: int):
        self._ActionTimeSpan = value

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, value: int):
        self._Period = value

    @property
    def OpenPrice(self):
        return self._OpenPrice

    @OpenPrice.setter
    def OpenPrice(self, value: float):
        self._OpenPrice = value

    @property
    def HighestPrice(self):
        return self._HighestPrice

    @HighestPrice.setter
    def HighestPrice(self, value: float):
        self._HighestPrice = value

    @property
    def LowestPrice(self):
        return self._LowestPrice

    @LowestPrice.setter
    def LowestPrice(self, value: float):
        self._LowestPrice = value

    @property
    def ClosePrice(self):
        return self._ClosePrice

    @ClosePrice.setter
    def ClosePrice(self, value: float):
        self._ClosePrice = value

    @property
    def CloseVolume(self):
        return self._CloseVolume

    @CloseVolume.setter
    def CloseVolume(self, value: int):
        self._CloseVolume = value

    @property
    def CloseBidPrice(self):
        return self._CloseBidPrice

    @CloseBidPrice.setter
    def CloseBidPrice(self, value: float):
        self._CloseBidPrice = value

    @property
    def CloseAskPrice(self):
        return self._CloseAskPrice

    @CloseAskPrice.setter
    def CloseAskPrice(self, value: float):
        self._CloseAskPrice = value

    @property
    def CloseBidVolume(self):
        return self._CloseBidVolume

    @CloseBidVolume.setter
    def CloseBidVolume(self, value: int):
        self._CloseBidVolume = value

    @property
    def CloseAskVolume(self):
        return self._CloseAskVolume

    @CloseAskVolume.setter
    def CloseAskVolume(self, value: int):
        self._CloseAskVolume = value

    @property
    def TotalTurnover(self):
        return self._TotalTurnover

    @TotalTurnover.setter
    def TotalTurnover(self, value: float):
        self._TotalTurnover = value

    @property
    def TotalVolume(self):
        return self._TotalVolume

    @TotalVolume.setter
    def TotalVolume(self, value: int):
        self._TotalVolume = value

    @property
    def OpenInterest(self):
        return self._OpenInterest

    @OpenInterest.setter
    def OpenInterest(self, value: int):
        self._OpenInterest = value
