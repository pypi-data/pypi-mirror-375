#--*--coding=utf-8--*--
import sys, re, logging, traceback, asyncio
from os import path
import re, threading
import hashlib, base64, json
import ssl
import websockets
import time
import uuid
import datetime

try:
    from .GandanMsg import *
    from .MMAP  import *
    from .GandanCallback import *
    from .GandanSubscription import *
except Exception as e:
    from gandan.GandanMsg import *
    from gandan.MMAP  import *
    from gandan.GandanCallback import *
    from gandan.GandanSubscription import *

class Gandan:
    def __init__(self, ip_port, debug=False):
        self.ip_port = ip_port
        self.debug = debug

        self.pub_topic = {}
        self.sub_topic = {}
        self.sub_ws_topic = {}
        self.sub_topic_lock = asyncio.Lock()
        
        # 새로운 기능들
        self.callback_manager = CallbackManager()
        self.subscription_manager = SubscriptionManager()
        self.publisher_states = {}  # topic -> state
        self.subscriber_connections = {}  # topic -> list of connections

    @staticmethod
    def setup_log(path, level = logging.DEBUG):
        l_format = '%(asctime)s:%(msecs)03d^%(levelname)s^%(filename)10s^%(funcName)20s^%(lineno)04d^%(message)s'
        d_format = '%Y-%m-%d^%H:%M:%S'
        logging.basicConfig(filename=path, format=l_format, datefmt=d_format,level=level)

    @staticmethod
    def error_stack(stdout = False):
        _type, _value, _traceback = sys.exc_info()
        logging.info("#Error" + str(_type) + str(_value))
        for _err_str in traceback.format_tb(_traceback):
            if stdout == False:
                logging.info(_err_str)
            else:
                logging.info(_err_str)
                
    @staticmethod
    def version():
        return int(re.sub('\.','',sys.version.split(' ')[0][0]))

    async def ws_handler(self, websocket):
        path = websocket.request.path
        key_value = path.split("?")[1]
        (key, value) = key_value.split("=")

        if key != "topic":
            raise Exception("Invalid request path")

        # we don't receive message from websocket
        topic = value
        if topic in self.sub_ws_topic:
            if not websocket in self.sub_ws_topic[topic]:
                self.sub_ws_topic[topic].append(websocket)
        else:
            self.sub_ws_topic[topic] = [websocket]

    async def tcp_handler(self, reader, writer):
        addr = writer.get_extra_info('peername')
        connection_id = str(uuid.uuid4())
        logging.info("addr : %s, connection_id: %s" % (str(addr), connection_id))
        
        while(True):
            try:
                msg = await GandanMsg.recv_async(reader)
                if msg == None:
                    continue
                logging.info("data : %s" % str(msg))
                if msg.topic not in self.pub_topic:
                    self.pub_topic[msg.topic] = []

                if msg.pubsub == 'P':
                    try:
                        # Publisher 상태 업데이트
                        await self._handle_publisher_message(msg, connection_id)

                        if writer not in self.pub_topic[msg.topic]:
                            self.pub_topic[msg.topic].append(writer)
                        
                        async with self.sub_topic_lock:
                            remove_writers, remove_ws_writers = [], []
                            
                            # TCP Subscribers 처리
                            if msg.topic in self.sub_topic:
                                for sub_writer in self.sub_topic[msg.topic]:
                                    try:
                                        # 구독 주기 확인
                                        subscriber_id = f"tcp_{id(sub_writer)}"
                                        should_send = await self.subscription_manager.should_send_message(
                                            subscriber_id, msg.topic
                                        )
                                        
                                        if should_send:
                                            logging.info("send message to subscriber")
                                            sub_writer.write(bytes(msg))
                                            await sub_writer.drain()
                                            self.subscription_manager.message_counts[subscriber_id] += 1
                                        else:
                                            # 메시지 버퍼링 (Push 모드인 경우)
                                            await self.subscription_manager.buffer_message(subscriber_id, msg)
                                            
                                    except Exception as e:
                                        logging.info(f"writer error: {e}")
                                        remove_writers.append(sub_writer)

                            # WebSocket Subscribers 처리
                            if msg.topic in self.sub_ws_topic:
                                for ws in self.sub_ws_topic[msg.topic]:
                                    try:
                                        subscriber_id = f"ws_{id(ws)}"
                                        should_send = await self.subscription_manager.should_send_message(
                                            subscriber_id, msg.topic
                                        )
                                        
                                        if should_send:
                                            await ws.send(bytes(msg.data, "utf-8"))
                                            self.subscription_manager.message_counts[subscriber_id] += 1
                                        else:
                                            await self.subscription_manager.buffer_message(subscriber_id, msg)
                                            
                                    except Exception as e:
                                        logging.info(f"writer error: {str(e)}")
                                        remove_ws_writers.append(ws)

                            # 에러난 writer 제거
                            for w in remove_writers:
                                if w in self.sub_topic[msg.topic]:
                                    self.sub_topic[msg.topic].remove(w)
                                    # Change Number of Subscriber
                                    await self.callback_manager.update_subscriber_count(self.sub_topic[msg.topic], msg.topic, len(self.sub_topic[msg.topic]))

                            # 에러난 writer 제거
                            for w in remove_ws_writers:
                                if w in self.sub_ws_topic[msg.topic]:
                                    self.sub_ws_topic[msg.topic].remove(w)
                                    # Change Number of Subscriber
                                    await self.callback_manager.update_subscriber_count(self.sub_ws_topic[msg.topic], msg.topic, len(self.sub_ws_topic[msg.topic]))
                                    
                    except Exception as e:
                        logging.info(f"lock or pub error: {e}")
                elif msg.pubsub == 'S':
                    try:
                        logging.info("sub topic: %s" % msg.topic)
                        async with self.sub_topic_lock:
                            if msg.topic not in self.sub_topic:
                                self.sub_topic[msg.topic] = [writer]
                            else:
                                if writer not in self.sub_topic[msg.topic]:
                                    self.sub_topic[msg.topic].append(writer)
                            
                            # Subscriber 등록 및 구독 설정
                            subscriber_id = f"tcp_{id(writer)}"
                            if msg.receive_interval > 0:
                                config = SubscriptionConfig(
                                    topic=msg.topic,
                                    receive_interval=msg.receive_interval,
                                    mode=SubscriptionMode.PULL if msg.subscription_mode == "pull" else SubscriptionMode.PUSH
                                )
                                await self.subscription_manager.add_subscription(subscriber_id, config)
                            
                            # Publisher 상태 업데이트 (Subscriber 등록)
                            await self.callback_manager.update_subscriber_count(self.pub_topic[msg.topic], msg.topic, 1)
                            
                    except Exception as e:
                        logging.info(traceback.format_exc())
                        logging.info(f"lock or sub error: {e}")
            except Exception as e:
                logging.info("error : %s" % str(e))
                break

    async def _handle_publisher_message(self, msg, connection_id):
        """Publisher 메시지 처리 및 상태 관리"""
        topic = msg.topic
        
        # Publisher 상태 초기화
        if topic not in self.publisher_states:
            await self.callback_manager.update_publisher_state(topic, PublisherState.CREATED)
            await self.callback_manager.update_publisher_state(topic, PublisherState.AUTHORIZED)
            await self.callback_manager.update_publisher_state(topic, PublisherState.PUBLISHING)
            self.publisher_states[topic] = PublisherState.PUBLISHING

    # start를 asyncio 기반으로 변경
    async def start(self, certfile="cert.pem", keyfile = "key.pem"):
        async def client_connected_cb(reader, writer):
            await self.tcp_handler(reader, writer)

        async def client_connected_cb_ws(websocket):
            await self.ws_handler(websocket)
            try:
                async for message in websocket:
                    logging.info(f"클라이언트 메시지 수신: {message}")
            except Exception as e:
                logging.info(f"WebSocket 에러: {e}")
                pass

        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)

        tcp_server = await asyncio.start_server(
            client_connected_cb,
            self.ip_port[0], self.ip_port[1]
        )
        ws_server = await websockets.serve(
            client_connected_cb_ws, 
            self.ip_port[2], 
            self.ip_port[3], ssl = ssl_ctx
        )
        async with tcp_server, ws_server:
            logging.info("------------ MW Gandan Version[%d] Start --------------" % Gandan.version())
            tcp_task = asyncio.create_task(tcp_server.serve_forever())
            ws_task = asyncio.create_task(ws_server.serve_forever())
            try:
                await asyncio.gather(tcp_task, ws_task)
                #await ws_server.serve_forever()
            except Exception as e:
                logging.info(str(e))
            finally:
                tcp_task.cancel()
                ws_task.cancel()
                pass

    # 새로운 API 메서드들
    async def register_publisher_callback(self, topic: str, callback: Callable):
        """Publisher 콜백 등록"""
        await self.callback_manager.register_callback(topic, callback)
    
    async def get_publisher_state(self, topic: str):
        """Publisher 상태 조회"""
        return self.callback_manager.get_publisher_state(topic)
    
    async def get_subscription_stats(self, subscriber_id: str):
        """구독 통계 조회"""
        return self.subscription_manager.get_subscription_stats(subscriber_id)

if __name__ == "__main__":
    try:
        l_ip_port = ("0.0.0.0", 59500, "0.0.0.0", 59501)
        mw = Gandan(l_ip_port)
        Gandan.setup_log(datetime.datetime.now().strftime("/tmp/%Y%m%d")+".Gandan.log")
        asyncio.run(mw.start())
    except Exception as e:
        logging.error("Error in Gandan", e)