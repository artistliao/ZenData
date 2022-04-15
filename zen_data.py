
# -*- coding:utf-8 -*-
#! python3

from pandas import DataFrame, Series
import pandas as pd
import numpy as np

import talib
import time
import sys
import os
import mysql.connector

from zd_logging import g_logger
from read_data import *
from utils import *

import random
import grpc
import secdata_transfer_pb2
import secdata_transfer_pb2_grpc

def run():
    # 连接 rpc 服务器
    channel = grpc.insecure_channel('localhost:50051')
    # 调用 rpc 服务
    stub = secdata_transfer_pb2_grpc.GreeterStub(channel)
    response = stub.SayHello(secdata_transfer_pb2.HelloRequest(name='czl'))
    print("Greeter client received: " + response.message)
    response = stub.SayHello(secdata_transfer_pb2.HelloRequest(name='daydaygo'))
    print("Greeter client received: " + response.message)

if __name__ == "__main__":

    stock_code = sys.argv[1] # '000001.XSHG'
    level = sys.argv[2]      # '1min'
    g_logger.info('stock_code:%s, level:%s', stock_code, level)


    # now_time = int(time.time())
    # zts = time.timezone
    # day_time = now_time - (now_time- time.timezone)%86400
    #
    # start_ts = int(time.time())
    # start_ts += 8*3600

    #读取数据
    zen_ms_data = ZenMsData('futures', 'config.ini')
    zen_ms_data.LoadAllSecurities()
    klines = zen_ms_data.LoadSecuritiesKlineData(stock_code, "1min", 1577808000)
    # klines = zen_ms_data.LoadSecuritiesKlineData(stock_code, "1min", 1587744000)
    if klines is None:
        g_logger.warning("read code:%s, level:%s, klines is None!", stock_code, level)
        sys.exit(-1)

    kline_num = len(klines.index)

    g_logger.debug("kline_num=%d", kline_num)
    # 连接 rpc 服务器
    channel = grpc.insecure_channel('localhost:50051')
    # 调用 rpc 服务
    stub = secdata_transfer_pb2_grpc.SecdataHandleStub(channel)
    count = 0
    for i in range(kline_num):
        # df.rename(columns={'ts':'Ts','open':'Open', 'high':'High', 'low':'Low', 'close':'Close', 'volume':'Volume'}, inplace=True)

        ts = int(klines.loc[i,'Ts'])
        open = klines.loc[i,'Open']
        high = klines.loc[i,'High']
        low = klines.loc[i,'Low']
        close = klines.loc[i,'Close']
        volume = klines.loc[i,'Volume']
        amount = klines.loc[i,'Amount']
        send_count = 1 #random.randint(1, 4)
        for j in range(send_count):
            response = stub.TransferKlineData(secdata_transfer_pb2.KlineRequest(ts=ts, code=stock_code, period=level, open=open, high=high, low=low, close=close, vol=int(volume), amount=amount))
            count += 1
            if i%100==0:
                g_logger.debug("i=%d, j=%d, time=%s", i, j, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)))
        # if i%10==0:
        #     time.sleep(0.01)

    g_logger.debug("all count=%d", count)