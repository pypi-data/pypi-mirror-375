import asyncio
import aiohttp
import json
import yaml
import threading
import time
import re
from datetime import datetime
import os
import csv
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
from asyncio import Queue
from .analyzer import FutureMethod
# from compute_index import ComputeIndex

FUNCTION_ID_RTN_STRATEGY_LOG = 11004

gstop_event = asyncio.Event()


class Trade:
    def __init__(self) -> None:
        self.datetime = ''
        self.trading_datetime = ''
        self.order_book_id = ''
        self.symbol = ''
        self.side = ''
        self.position_effect = ''
        self.exec_id = 0
        self.tax = 0
        self.commission = 0
        self.last_quantity = 0
        self.last_price = 0
        self.order_id = 0
        self.transaction_cost = 0
        self.finish = False


class Position:
    def __init__(self) -> None:
        self.date = ''
        self.order_book_id = ''
        self.symbol = ''
        self.margin = 0
        self.contract_multiple = 0
        self.last_price = 0
        self.long_pnl = 0
        self.long_margin = 0
        self.long_market_value = 0
        self.long_quantity = 0
        self.long_avg_open_price = 0
        self.short_pnl = 0
        self.short_margin = 0
        self.short_market_value = 0
        self.short_quantity = 0
        self.short_avg_open_price = 0


class Account:
    def __init__(self) -> None:
        self.date = ''
        self.cash = 0
        self.total_value = 0
        self.market_value = 0
        self.unit_net_value = 0
        self.units = 0
        self.static_unit_net_value = 0

class BackInfo:
    def __init__(self):
        self.init_cash = 0.0
        self.start = ""
        self.end = ""
        self.risk_free_rate = 0.0

