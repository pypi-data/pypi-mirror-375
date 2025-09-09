#--*--coding:utf-8--*--
import struct, logging, traceback
import json
from typing import Optional, Dict, Any

class GandanMsg:
    def __init__(self, pubsub, topic, data, receive_interval: float = 0.0, 
                 subscription_mode: str = "pull", metadata: Optional[Dict[str, Any]] = None):
        if pubsub == 'PUB' or pubsub == 'P':
            self.pubsub = 'P'
        elif pubsub == 'SUB' or pubsub == 'S':
            self.pubsub = 'S'
        else:
            raise Exception('pubsub')
        self.topic_size = len(bytes(topic, "utf-8"))
        self.data_size = len(bytes(data,"utf-8"))
        (self.topic, self.data) = (topic, data)
        self.receive_interval_size = len(bytes(str(receive_interval), "utf-8"))
        self.subscription_mode_size = len(bytes(subscription_mode, "utf-8"))
        self.metadata_size = len(bytes(json.dumps(metadata), "utf-8"))
        # 새로운 필드들
        self.receive_interval = receive_interval
        self.subscription_mode = subscription_mode
        self.metadata = metadata or {}
        
        # 크기 계산
        self.receive_interval_size = 4  # float은 4바이트
        self.subscription_mode_size = len(bytes(subscription_mode, "utf-8"))
        self.metadata_json = json.dumps(self.metadata)
        self.metadata_size = len(bytes(self.metadata_json, "utf-8"))
        
        self.total_size = 0
        self.total_size = len(bytes(self))
        self.protocol_type = "tcp"

    def __bytes__(self):
        _b = bytes(self.pubsub, "utf-8")
        _b += struct.pack("!i", self.total_size)
        _b += struct.pack("!i", self.topic_size)
        _b += struct.pack("!i", self.data_size)
        _b += struct.pack("!i", self.receive_interval_size)
        _b += struct.pack("!i", self.subscription_mode_size)
        _b += struct.pack("!i", self.metadata_size)

        _b += bytes(self.topic, "utf-8")
        _b += bytes(self.data, "utf-8")
        _b += struct.pack("!f", self.receive_interval)
        _b += bytes(self.subscription_mode, "utf-8")
        _b += bytes(self.metadata_json, "utf-8")
        
        return _b
    
    def __str__(self):
        return self.topic+":"+self.data

    @staticmethod
    async def recv_async(reader):
        """
        비동기 버전: reader는 asyncio.StreamReader 등 비동기 reader 객체여야 하며, read(n) 메서드를 비동기적으로 호출해야 합니다.
        """
        pubsub_byte = await reader.read(65535)
        if len(pubsub_byte) == 0:
            raise Exception("conn")

        try:
            logging.info("pubsub_byte: %s" % pubsub_byte)
            if pubsub_byte[0:1] != b'P' and pubsub_byte[0:1] != b'S':
                raise Exception("pubsub type error")
            logging.info("###### Message ######")
            (total_size, topic_size, data_size
            , receive_interval_size, subscription_mode_size
            , metadata_size) = struct.unpack("!iiiiii", pubsub_byte[1:25])
            logging.info("# total_size: %d" % total_size)
            logging.info("# topic_size: %d" % topic_size)
            logging.info("# data_size: %d" % data_size)
            logging.info("# receive_interval_size: %d" % receive_interval_size)
            logging.info("# subscription_mode_size: %d" % subscription_mode_size)
            logging.info("# metadata_size: %d" % metadata_size)

            offset = 25
            topic = str(pubsub_byte[offset:offset+topic_size], "utf-8")
            offset += topic_size
            data = str(pubsub_byte[offset:offset+data_size], "utf-8")
            offset += data_size
            receive_interval = struct.unpack("!f", pubsub_byte[offset:offset+receive_interval_size])[0]
            offset += receive_interval_size
            subscription_mode = str(pubsub_byte[offset:offset+subscription_mode_size], "utf-8")
            offset += subscription_mode_size
            metadata = json.loads(str(pubsub_byte[offset:offset+metadata_size], "utf-8"))

            logging.info("# data: %s..." % data[0:10])
            logging.info("####################")
        except Exception as e:
            logging.error(traceback.format_exc())
            raise Exception('convert pubsub_byte')
        
        return GandanMsg(str(pubsub_byte[0:1], "utf-8"), topic, data, 
                        receive_interval, subscription_mode, metadata)

    @staticmethod
    def recv_sync(sock):
        """
        동기 버전: reader는 socket 등 file-like 객체여야 하며, read(n) 메서드를 동기적으로 호출해야 합니다.
        """
        pubsub_byte = sock.recv(65535)
        if len(pubsub_byte) == 0:
            raise Exception("timed out")

        try:
            logging.info("pubsub_byte: %s" % pubsub_byte)
            if pubsub_byte[0:1] != b'P' and pubsub_byte[0:1] != b'S':
                raise Exception("pubsub type error")
            logging.info("###### Message ######")
            (total_size, topic_size, data_size
            , receive_interval_size, subscription_mode_size
            , metadata_size) = struct.unpack("!iiiiii", pubsub_byte[1:25])
            logging.info("# total_size: %d" % total_size)
            logging.info("# topic_size: %d" % topic_size)
            logging.info("# data_size: %d" % data_size)
            logging.info("# receive_interval_size: %d" % receive_interval_size)
            logging.info("# subscription_mode_size: %d" % subscription_mode_size)
            logging.info("# metadata_size: %d" % metadata_size)

            offset = 25
            topic = str(pubsub_byte[offset:offset+topic_size], "utf-8")
            offset += topic_size
            data = str(pubsub_byte[offset:offset+data_size], "utf-8")
            offset += data_size
            receive_interval = struct.unpack("!f", pubsub_byte[offset:offset+receive_interval_size])[0]
            offset += receive_interval_size
            subscription_mode = str(pubsub_byte[offset:offset+subscription_mode_size], "utf-8")
            offset += subscription_mode_size
            metadata = json.loads(str(pubsub_byte[offset:offset+metadata_size], "utf-8"))

            logging.info("# data: %s..." % data[0:10])
            logging.info("####################")
        except Exception as e:
            logging.error(traceback.format_exc())
            raise Exception('convert pubsub_byte')
        
        return GandanMsg(str(pubsub_byte[0:1], "utf-8"), topic, data, 
                        receive_interval, subscription_mode, metadata)