from typing import Tuple, Optional, Union
import msgpack
import lzma
import zlib
import datetime
import pickle
import pandas as pd
import numpy as np


from .req_rsp import ReqRspDict, ReqRsp
from ..listener import IListener
from ..interface import IData, MsgID
from ..tsocket import TSocket
from ..data.message_data import MessageData

from ..data.market.market_param_data import MarketParamData
from ..data.market.sub_ohlc_param_data import SubOHLCParamData
from ..data.market.query_param_data import QueryParamData

from ..data.market.tick_data import TickData
from ..data.market.ohlc_data import OHLCData
from ..data.market.history_ohlc_param_data import HistoryOHLCParamData
from ..data.market.fin_persist_filed_data import FinPersistFiledData
from ..data.market.fin_persist_save_param_data import FinPersistSaveParamData
from ..data.market.fin_persist_read_param_data import FinPersistReadParamData
from ..data.market.fin_persist_delete_param_data import FinPersistDeleteParamData


class MarketHandle():
    def __init__(self, tsocket: TSocket):
        self.__TSocket = tsocket
        self.__TSocket.set_market_callback(self.__recv_msg)
        self.__ReqID = 0
        self.__Listener = None
        self.__ReqRspDict = ReqRspDict()

    def set_callback(self, **kwargs):
        if kwargs is None:
            return
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def set_listener(self, listener: IListener):
        self.__Listener = listener

    def set_market_params(self, params: MarketParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.MSGID_Market_SetParams.value), params)

    def subscribe(self, params: QueryParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.MSGID_Market_Sub.value), params)

    def subscribe_ohlc(self, params: SubOHLCParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.MSGID_Market_SubOHLC.value), params)

    def __notify_on_tick(self, msg: MessageData):
        hasontick = hasattr(self, 'on_tick')
        if hasontick is False and self.__Listener is None:
            print('未定义任何on_tick回调方法')
            return
        t = TickData()
        if t.un_pack(msg.UData) is True:
            if hasontick is True:
                self.on_tick(t)  # type: ignore
            if self.__Listener is not None:
                self.__Listener.on_tick(t)

    def __notify_on_ohlc(self, msg: MessageData):
        hasonohlc = hasattr(self, 'on_ohlc')
        if hasonohlc is False and self.__Listener is None:
            print('未定义任何on_ohlc回调方法')
            return
        o = OHLCData()
        if o.un_pack(msg.UData) is True:
            if hasonohlc is True:
                self.on_ohlc(o)  # type: ignore
            if self.__Listener is not None:
                self.__Listener.on_ohlc(o)

    def __recv_msg(self, msg: MessageData):
        if msg.MID == int(MsgID.MSGID_Market_Tick.value):
            self.__notify_on_tick(msg)
            return
        elif msg.MID == int(MsgID.MSGID_Market_OHLC.value):
            self.__notify_on_ohlc(msg)
            return

        key = '%s_%s' % (msg.MID, msg.RequestID)
        reqrsp: Optional[ReqRsp] = self.__ReqRspDict.get_reqrsp(key)
        if reqrsp is not None:
            reqrsp.append_rsp(msg)

    def __wait_send_msg(self, mid, params: IData) -> Tuple[bool, str]:
        self.__ReqID = self.__ReqID + 1
        msg = MessageData(mid=mid, request_id=self.__ReqID)
        if params is not None:
            msg.UData = params.pack()  # type: ignore

        key = '%s_%s' % (mid, self.__ReqID)

        req_rsp = self.__ReqRspDict.new_reqrsp(key, msg)
        if self.__TSocket.send_message(msg) is False:
            self.__ReqRspDict.remove(key)
            return (False, '发送命令失败')

        rsp = req_rsp.wait_last_rsp(60)
        if rsp is None:
            self.__ReqRspDict.remove(key)
            return (False, '发送命令超时')

        ret = (rsp.RspSuccess, rsp.RspMsg)
        self.__ReqRspDict.remove(key)
        return ret