class WebSocketClient:
    def __init__(self, uri, user, passwd, strategy_name, strategy_param, upload_strategy, info : BackInfo ):
        self.uri = uri
        self.user = user
        self.passwd = passwd
        self.strategy_name = strategy_name
        self.strategy_id = 0
        self.strategy_param = strategy_param
        self.info = info
        self.session = None
        self.websocket = None
        self.connected = False
        self.strategy_id = -1
        self.select_strategy = ""
        self.results = {"position": [], "trades": []}
        self.condition = threading.Condition()
        self.lock = asyncio.Lock()  # 创建一个锁
        self.ready = False
        self._isFinish = False
        self.path = ''
        self.upload_strategy = upload_strategy
        self.message_queue = asyncio.Queue()  # 消息队列
        self.finish = False
        self.time_stamp = self.get_current_time_string()
        self.instruments = {}
        self.dailyData = {}
        self.dailyDataLastSnap = {}
        self.trade_dates = []
        self.rq_trade_file = ""
        self.rq_positions_file = ""

        self.func_map = {
            10001: self.handle_login_response,
            10005: self.handle_create_strategy_response,
            10020: self.handle_rtn_strategy_status,
            12029: self.handle_query_trade_list,
            11004: self.handle_rtn_strategy_log,
            12030: self.handle_query_position_list,
            12032: self.handle_rtn_back_results,
            12033: self.handle_rtn_message,
            12035: self.handle_daily_data,
        }

        self.analyzer = FutureMethod(self.trade_dates, self.dailyData, self.dailyDataLastSnap, self.rq_trade_file
                                              , self.rq_positions_file, self.info.init_cash
                                              , self.info.start, self.info.end)


        # 日志级别映射??
        self.log_levels = {
            0: 'Verbose',
            1: 'Debug',
            2: 'Info',
            3: 'Warn',
            4: 'Error',
            5: 'Fatal'
        }

    async def update_positions(self, new_data):
        # 处理接收到的新数据并更新结果
        for item in new_data:
            self.results["position"].extend(item['positionList'])
            # position_list = item['positionList']
            # date_dict = {}
            # for i in range(len(position_list)):
            #     # 相同交易日
            #     position = position_list[i]
            #     date_dict[position['tradingDay']].append(position)

            # for key, value in date_dict.items():
            #     print(f"date key:{key}")

    async def isFinish(self):
        async with self.lock:  # 加锁以确保线程安全
            return self._isFinish

    async def setFinish(self, value):
        async with self.lock:  # 加锁以确保线程安全
            self._isFinish = value

    def wait_for_condition(self):
        with self.condition:
            while not self.ready:
                self.condition.wait()

    def set_condition(self):
        time.sleep(2)  # 模拟一些工作
        with self.condition:
            self.ready = True
            self.condition.notify_all()  # 通知所有等待的线程

    async def connect(self):
        """建立 WebSocket 连接并保持活动状态"""
        self.session = aiohttp.ClientSession()
        try:
            self.websocket = await self.session.ws_connect(self.uri, max_msg_size=10 * 1024 * 1024)
            self.connected = True

            # 登录请求
            await self.login_request()
            # 启动消息处理任务
            asyncio.create_task(self.process_messages())

            # 监听消息
            # asyncio.create_task(self.listen())
            await self.listen()

        except Exception as e:
            print(f"连接失败: {e}")
            await self.close_session()  # 确保关闭会话
            await self.reconnect()

    async def reconnect(self):
        """尝试重新连接"""
        print("尝试重新连接...")
        await asyncio.sleep(1)  # 等待 1 秒后重新连接
        await self.connect()

    async def listen(self):
        """监听服务器消息"""
        try:
            async for msg in self.websocket:
                if self.message_queue.full():
                    # 队列满时的处理，这里简单打印日志
                    print("消息队列已满，暂停接收消息")
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self.message_queue.put(msg.data)  # 将消息放入队列
                    # await self.process_response(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(msg.data)
                    print(f"WebSocket 错误1: {self.websocket.exception()}")
                    close_code = self.websocket.close_code
                    print(f"Close code2: {close_code}")
                    # 尝试获取更底层的传输信息
                    transport = self.websocket._response.connection.transport
                    if transport:
                        print(f"Transport info3: {transport.get_extra_info('peername')}")
                    
        except Exception as e:
            print(f"监听时发生异常4: {e}")
        finally:
            self.connected = False

    async def process_messages(self):
        """处理消息队列中的消息"""
        while True:
            # response = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)  # 从队列中获取消息
            response = await self.message_queue.get()  # 从队列中获取消息
            try:
                data = json.loads(response)
                funcion_id = data.get("funcionId")
                err_id = data.get("errId")
                err_msg = data.get("errMsg")
                response_data = data.get("data")

                if err_id != 0:
                    print(f"错误代码 {err_id}: {err_msg}")
                    continue

                if funcion_id in self.func_map:
                    await self.func_map[funcion_id](response_data)
            except json.JSONDecodeError:
                print("接收到的消息不是有效的 JSON 格式")

    async def process_response(self, response):
        """处理接收到的消息"""
        try:
            data = json.loads(response)
            funcion_id = data.get("funcionId")
            err_id = data.get("errId")
            err_msg = data.get("errMsg")
            response_data = data.get("data")

            if err_id != 0:
                print(f"错误代码 {err_id}: {err_msg}")
                return

            # 处理对应的 funcionId
            if funcion_id in self.func_map:
                await self.func_map[funcion_id](response_data)

        except json.JSONDecodeError:
            print("接收到的消息不是有效的 JSON 格式")

    async def send_request(self, request_data):
        """发送请求"""
        if self.connected:
            await self.websocket.send_str(json.dumps(request_data))
        else:
            print("WebSocket 尚未连接，无法发送请求")

    def get_current_time_string(self):
        current_time = datetime.now()
        return current_time.strftime("%Y%m%d_%H%M%S")

    async def sub_strategy_message(self):
        request_data = {
            "funcionId": 12034,
            "finished": True,
            "dataType": 1,
            "requestId": 1,
            "errId": 0,
            "errMsg": "",
            "data": [
                {
                    "userId": f"{self.user}"
                }
            ]
        }
        await self.send_request(request_data)

    async def sub_daily_data(self):
        request_data = {
            "funcionId": 12036,
            "finished": True,
            "dataType": 1,
            "requestId": 1,
            "errId": 0,
            "errMsg": "",
            "data": [
                {
                    "userId": f"{self.user}"
                }
            ]
        }
        await self.send_request(request_data)

    async def sub_strategy_log(self):
        request_data = {
            "funcionId": 12014,
            "finished": True,
            "dataType": 1,
            "requestId": 1,
            "errId": 0,
            "errMsg": "",
            "data": [
                {
                    "userId": f"{self.user}"
                }
            ]
        }
        await self.send_request(request_data)

    async def sub_strategy_backresult(self):
        request_data = {
            "funcionId": 12031,
            "finished": True,
            "dataType": 1,
            "requestId": 1,
            "errId": 0,
            "errMsg": "",
            "data": [
                {
                    "userId": f"{self.user}"
                }
            ]
        }
        await self.send_request(request_data)

    async def login_request(self):
        """发送登录请求"""
        request_data = {
            "funcionId": 10001,
            "finished": True,
            "dataType": 1,
            "requestId": 1,
            "errId": 0,
            "errMsg": "",
            "data": [
                {
                    "userName": self.user,
                    "passWord": self.passwd
                }
            ]
        }
        await self.send_request(request_data)

    async def handle_login_response(self, data):
        """处理登录响应"""
        if isinstance(data, list) and data:
            response_data = data[0]
            if response_data.get("msg") == "welcome":
                print(f"{self.user}登录成功！")
                await self.sub_strategy_log()

                await self.create_strategy()

            else:
                print("登录失败！")
        else:
            print("无效的响应数据格式")

    async def convert_to_json(self, data):
        """将 Python 对象转换为 JSON 字符串"""
        return json.dumps(data, ensure_ascii=False, indent=4)

    async def create_strategy(self):
        """创建策略请求"""
        await self.sub_strategy_message()
        param = await self.convert_to_json(self.strategy_param)
        await self.sub_daily_data()
        file_content = ''
        try:
            # 读取文件内容
            with open(self.strategy_name, 'r', encoding='utf-8') as file:
                file_content = file.read()
        except Exception as e:
            print(f"策略文件时出错: {e}")
            os._exit(0)
        request = {
            "funcionId": 10005,
            "finished": True,
            "dataType": 1,
            "requestId": 2,
            "errId": 0,
            "errMsg": "",
            "data": [
                {
                    "soName": self.strategy_name,
                    "param": param,
                    "operationType": 1,
                    "strategyId": 0,
                    "strategyType": 2,
                    "frequencyType": 1,
                    "status": 0,
                    "userId": self.user,
                    "strategyfile": file_content,
                    "sourceType": self.upload_strategy
                }
            ]
        }
        await self.send_request(request)

    async def query_trade_list(self):

        request_data = {
            "funcionId": 12029,
            "finished": True,
            "dataType": 1,
            "requestId": 1,
            "errId": 0,
            "errMsg": "",
            "data": [{
                "strategyId": self.select_strategy["strategyId"]
            }]
        }
        await self.send_request(request_data)

    async def query_position_list(self):

        request_data = {
            "funcionId": 12030,
            "finished": True,
            "dataType": 1,
            "requestId": 1,
            "errId": 0,
            "errMsg": "",
            "data": [{
                "strategyId": self.select_strategy["strategyId"]
            }]
        }
        await self.send_request(request_data)

    async def start_strategy(self):
        """ 开始策略请求 """
        param = await self.convert_to_json(self.strategy_param)
        self.strategy_id = self.select_strategy["strategyId"]
        request = {
            "funcionId": 10005,
            "finished": True,
            "dataType": 1,
            "requestId": 2,
            "errId": 0,
            "errMsg": "",
            "data": [
                {
                    "soName": self.strategy_name,
                    "param": self.select_strategy["param"],
                    "operationType": 5,
                    "strategyId": self.select_strategy["strategyId"],
                    "strategyType": 2,
                    "frequencyType": 1,
                    "status": self.select_strategy["status"],
                    "userId": self.user,
                    "sourceType": 1
                }
            ]
        }

        await self.send_request(request)

    async def handle_create_strategy_response(self, data):
        """处理创建策略响应"""
        await self.sub_strategy_backresult()
        # print(f"处理创建策略响应: {data}")
        # 过滤出 soName 为 self.strategy_name 的对象

        filtered_data = [item for item in data]

        # 如果有匹配的对象，则找到 strategyid 最大的对象
        if filtered_data:
            self.select_strategy = max(filtered_data, key=lambda x: x['strategyId'])

            if self.select_strategy["status"] == 2:
                await self.start_strategy()
                self.strategy_id = int(self.select_strategy["strategyId"])
        else:
            print("创建策略失败")

    async def close_session(self):
        """关闭客户端会话"""
        try:
            if self.websocket and not self.websocket.closed:
                await self.websocket.close()
            if self.session and not self.session.closed:
                await self.session.close()
                self.session = None
            print("客户端会话已关闭")
            os._exit(0)
        except Exception as e:
            print(f"关闭会话时发生错误: {e}")

    async def handle_rtn_strategy_status(self, data):
        filtered_data = [item for item in data if item['strategyId'] == self.strategy_id]
        if filtered_data:
            self.select_strategy = filtered_data[0]

            # 屏蔽以下代码，由后台主推每日推荐数据接口处理数据
            # if self.select_strategy["status"] == 6:
            #     print("策略完成状态")
            #     await self.query_trade_list()

    # 秒级时间戳转换
    def convert_millisecond_time_stamp(self, timestamp):
        datetime_str = ''
        datetime_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")
        return datetime_str

    async def handle_query_trade_list(self, data):
        for item in data:
            trade_list = item["tradeList"]
            # 处理成交字段信息
            for i in range(len(trade_list)):
                timestamp = trade_list[i]["exchangeTradeTime"] / 1000.0  # 毫秒转成秒
                trade_list[i]["exchangeTradeTime"] = self.convert_millisecond_time_stamp(timestamp)
            self.results["trades"] = trade_list

        await self.query_position_list()

    async def handle_rtn_strategy_log(self, data):
        param = self.strategy_param
        log_file_name = self.strategy_name.split(".")[0] + str(self.strategy_id) + ".log"
        log_file_path = os.path.join(param["env"]["log_path"], log_file_name)  # 替换为实际的日志文件路径
        log_to_terminal = param["env"]["stdout"]

        # 如果日志文件所在目录不存在，则创建目录
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        file_handler = open(log_file_path, 'a', encoding='utf-8')  # 以追加模式打开文件

        for entry in data:
            if "logLevel" not in entry:
                continue
            # 过滤非本策略的日志
            strategy_id = entry['strategyId']
            if strategy_id != self.strategy_id:
                continue
            log_level = entry['logLevel']
            log_message = entry['logMessage']
            log_time = entry['logTime']

            if "加载" in log_message:
                print(log_message)
            # 转换 logTime 为可视化时间
            # 假设 logTime 是以微秒为单位的时间戳
            readable_time = datetime.fromtimestamp(log_time / 1_000_000).strftime('%Y-%m-%d %H:%M:%S')

            # 将日志信息写入到日志文件
            file_handler.write(
                f"时间: {readable_time} 日志级别: {self.log_levels.get(log_level, 'Unknown')} 日志信息:{log_message.strip()}\n")

            # 打印格式化的日志信息
            if log_to_terminal == "yes":
                print(
                    f"时间: {readable_time} 日志级别: {self.log_levels.get(log_level, 'Unknown')} 日志信息:{log_message.strip()}")

        if file_handler:
            file_handler.close()

        await self.try_finish()

    async def convert_trade_list_to_rq(self, trades):
        if len(trades) == 0:
            return
        
        rq_trades = []
        for i in range(len(trades)):
            uni_trade = trades[i]
            rq_trade = Trade()
            rq_trade.datetime = uni_trade['tradingDay']
            rq_trade.trading_datetime = uni_trade['exchangeTradeTime']
            rq_trade.order_book_id = uni_trade['instrumentId']
            rq_trade.symbol = ''
            rq_trade.side = uni_trade['side']
            rq_trade.position_effect = uni_trade['offset']
            rq_trade.exec_id = uni_trade['tradeId']
            rq_trade.tax = 0
            rq_trade.commission = uni_trade['commission']
            rq_trade.last_quantity = uni_trade['volume']
            rq_trade.last_price = uni_trade['price']
            rq_trade.order_id = uni_trade['orderId']
            rq_trade.transaction_cost = uni_trade['commission']
            rq_trades.append(rq_trade.__dict__)
        pd_data = pd.DataFrame(rq_trades)
         # 拼接完整的文件路径
        self.rq_trade_file = self.path + self.time_stamp + "_" + self.strategy_name.rstrip('.py') + '_' + str(self.strategy_id) + "rq_trades.csv"
        #file_path = self.path + 'rq_trades.csv'
        # 检查文件是否存在
        file_exists = os.path.isfile(self.rq_trade_file)
        # 写入 CSV 文件，根据文件是否存在决定是否包含列头
        pd_data.to_csv(self.rq_trade_file, float_format='%.6f', mode='a' if file_exists else 'w', index=False, header=not file_exists)
    def get_contract_multiplier(self, instrument_id):
        """
        从合约字典中获取指定合约的合约乘数
        
        参数:
        - instrument_id: 合约ID，如"m2409"
        - contract_dict: 合约信息字典，格式为 {instrument_id: 合约详情}
        
        返回:
        - 合约乘数 (int/float)，若合约不存在则返回None
        """
        # 检查合约是否存在于字典中
        if instrument_id in self.instruments:
            return self.instruments[instrument_id].get('contract_multiplier')
        else:
            print(f"警告: 合约 {instrument_id} 不存在")
            return 1.0
        
    async def convert_daily_positions_to_rq(self, daily_positions):
        if len(daily_positions) == 0:
            return
        
        position_dict = {}
        for i in range(len(daily_positions)):
            # 合并相同交易日的持仓
            position = json.loads(daily_positions[i])
            date_key = position['trading_day']
            instrument_key = position['instrument_id']
            key = date_key + '.' + instrument_key
            # print(f"key:{key}")
            if key not in position_dict:
                position_dict[key] = []
            position_dict[key].append(position)

        rq_daily_positions = []
        for positions in position_dict.values():
            instrument_position = Position()
            for i in range(len(positions)):
                position = positions[i]
                instrument_position.date = position['trading_day']
                instrument_position.order_book_id = position['instrument_id']
                instrument_position.symbol = ''
                instrument_position.margin = position['margin']
                instrument_position.contract_multiple = self.get_contract_multiplier(position['instrument_id'])
                instrument_position.last_price = position['last_price']
                if position['direction'] == 'Long':
                    instrument_position.long_pnl = position['position_pnl']
                    instrument_position.long_margin = 0
                    instrument_position.long_market_value = 0
                    instrument_position.long_quantity = position['volume']
                    instrument_position.long_avg_open_price = position['avg_open_price']
                elif position['direction'] == 'Short':
                    instrument_position.short_pnl = position['position_pnl']
                    instrument_position.short_margin = 0
                    instrument_position.short_market_value = 0
                    instrument_position.short_quantity = position['volume']
                    instrument_position.short_avg_open_price = position['avg_open_price']
            # if instrument_position.short_quantity == 0 and instrument_position.long_quantity == 0:
            #     continue
            rq_daily_positions.append(instrument_position.__dict__)
        pd_data = pd.DataFrame(rq_daily_positions)
        # 拼接完整的文件路径
        self.rq_positions_file = self.path + self.time_stamp + "_" + self.strategy_name.rstrip('.py') + '_' + str(self.strategy_id) + "rq_daily_positions.csv"
        #file_path = self.path + 'rq_daily_positions.csv'
        # 检查文件是否存在
        file_exists = os.path.isfile(self.rq_positions_file)
        # 写入 CSV 文件，根据文件是否存在决定是否包含列头
        pd_data.to_csv(self.rq_positions_file, float_format='%.6f', mode='a' if file_exists else 'w', index=False, header=not file_exists)

    async def try_finish(self):
        if self.finish == True and self.message_queue.qsize() == 0:
            # print("策略回测成功！...")
            # os._exit(0)
            pass

    async def convert_daily_portfolio_to_rq(self, daily_portfolio):
        if len(daily_portfolio) == 0:
            return
        
        rq_daily_portfolio = []
        for i in range(len(daily_portfolio)):
            uni_portfolio = daily_portfolio[i]
            rq_portfolio = Account()
            rq_portfolio.date = uni_portfolio['tradingDay']
            rq_portfolio.cash = uni_portfolio['avail']
            rq_portfolio.total_value = uni_portfolio['initialEquity'] - uni_portfolio['intradayFee'] + uni_portfolio[
                'realizedPnl'] + uni_portfolio['unrealizedPnl']
            rq_portfolio.market_value = uni_portfolio['marketValue']
            rq_portfolio.unit_net_value = 0
            rq_portfolio.units = uni_portfolio['initialEquity']
            rq_portfolio.static_unit_net_value = 0
            rq_daily_portfolio.append(rq_portfolio.__dict__)
        pd_data = pd.DataFrame(rq_daily_portfolio)
        # 拼接完整的文件路径
        file_path = self.path + 'rq_daily_portfolio.csv'
        # 检查文件是否存在
        file_exists = os.path.isfile(file_path)
        # 写入 CSV 文件，根据文件是否存在决定是否包含列头
        pd_data.to_csv(file_path, float_format='%.6f', mode='a' if file_exists else 'w', index=False, header=not file_exists)

    async def show_progress(self, progress):
        """
        此函数用于显示进度条，根据传入的进度值更新显示。
        :param progress: 0 到 1 之间的小数，表示进度
        """
        if progress < 0 or progress > 1:
            raise ValueError("进度值必须在 0 到 1 之间。")
        bar_length = 50
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        percentage = f'{progress * 100:.1f}%'
        print(f'\r|{bar}| {percentage}', end='', flush=True)

    async def handle_rtn_message(self, data):
        for entry in data:
            msg = entry['msg']
            strategy_id = entry['strategyId']
            log_level = entry['level']
            # 处理本策略的日志
            if strategy_id == self.strategy_id:
                print(f"[{self.log_levels.get(log_level, 'Unknown')}]: {msg}")
                print('策略执行发生异常，终止')
                os._exit(0)
        # for entry in data:
        #     msg = entry['msg']
        #     # Verbose 0, Debug 1, Info 2, Warn 3, Error 4, Fatal 5
        #     log_level = entry['level']
        #     print(f"[{self.log_levels.get(log_level, 'Unknown')}]: {msg}")
        #     if log_level >= 4:
        #         print('策略执行发生异常，终止策略!!!')
        #         os._exit(0)


    async def handle_daily_data(self, data):
        is_display_progress_bar = self.strategy_param["env"]["is_display_progress_bar"]
        for entry in data:
            strategy_id = entry["strategyId"]
            if strategy_id != self.strategy_id:
                continue

            data_type = entry["dataType"]
            # 每日订单列表
            if data_type == 1: 
                await self.save_daily_data(entry["orderList"],
                                       self.time_stamp + "_" + self.strategy_name.rstrip('.py') + '_' + str(self.strategy_id) + "_orderList.csv")
            # 每日成交列表
            elif data_type == 2: 
                await self.save_daily_data(entry["tradeList"],
                                       self.time_stamp + "_" + self.strategy_name.rstrip('.py') + '_' + str(self.strategy_id) + "_tradeList.csv")
                # 转成米筐形式的数据
                trade_list = entry["tradeList"]
                await self.convert_trade_list_to_rq(trade_list)
            # 每日持仓列表
            elif data_type == 3: 
                #根据配置是否显示进度条
                if is_display_progress_bar == 1:
                    await self.show_progress(entry["pregress"])
                
                position_list = [json.loads(item) for item in entry["positions"]]
                await self.save_daily_data(position_list,
                                       self.time_stamp + "_" + self.strategy_name.rstrip('.py') + '_' + str(self.strategy_id) + "_positions.csv")
                # 转成米筐形式的数据、
                await self.convert_daily_positions_to_rq(entry["positions"])
            # 每日账户资金情况
            elif data_type == 4: 
                await self.save_daily_data(entry["dailyFound"],
                                       self.time_stamp + "_" + self.strategy_name.rstrip('.py') + '_' + str(self.strategy_id) + "_daily_found_results.csv")
                # 转成米筐形式的数据
                daily_portfolio = entry["dailyFound"]
                    
                await self.convert_daily_portfolio_to_rq(daily_portfolio)
            elif data_type == 5:
                self.trade_dates = entry["tradingDays"]
                for item in entry["instruments"]:
                    try:
                        # 解析JSON字符串
                        parsed = json.loads(item)
                        # 使用instrument_id作为键，整个对象作为值
                        self.instruments[parsed['instrument_id']] = parsed
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"处理数据时出错: {e}")
                        continue  # 跳过错误项，继续处理其他项
            elif data_type == 6:
                for item in entry["dailyData"]:
                    try:
                        # 解析JSON字符串
                        #parsed = json.loads(item)
                        # 使用instrument_id作为键，整个对象作为值
                        key = f"{item['instrumentId']}_{item['tradingDay']}"
                        self.dailyData[key] = item['closePrice']
                        self.dailyDataLastSnap[item['instrumentId']] = item['closePrice']
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"处理数据时出错: {e}")
                        continue  # 跳过错误项，继续处理其他项
            else:
                pass

    async def save_daily_data(self, data, file_name):
        if len(data) == 0:
            return
         
        param = self.strategy_param
        self.path = param["env"]["result_path"]
        if not os.path.exists(self.path):
            os.makedirs(self.path)

            # def process_data(self, data, file_name_before):
        trade_lists = data
        df = pd.DataFrame(trade_lists)

        # 拼接完整的文件路径
        file_path = self.path + file_name

        # 检查文件是否存在
        file_exists = os.path.isfile(file_path)

        # 写入 CSV 文件，根据文件是否存在决定是否包含列头
        df.to_csv(file_path, float_format='%.6f', mode='a' if file_exists else 'w', index=False, header=not file_exists)

    async def handle_rtn_back_results(self, data):
        file_name_before = self.time_stamp + "_" + self.strategy_name.rstrip('.py') + '_' + str(self.strategy_id)

        if not os.path.exists(self.path):
                os.makedirs(self.path)
        self.analyzer = FutureMethod(self.trade_dates, self.dailyData, self.dailyDataLastSnap, self.rq_trade_file
                                              , self.rq_positions_file, self.info.init_cash
                                              , self.info.start, self.info.end, self.path + file_name_before + "_", self.info.risk_free_rate)
        
        self.analyzer.handle_date()
        for entry in data:
            strategy_id = entry["strategyId"]
            if strategy_id != self.strategy_id:
                continue

            print("\n策略回测成功...")

            param = self.strategy_param
            self.path = param["env"]["result_path"]
            # is_prompt = param["env"]["is_prompt"]
            

            # 设置中文字体
            # plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']  # 或者 'Noto Sans CJK'
            # plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
            
            # 在单独线程中运行同步方法
            # compute_index_obj = ComputeIndex()
            # await asyncio.to_thread(
            #     compute_index_obj.run,
            #     param,
            #     self.path + file_name_before + '_positions.csv',
            #     self.path + file_name_before + '_daily_found_results.csv',
            #     self.path,
            #     is_prompt
            # )

            accReturn = entry["accReturn"]
            df = pd.DataFrame(list(accReturn.items()), columns=['time', 'value'])

            # 将字符串时间转换为 datetime 对象，指定格式
            df['time'] = pd.to_datetime(df['time'], format='%Y.%m.%d')

            # 创建文本信息的图表
            plt.figure(figsize=(12, 2))  # 高度较小
            plt.axis('off')  # 不显示坐标轴

            # 可能会存在最后的结果为None的情况，这种情况下，就不参与下面的计算
            if entry["stdReturn"] and entry["sharpRatio"] and entry["backReturn"] and entry["annualizedReturn"] and entry["calmarRatio"]:
                # 获取数据
                stdReturn = entry["stdReturn"] * 100
                # 以数字带2-4位小数显示
                sharpRatio = entry["sharpRatio"]
                backReturn = entry["backReturn"] * 100
                annualizedReturn = entry["annualizedReturn"] * 100
                # calmar应该是正的，最大回撤取绝对值，以数字带2-4位小数显示
                calmarRatio = abs(entry["calmarRatio"])

                winRatio = 0.0
                if entry["winRatio"] != None:
                    winRatio = entry["winRatio"] * 100

                maxDrawdown = entry["drawdown"]["maxDrawdown"] * 100
                peakTime = entry["drawdown"]["peakTime"]
                troughTime = entry["drawdown"]["troughTime"]

                # 使用 figtext 方法添加文本信息
                # 使用 figtext 方法添加文本信息，分成两行，每行三个
                plt.figtext(0.2, 0.5, f'backReturn: {backReturn:.4f}%', ha='center', fontsize=12)
                plt.figtext(0.5, 0.5, f'annualizedReturn: {annualizedReturn:.4f}%', ha='center', fontsize=12)
                plt.figtext(0.8, 0.5, f'stdReturn: {stdReturn:.4f}%', ha='center', fontsize=12)

                plt.figtext(0.2, 0.3, f'sharpRatio: {sharpRatio:.4f}', ha='center', fontsize=12)
                plt.figtext(0.5, 0.3, f'calmarRatio: {calmarRatio:.4f}', ha='center', fontsize=12)
                plt.figtext(0.8, 0.3, f'winRatio: {winRatio:.4f}%', ha='center', fontsize=12)

                plt.figtext(0.2, 0.1, f'maxDrawdown: {maxDrawdown:.4f}%', ha='center', fontsize=12)
                plt.figtext(0.5, 0.1, f'peakTime: {peakTime}', ha='center', fontsize=12)
                plt.figtext(0.8, 0.1, f'troughTime: {troughTime}', ha='center', fontsize=12)

                # 保存文本信息图表为图片
                plt.tight_layout()
                plt.savefig(self.path + 'text_info.png')  # 保存为 text_info.png
                plt.close()  # 关闭图形以释放资源

                # 创建图表并保存为图片
                plt.figure(figsize=(12, 6))
                plt.plot(df['time'], df['value'], marker='o', label='Value Line')
                plt.title('Time vs Value')
                plt.xlabel('Time')
                plt.ylabel('Value')
                plt.xticks(rotation=45)
                plt.grid()
                plt.legend()
                plt.tight_layout()
                plt.savefig(self.path + 'chart.png')  # 保存为 chart.png
                plt.close()  # 关闭图形以释放资源

                # 拼接两张图片
                # text_img = Image.open(self.path + 'text_info.png')
                # chart_img = Image.open(self.path + 'chart.png')

                # # 创建一个新的空图像，宽度为两张图像的宽度，高度为两者高度之和
                # combined_img = Image.new('RGB', (text_img.width, text_img.height + chart_img.height))

                # # 将两张图片粘贴到合并的图像中
                # combined_img.paste(text_img, (0, 0))  # 将文本图放在上面
                # combined_img.paste(chart_img, (0, text_img.height))  # 将图表放在下面

                # # 保存拼接后的图像
                # combined_img.save(self.path + file_name_before + '_combined_output.png')

            self.finish = True
            print("策略最终回测数据处理完毕！")
            await self.try_finish()
            # os._exit(0)

    async def save_results(self, config):
        """
        保存结果到CSV文件
        :param config: 配置文件路径
        """
        try:
            # 读取配置文件
            with open(config, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)

            # 确保结果中有数据
            if not self.results.get("trades") or not self.results.get("position"):
                print("没有可保存的结果数据")
                return

            # 构建保存路径
            strategy_id = str(self.results["trades"][0]["strategyId"])
            result_dir = config_data["env"].get("result_path", "results")

            # 保存持仓数据
            await self._save_positions(result_dir, strategy_id)

            # 保存交易数据
            await self._save_trades(result_dir, strategy_id)

        except Exception as e:
            print(f"保存结果失败: {e}")
            raise

    async def _save_positions(self, result_dir, strategy_id):
        """保存持仓数据"""
        try:
            positions = self.results.get("position", [])
            if not positions:
                return

            csv_file_path = os.path.join(result_dir, f"{strategy_id}_positions.csv")
            os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                # 获取表头
                headers = list(positions[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=headers)

                # 写入表头
                csvfile.write(','.join(headers) + '\n')

                # 写入数据
                for position in positions:
                    csvfile.write(','.join(str(position[header]) for header in headers) + '\n')
        except Exception as e:
            print(f"保存持仓数据失败: {e}")
            raise

    async def _save_trades(self, result_dir, strategy_id):
        """保存交易数据"""
        try:
            trades = self.results.get("trades", [])
            if not trades:
                return

            csv_file_path = os.path.join(result_dir, f"{strategy_id}_trades.csv")
            os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                headers = list(trades[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=headers)

                csvfile.write(','.join(headers) + '\n')

                for trade in trades:
                    csvfile.write(','.join(str(trade[header]) for header in headers) + '\n')
        except Exception as e:
            print(f"保存交易数据失败: {e}")
            raise

    async def handle_query_position_list(self, data):
        # print(f"处理策略持仓推送: ", data)
        await self.update_positions(data)
        # self.results["position"] = data


uri = ""
user = ""
passwd = ""
strategy_name = ""
strategy_param = ""

gclient = WebSocketClient("", "", "", "", "", 0, BackInfo())


def read_yaml_file(filepath):
    """读取 YAML 文件"""
    with open(filepath, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)



async def run_func(config_data):
    """运行函数，读取配置并执行相关逻辑"""
    env_config = config_data.get("env", {})
    uri = env_config.get("uri")
    user = env_config.get("user")
    passwd = env_config.get("passwd")
    strategy_name = env_config.get("pystrategy")
    strategy_param = config_data
    upload_strategy = env_config.get("upload_strategy")

    info = BackInfo()
    base_config = config_data.get("base", {})
    info.init_cash = base_config.get("accounts")
    info.start = base_config.get("start_date")
    info.end = base_config.get("end_date")
    info.risk_free_rate = base_config.get("risk_free_rate")

    global gclient
    gclient = WebSocketClient(uri, user, passwd, strategy_name, strategy_param
                              , upload_strategy
                              , info)
    await gclient.connect()


async def monitor_condition():
    global gclient
    while True:
        # 检查 gclient.isFinish() 的返回值
        if await gclient.isFinish():
            print("Condition met, stopping the execution.")
            gstop_event.set()  # 设置事件，通知 run_func 停止
            break  # 退出循环
        await asyncio.sleep(0.5)  # 每 0.5 秒检查一次


async def run_strategy(config_data):
    global gclient
    try:
        # 创建任务
        task = asyncio.create_task(run_func(config_data))
        monitor_task = asyncio.create_task(monitor_condition())

        # 等待任务完成或条件满足
        done, pending = await asyncio.wait(
            [task, monitor_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # 如果条件满足，取消任务
        if gstop_event.is_set():
            # 取消未完成的任务
            for t in pending:
                t.cancel()
            # 等待取消完成
            await asyncio.gather(*pending, return_exceptions=True)

            # 保存结果
            # if gclient:
            #     await gclient.save_results(config)

    except asyncio.CancelledError:
        print("run_func was cancelled.")
    finally:
        # 确保关闭 session
        if gclient and gclient.session:
            await gclient.close_session()


def is_valid_ws_uri(uri):
    pattern = re.compile(r'^ws(s)?://[\w.-]+(:\d+)?(/[\w./-]*)?$')
    return bool(pattern.match(uri))


def is_py_file(filename):
    return filename.endswith('.py')


def convert_date(date_str, date_formats):
    for fmt in date_formats:
        try:
            # 尝试使用当前格式解析日期字符串
            dt = datetime.strptime(date_str, fmt)
            # 将解析后的日期对象转换为 YYYY.mm.dd 格式
            return dt.strftime('%Y.%m.%d')
        except ValueError:
            continue
    # 如果所有格式都无法解析，返回 None
    return None


def check_missing_fields(data, required_fields):
    missing_fields_info = []
    if isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, dict):
                missing = [field for field in required_fields if field not in item]
                if missing:
                    missing_fields_info.append(f"第 {index + 1} 个对象缺失字段: {', '.join(missing)}")
    elif isinstance(data, dict):
        missing = [field for field in required_fields if field not in data]
        if missing:
            missing_fields_info.append(f"对象缺失字段: {', '.join(missing)}")
    return missing_fields_info


def check_yaml_data(config_data):
    # 保存错误信息
    errors = []

    # 定义每个部分的必需字段
    required_fields = {
        "env": ["uri", "user", "passwd", "pystrategy", "log_path", "stdout", "result_path", "upload_strategy", 
                "is_prompt", "is_display_progress_bar"],
        "base": ["start_date", "end_date", "frequency_type", "accounts", "commission_multiplier", "risk_free_rate"],
        "sys_risk": ["check_valid_price", "check_upperlower_price", "check_max_volume", "check_valid_cash",
                     "check_self_trade"],
        "sys_simulation": ["bar_matching_type", "tick_matching_type", "current_matching_type", "volume_limit_percent",
                           "slippage_type", "slippage"],
    }
    # 日期格式
    date_formats = [
        '%Y-%m-%d', '%Y/%m/%d', '%m-%d-%Y', '%m/%d/%Y', '%Y.%m.%d', '%m.%d.%Y', '%Y%m%d'
    ]

    # 检查是否漏以上定义的字段
    if config_data:
        for section, fields in required_fields.items():
            if section in config_data:
                missing_info = check_missing_fields(config_data[section], fields)
                if missing_info:
                    errors.extend([f"{section} 部分: {info}" for info in missing_info])
        if errors:
            # 返回错误
            return errors
    else:
        errors.extend("解析的配置json对象为空")
        return errors

    # 检查 env 部分
    env = config_data.get('env')
    if env:
        # 检查uri地址格式
        uri = env.get('uri')
        if uri and not is_valid_ws_uri(uri):
            errors.append(f"env 中的 uri {uri} 不是有效的 WebSocket 链接地址")
        # 检查策略文件后缀名
        pystrategy = env.get('pystrategy')
        if pystrategy and not is_py_file(pystrategy):
            errors.append(f"env 中的 pystrategy {pystrategy} 不以 .py 结尾")
        # 检查路径
        log_path = env.get('log_path')
        if log_path and len(log_path) == 0:
            errors.append("log_path路径为空")
        result_path = env.get('result_path')
        if result_path and len(result_path) == 0:
            errors.append("result_path路径为空")

    # 检查 base 部分
    base = config_data.get('base')
    if base:
        # 检查start_date日期格式
        start_date = base.get('start_date')
        if start_date:
            new_start_date = convert_date(start_date, date_formats)
            if new_start_date:
                base['start_date'] = new_start_date
            else:
                errors.append(f"base 中的 start_date {start_date} 格式错误且无法转换,支持日期格式{date_formats}")
        # 检查end_date日期格式
        end_date = base.get('end_date')
        if end_date:
            new_end_date = convert_date(end_date, date_formats)
            if new_end_date:
                base['end_date'] = new_end_date
            else:
                errors.append(f"base 中的 end_date {end_date} 格式错误且无法转换,支持日期格式{date_formats}")
        # 检查frequency_type类型值
        frequency_type = base.get('frequency_type')
        valid_types = ["1d", "1m", "tick"]
        if frequency_type not in valid_types:
            errors.append(f"base 中的 frequency_type {frequency_type} 不在允许的类型列表中{valid_types}")

    sys_simulation = config_data.get('sys_simulation')
    if sys_simulation:
        # 检查bar_matching_type类型值
        bar_matching_type = sys_simulation.get('bar_matching_type')
        valid_types = ["previous_open", "previous_close", "current_open", "current_close", "next_open", "next_close",
                       "best"]
        if bar_matching_type not in valid_types:
            errors.append(
                f"sys_simulation 中的 bar_matching_type {bar_matching_type} 不在允许的类型列表中{valid_types}")

        # 检查tick_matching_type类型值
        tick_matching_type = sys_simulation.get('tick_matching_type')
        valid_types = ["last", "best_own", "best_counter_party", "counter_party_offer"]
        if tick_matching_type not in valid_types:
            errors.append(
                f"sys_simulation 中的 tick_matching_type {tick_matching_type} 不在允许的类型列表中{valid_types}")

        # 检查current_matching_type类型值
        current_matching_type = sys_simulation.get('current_matching_type')
        valid_types = ["bar", "tick"]
        if current_matching_type not in valid_types:
            errors.append(
                f"sys_simulation 中的 current_matching_type {current_matching_type} 不在允许的类型列表中{valid_types}")

        # 检查slippage_type类型值
        slippage_type = sys_simulation.get('slippage_type')
        valid_types = ["price_percent", "price_tick"]
        if slippage_type not in valid_types:
            errors.append(f"sys_simulation 中的 slippage_type {slippage_type} 不在允许的类型列表中{valid_types}")

    # 检查frequency_type类型值和current_matching_type是否同时满足条件
    check_frequency_type(base, sys_simulation)

    return errors


def check_frequency_type(base, sys_simulation):
    """
    检查frequency_type类型值和bar_matching_type是否同时满足条件
    """
    # 检查frequency类型值和bar_matching_type是否同时满足条件
    frequency_type = base.get('frequency_type')
    current_matching_type = sys_simulation.get('current_matching_type')

    if frequency_type in ["1d", "1m"]:
        if current_matching_type != 'bar':
            raise Exception(f"frequency_type 为 '1d' 或 '1m' 时, {current_matching_type} 要填 'bar'")
    elif frequency_type == 'tick':
        if current_matching_type != 'tick':
            raise Exception(f"frequency_type 为 'tick' 时, {current_matching_type} 要填 'tick'")
    else:
        raise Exception(f"frequency_type 只能为 'tick', '1d', '1m'")


def run_unitrade(config):
    global gclient
    try:
        # 调用函数读取和检查YAML配置文件
        config_data = read_yaml_file(config)
        error_list = check_yaml_data(config_data)
        if error_list:
            for error in error_list:
                print(error)
        else:
            print("所有配置检查通过，数据格式正确。")
            # print(f"result:{config_data}")
            asyncio.run(run_strategy(config_data))
            gclient.wait_for_condition()
            return gclient.results
    except FileNotFoundError:
        print(f"文件 {config} 未找到。")
    except yaml.YAMLError as e:
        print(f"解析 YAML 文件时出错: {e}")
    finally:
        # 清理全局变量
        if gclient:
            gclient = None
