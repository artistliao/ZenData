
# -*- coding:utf-8 -*-
#! python3

from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import os
import time
import datetime
import mysql.connector
import configparser
import os
import sys
from jqdatasdk import *

import logging
import colorlog
import logging.handlers

log_colors_config = {
    'DEBUG': 'white',  #cyan white
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

#增加日志库
g_logger = logging.getLogger("logger")

handler1 = logging.StreamHandler()
handler2 = logging.handlers.RotatingFileHandler("jqdata_history_" + time.strftime("%m%d%H%M", time.localtime())+ ".log", mode="a", maxBytes=1024*1024, backupCount=0, encoding="utf-8")

g_logger.setLevel(logging.DEBUG)
handler1.setLevel(logging.DEBUG)
handler2.setLevel(logging.DEBUG)

#%(asctime)s [%(threadName)s:%(thread)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s
console_formatter = colorlog.ColoredFormatter(
    fmt='%(log_color)s[%(asctime)s.%(msecs)03d] [%(filename)s:%(lineno)d] [%(levelname)s]- [%(message)s]',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors=log_colors_config
)
handler1.setFormatter(console_formatter)

formatter = logging.Formatter(
    fmt="[%(asctime)s.%(msecs)03d] [%(thread)d] [%(lineno)d] [%(levelname)s]- [%(message)s]",
    datefmt='%Y-%m-%d %H:%M:%S')
handler2.setFormatter(formatter)

g_logger.addHandler(handler1)
g_logger.addHandler(handler2)

# mysql
mydb = None
gp_securities = dict()
gp_trade_days = list()
gp_units = {'1min':'1m', '5min':'5m', '15min':'15m','30min':'30m', '60min':'60m', '120min':'120m', '1day':'1d'}
gp_unit_lens = {'1min':60, '5min':300, '15min':900, '30min':1800, '60min':3600, '120min':7200, '1day':14400}

def Initialize(path):
    global mydb
    g_logger.info('Initialize begin!')
    if path=='':
        g_logger.info("Initialize path is null!")
        return

    try:
        g_logger.info('cfg_path=%s', path)
        cf = configparser.ConfigParser()
        cf.read(path)
        host = cf.get("conf", "host")
        username = cf.get("conf", "username")
        password = cf.get("conf", "password")
        dbname = cf.get("conf", "dbname")
        port = cf.get("conf", "port")
        mydb = mysql.connector.connect(
            host=host,
            port=port,
            user=username,
            passwd=password,
            database=dbname
        )
    except Exception as e:
        g_logger.warning(str(e))
        g_logger.exception(e)


def CreatePriceTable(dbname, table):
    global mydb
    g_logger.info('CreatePriceTable begin!')
    if dbname=='' or table=='':
        g_logger.warning("error dbname=%s, table=%s", dbname, table)
        return

    mycursor = mydb.cursor()
    try:
        create_sql = "CREATE TABLE " + dbname + "." + table + " (\
                    `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增主键id,无具体含义',\
                    `gp_id` smallint(6) NOT NULL COMMENT 'gp id',\
                    `ts` int(11) NOT NULL COMMENT '开始时间戳',\
                    `open` FLOAT(8,2) NOT NULL COMMENT 'open',\
                    `high` FLOAT(8,2) NOT NULL COMMENT 'high',\
                    `low` FLOAT(8,2) NOT NULL COMMENT 'low',\
                    `close` FLOAT(8,2) NOT NULL COMMENT 'close',\
                    `volume` FLOAT(16,2) NOT NULL COMMENT 'volume',\
                    `money` FLOAT(16,2) NOT NULL COMMENT 'money',\
                    `factor` FLOAT(12,6) NOT NULL COMMENT 'factor',\
                    `divergence` tinyint(4) DEFAULT NULL COMMENT 'divergence',\
                    PRIMARY KEY (`id`),\
                    KEY `idx_gp_id` (`gp_id`),\
                    KEY `idx_ts` (`ts`)\
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='行情表';"
        mycursor.execute(create_sql)
        mydb.commit()
    except Exception as e:
        mydb.rollback()
        g_logger.warning(str(e))
        g_logger.exception(e)


def GetBars(securities_type, code, db_name, securities, unit, start_date, end_date):
    global mydb
    global gp_trade_days
    global gp_units

    g_logger.info("GetBars code:%s, unit:%s", code, unit)
    codes = code.split(".")
    if len(codes) != 2:
        g_logger.warning("error code:%s", code)
        return

    if securities_type=='futures':
        tableName = unit + "_prices_" + codes[0][0:2]
    else:
        tableName = unit + "_prices_" + codes[0][-2:]

    tableExist = False
    #判断表是否存在
    mycursor = mydb.cursor()
    check_sql = ""
    try:
        check_sql = "SELECT table_name FROM information_schema.TABLES WHERE table_schema='" + db_name + "' AND table_name = '" + tableName +"';"
        mycursor.execute(check_sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        for row in results:
            tableExist = True
        g_logger.debug("tableName=%s, tableExist=%s", tableName, str(tableExist))
    except Exception as e:
        g_logger.warning(str(e))
        g_logger.exception(e)

    #不存在则建表
    if tableExist==False:
        CreatePriceTable(db_name, tableName)

    max_ts = 0
    try:
        check_sql = "SELECT IFNULL(MAX(ts), 0) FROM " + db_name + "." + tableName +" WHERE gp_id='" + str(securities['id']) + "';"
        mycursor.execute(check_sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        for row in results:
            max_ts = int(row[0])

        g_logger.debug("max_ts=%d", max_ts)
    except Exception as e:
        g_logger.warning("check_sql=%s", check_sql)
        g_logger.warning(str(e))
        g_logger.exception(e)

    #当前查询到的数据的最大日期
    max_str_time = time.strftime('%Y-%m-%d', time.localtime(max_ts))
    start_trade_day = securities['start_date']
    end_trade_day = securities['end_date']

    trade_day_len = len(gp_trade_days)
    idx = 0
    step = 1
    if unit=='60min':
        step = 100
    if  unit=='120min':
        step = 200

    if end_date<max_str_time:
        g_logger.debug("end_date=%s, max_str_time=%s", end_date, max_str_time)
        return

    while(idx<trade_day_len):
        day = gp_trade_days[idx]

        if day<start_trade_day or day<start_date or day<max_str_time:
            idx += step
            if idx>=trade_day_len:
                idx=(trade_day_len-1)
            continue

        if day>end_date:
            break

        unit_inf  = gp_units[unit]
        unit_len = gp_unit_lens[unit]
        bars_count = (8*3600)/unit_len
        if unit=='60min':
            bars_count = 500

        if  unit=='120min':
            bars_count = 500

        tarr = day.split('-')
        if len(tarr)<3:
            g_logger.warning("err trade day:%s", day)
            continue
        end_dt_param = datetime.datetime(int(tarr[0]), int(tarr[1]), int(tarr[2]), 23, 59, 59)
        # fq_ref_date_param = datetime.datetime(2021, 8, 5, 23, 59, 59)
        fq_ref_date_param = datetime.datetime.now()
        g_logger.debug("code:%s, count:%d, end_dt=%s", code, int(bars_count), datetime.datetime.strftime(end_dt_param,'%Y-%m-%d %H:%M:%S'))
        prices = get_bars([code], count=int(bars_count), unit=unit_inf,  fields=['date', 'open', 'close', 'high', 'low', 'volume', 'money', 'factor'],
                          end_dt=end_dt_param, fq_ref_date=fq_ref_date_param, df=True)
        this_max_ts = max_ts
        str_sql = "INSERT INTO " + db_name + "." + tableName + "(gp_id, ts, open, high, low, close, volume, money, factor) VALUES "
        for index, row in prices.iterrows():
            trade_time = int(row['date'].tz_localize(tz='Asia/Shanghai').timestamp())
            trade_time -= unit_len
            if unit=='30min' and datetime.datetime.fromtimestamp(trade_time).strftime('%H:%M')=='09:45':
                trade_time += 900

            if trade_time<=max_ts:
                continue
            elif trade_time>this_max_ts:
                this_max_ts = trade_time
            str_sql += "("
            str_sql += str(securities['id'])
            str_sql += ","
            str_sql += str(trade_time)
            str_sql += ","
            str_sql += "'%.2f'" % round(row['open'], 2)
            str_sql += ","
            str_sql += "'%.2f'" % round(row['high'], 2)
            str_sql += ","
            str_sql += "'%.2f'" % round(row['low'], 2)
            str_sql += ","
            str_sql += "'%.2f'" % round(row['close'], 2)
            str_sql += ","
            str_sql += "'%.2f'" % round(row['volume'], 2)
            str_sql += ","
            str_sql += "'%.2f'" % round(row['money'], 2)
            str_sql += ","
            str_sql += "'%.6f'" % round(row['factor'], 6)
            str_sql += "),"
        str_sql = str_sql[:len(str_sql)-1] + ";"
        if this_max_ts==max_ts:
            idx += step
            continue

        try:
            mycursor.execute(str_sql)
            mydb.commit()
            max_ts = this_max_ts
            g_logger.debug("max_ts=%d", max_ts)
        except Exception as e:
            mydb.rollback()
            g_logger.warning(str(e))
            g_logger.warning("str_sql=%s", str_sql)
            g_logger.exception(e)

        if day>=end_trade_day or day>=end_date:
            break
        idx += step

#修补缺失的数据
def RepairPriceData(code, db_name, securities, start_date, end_date):
    global mydb
    global gp_trade_days

    codes = code.split(".")
    if len(codes) != 2:
        g_logger.warning("error code:%s", code)
        return

    tableName = "1min_prices_" + codes[0][-2:]
    tableExist = False    #判断表是否存在
    mycursor = mydb.cursor()
    try:
        check_sql = "SELECT table_name FROM information_schema.TABLES WHERE table_schema='" + db_name + "' AND table_name = '" + tableName +"';"
        mycursor.execute(check_sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        for row in results:
            tableExist = True

        g_logger.debug("tableName=%s, tableExist=%s", tableName, str(tableExist))
    except Exception as e:
        g_logger.warning(str(e))
        g_logger.exception(e)

    #不存在则建表
    if tableExist==False:
        CreatePriceTable(db_name, tableName)

    #首先找出所有已经存在的数据
    exist_ts = dict()
    try:
        check_sql = "SELECT ts FROM " + db_name + "." + tableName +" WHERE gp_id='" + str(securities['id']) + "';"
        mycursor.execute(check_sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        for row in results:
            ts = int(row[0])
            exist_ts[ts] = 1

        g_logger.debug("len(exist_ts)=%d", len(exist_ts))
    except Exception as e:
        g_logger.warning(str(e))
        g_logger.exception(e)

    #遍历所有的trade_days，找出缺失的数据
    not_exist_ts = list()
    for day in gp_trade_days:
        if day<start_date or day>end_date:
            continue

        strTime = day+' 09:30:00'
        ts = int(time.mktime(time.strptime(strTime,'%Y-%m-%d %H:%M:%S')))
        zero_ts = ts - ((ts + 8 * 3600) % 86400)
        for i in range(9*3600+30*60, 11*3600+30*60, 60):
            sec_ts = zero_ts+i
            if sec_ts not in exist_ts:
                not_exist_ts.append(sec_ts)
        for i in range(13*3600, 15*3600, 60):
            sec_ts = zero_ts+i
            if sec_ts not in exist_ts:
                not_exist_ts.append(sec_ts)

    not_exist_ts.sort()
    g_logger.debug("len(not_exist_ts)=%d", len(not_exist_ts))

    firstTs = 0
    findTs = list()
    for ts in not_exist_ts:
        if len(findTs)==0:
            firstTs = ts
            findTs.append(ts)
            continue
        elif IsSameDay(ts, firstTs)==True:
            findTs.append(ts)
        else:
            findTs.sort()
            startTs = findTs[0]+60
            startTimeArray = time.localtime(startTs)
            strStartTime = time.strftime("%Y-%m-%d %H:%M:%S", startTimeArray)
            lastTs = findTs[len(findTs)-1]+60
            lastTimeArray = time.localtime(lastTs)
            strLastTime = time.strftime("%Y-%m-%d %H:%M:%S", lastTimeArray)
            prices = get_price([code], start_date=strStartTime, end_date=strLastTime, frequency='1m', fields=['open', 'close', 'low', 'high', 'volume', 'money', 'factor', 'paused', 'open_interest'],
                               skip_paused=True, fq='pre',  panel=False, fill_paused=True)

            str_sql = "INSERT INTO " + db_name + "." + tableName + "(gp_id, ts, open, high, low, close, volume, money, factor) VALUES "
            for index, row in prices.iterrows():
                trade_time = int(row['time'].tz_localize(tz='Asia/Shanghai').timestamp())
                trade_time -= 60

                str_sql += "("
                str_sql += str(securities['id'])
                str_sql += ","
                str_sql += str(trade_time)
                str_sql += ","
                str_sql += "'%.2f'" % round(row['open'], 2)
                str_sql += ","
                str_sql += "'%.2f'" % round(row['high'], 2)
                str_sql += ","
                str_sql += "'%.2f'" % round(row['low'], 2)
                str_sql += ","
                str_sql += "'%.2f'" % round(row['close'], 2)
                str_sql += ","
                str_sql += "'%.2f'" % round(row['volume'], 2)
                str_sql += ","
                str_sql += "'%.2f'" % round(row['money'], 2)
                str_sql += ","
                str_sql += "'%.6f'" % round(row['factor'], 6)
                str_sql += "),"
            str_sql = str_sql[:len(str_sql)-1] + ";"

            try:
                mycursor.execute(str_sql)
                mydb.commit()
                findTs.clear()
                firstTs = ts
                findTs.append(ts)
            except Exception as e:
                mydb.rollback()
                g_logger.warning("str_sql=%s", str_sql)
                g_logger.warning(str(e))
                g_logger.exception(e)

def IsSameDay(utc_time1, utc_time2):
    return LocalDayOffset(utc_time1, utc_time2) == 0

def LocalDayOffset(time1, time2):
    time1 = int(time1)
    time2 = int(time2)
    day1 = (time1 + 8 * 3600) // 86400
    day2 = (time2 + 8 * 3600) // 86400
    return day1 - day2

#检测数据是否有缺失
def CheckPriceData(code, db_name, securities):
    global mydb
    global gp_trade_days

    g_logger.info("CheckPriceData code:%s, gp_id:%d", code, securities['id'])
    codes = code.split(".")
    if len(codes) != 2:
        g_logger.warning("error code:%s", code)
        return

    tableName = "1min_prices_" + codes[0][-2:]

    #遍历数据检测
    mycursor = mydb.cursor()
    last_ts = 0
    day_fisrt_ts = 0
    try:
        check_sql = "SELECT ts FROM " + db_name + "." + tableName +" WHERE gp_id='" + str(securities['id']) + "' ORDER BY ts ASC;"
        mycursor.execute(check_sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        count=0
        for row in results:
            ts = int(row[0])
            day_shifting_ts = ((ts + 8 * 3600) % 86400)
            last_day_shifting_ts = ((last_ts + 8 * 3600) % 86400)
            if (ts-last_ts)!=60 and day_shifting_ts != (9*3600+30*60) and day_shifting_ts != (13*3600):
                g_logger.warning("code:%s, gp_id:%d, ts:%d", code, securities['id'], ts)

            if day_shifting_ts == (9*3600+30*60) and (last_day_shifting_ts != (15*3600-60)) and (last_ts!=0):
                g_logger.warning("code:%s, gp_id:%d, last_ts:%d", code, securities['id'], last_ts)

            if day_shifting_ts == (13*3600) and (last_day_shifting_ts != (11*3600+30*60-60)) and (last_ts!=0):
                g_logger.warning("code:%s, gp_id:%d, last_ts:%d", code, securities['id'], last_ts)

            if last_ts==0:
                day_fisrt_ts = ts
                count+=1
            elif IsSameDay(ts, day_fisrt_ts):
                count+=1
            elif count!=240:
                g_logger.warning("code:%s, gp_id:%d, day_fisrt_ts:%d ts:%d, count:%d", code, securities['id'], day_fisrt_ts, ts, count)
                day_fisrt_ts = ts
                count = 1

            last_ts = ts
    except Exception as e:
        g_logger.warning(str(e))
        g_logger.exception(e)


#获取所有的gp代码
def GetAllSecurities(securities_type):
    g_logger.info('GetAllSecurities begin! securities_type=%s', securities_type)
    global mydb
    sec_types =[]
    sec_types.append(securities_type)
    db_name = ''
    if securities_type=='stock':
        db_name = 'gp'
    elif securities_type=='index':
        db_name='idx'
    elif securities_type=='futures':
        db_name='futures'

    mycursor = mydb.cursor()
    all_codes = dict()
    try:
        check_sql = "SELECT code, name FROM " + db_name + ".securities;"
        mycursor.execute(check_sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        for row in results:
            code = row[0]
            name = row[1]
            all_codes[code] = name
    except Exception as e:
        g_logger.warning(str(e))
        g_logger.exception(e)

    securities = get_all_securities(types=sec_types, date=None)
    try:
        count = 0
        for index, row in securities.iterrows():
            count+=1
            code = index
            if code in all_codes:
                continue
            display_name = row['display_name']
            name = row['name']
            start_date = row['start_date']
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = row['end_date']
            end_date = end_date.strftime("%Y-%m-%d")
            insert_sql = "insert into " + db_name + ".securities(code, display_name, name, start_date, end_date) values('" \
                        + code + "', '" + display_name + "', '"+ name + "', '"+ start_date + "', '"+ end_date + "');"

            mycursor.execute(insert_sql)
            mydb.commit()
            all_codes[code] = name
        g_logger.info('GetAllSecurities count=%d', count)
    except Exception as e:
        mydb.rollback()
        g_logger.warning(str(e))
        g_logger.exception(e)

#加载所有的gp代码
def LoadAllSecurities(securities_type):
    g_logger.info('LoadAllSecurities begin! securities_type=%s', securities_type)
    global mydb
    global gp_securities
    db_name = ''
    if securities_type=='stock':
        db_name = 'gp'
    elif securities_type=='index':
        db_name='idx'
    elif securities_type=='futures':
        db_name='futures'

    mycursor = mydb.cursor()
    try:
        sec_sql = "SELECT id, code, start_date, end_date FROM " + db_name + ".securities"
        mycursor.execute(sec_sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        for row in results:
            oneSecurities = dict()
            oneSecurities['id'] = int(row[0])
            oneSecurities['code'] = row[1]
            oneSecurities['start_date'] = row[2]
            oneSecurities['end_date'] = row[3]
            gp_securities[row[1]] = oneSecurities
            # g_logger.debug("code=%s, securities=%s", row[1], str(oneSecurities))
        g_logger.debug("securities length=%d", len(gp_securities))
    except Exception as e:
        g_logger.warning(str(e))
        g_logger.exception(e)

#获取交易日
def GetTradeDays(year):
    global mydb
    start_date=str(year)+'-01-01'
    end_date=str(year)+'-12-31'
    trade_days = get_trade_days(start_date=start_date, end_date=end_date)
    mycursor = mydb.cursor()
    try:
        for trade_day in trade_days:
            day = trade_day.strftime('%Y-%m-%d')

            insert_sql = "insert into gp.gp_trade_days(day) values('" \
                         + day + "');"

            mycursor.execute(insert_sql)
            mydb.commit()
    except Exception as e:
        mydb.rollback()
        g_logger.warning(str(e))
        g_logger.exception(e)

#加载所有的交易日
def LoadTradeDays():
    global mydb
    global gp_trade_days
    g_logger.info('LoadTradeDays begin!')
    mycursor = mydb.cursor()
    try:
        sec_sql = "SELECT day FROM gp.gp_trade_days ORDER BY day ASC"
        mycursor.execute(sec_sql)
        # 获取所有记录列表
        results = mycursor.fetchall()
        for row in results:
            gp_trade_days.append(row[0])

        g_logger.debug("gp_trade_days length=%d", len(gp_trade_days))
    except Exception as e:
        g_logger.warning(str(e))
        g_logger.exception(e)


def main():
    Initialize('config.ini')
    #登录
    g_logger.info('auth begin!')
    auth('1588963xxxx', 'ABCDefxxxx')

    is_auth_succ = is_auth()
    if is_auth_succ == False:
        g_logger.warning("auth failed!")
        return
    else:
        g_logger.info('auth success!')

    # GetAllSecurities('futures')
    # return

    securities_type = 'futures'
    db_name = ''
    if securities_type=='stock':
        db_name = 'gp'
    elif securities_type=='index':
        db_name='idx'
    elif securities_type=='futures':
        db_name='futures'

    LoadAllSecurities(securities_type)
    LoadTradeDays()
    codes = ['IF1109.CCFX','IF1110.CCFX','IF1111.CCFX']
    #AP2110.XZCE,BU2109.XSGE,C2109.XDCE,CF2109.XZCE,CS2109.XDCE,FU2109.XSGE,JD2109.XDCE,M2109.XDCE,MA2109.XZCE,P2109.XDCE,PP2109.XDCE,RB2110.XSGE,RM2109.XZCE,SA2109.XZCE,SR2109.XZCE,TA2109.XZCE
    # codes = ['AP2110','CF2109','CJ2109','CY2109','FG2109','MA2109','OI2109','PF2109','PK2110',
    #          'RM2109','SA2109','SF2109','SM2109','SR2109','TA2109','UR2109','ZC2109','A2109',
    #          'B2108','C2109','CS2109','EB2108','EG2109','I2109','J2109','JD2109','JM2109',
    #          'L2109','LH2109','M2109','P2109','PG2108','PP2109','V2109','Y2109',
    #          'AL2108','BC2109','BU2109','CU2108','FU2109','HC2110','LU2110','NI2108','NR2109',
    #          'PB2108','RB2110','RU2109','SN2108','SP2109','SS2108','ZN2108']
    # codes = ['AP2110.XZCE','BU2109.XSGE','C2109.XDCE','CF2201.XZCE','CS2109.XDCE','FU2109.XSGE',
    #          'JD2109.XDCE','M2201.XDCE','MA2201.XZCE','P2109.XDCE','PP2109.XDCE','RB2201.XSGE',
    #          'RM2201.XZCE','SA2201.XZCE','SR2201.XZCE','TA2201.XZCE']
    # codes = ['AP8888.XZCE','BU8888.XSGE','C8888.XDCE','CF8888.XZCE','CS8888.XDCE','FU8888.XSGE',
    #     'JD8888.XDCE','M8888.XDCE','MA8888.XZCE','P8888.XDCE','PP8888.XDCE','RB8888.XSGE',
    #     'RM8888.XZCE','SA8888.XZCE','SR8888.XZCE','TA8888.XZCE']
    # units = {'1min':'1m','5min':'5m', '15min':'15m', '30min':'30m'}
    units = {'1min':'1m'}
    for code in codes:
        g_logger.debug("code:%s", code)
        securities = None
        for sec_code, security in gp_securities.items():
            # if sec_code.find(code+'.X')==0:
            if sec_code.find(code)==0:
                securities = security
                # break

        if securities is None:
            g_logger.warning("gp_securities not find code:%s", code)
            continue

        for unit in units.keys():
            start_date = '2011-01-01'
            # start_date = '2020-01-01'
            # if unit=='1min':
            #     start_date = '2021-01-01'
            # elif unit=='5min':
            #     start_date = '2020-01-01'
            # elif unit=='15min':
            #     start_date = '2018-01-01'
            # elif unit=='30min':
            #     start_date = '2018-01-01'

            end_date = '2011-12-31'
            # end_date = time.strftime("%Y-%m-%d", time.localtime())
            GetBars(securities_type, securities['code'], db_name, securities, unit, start_date, end_date)
            # RepairPriceData(code, db_name, securities, '2005-01-04', '2021-03-16')
            # CheckPriceData(code, db_name, securities)

    count_rsp = get_query_count()
    g_logger.debug("count_rsp=%s", str(count_rsp))


if __name__ == "__main__":
    main()


