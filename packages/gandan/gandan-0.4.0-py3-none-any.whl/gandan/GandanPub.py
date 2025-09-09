#--*--encoding:utf-8--*--
import struct, sys, time, logging, traceback
import socket
import re
import asyncio
from typing import Callable, Optional
try:
	from .GandanMsg import *
	from .GandanCallback import *
except Exception as e:
	from gandan.GandanMsg import *
	from gandan.GandanCallback import *

class GandanPub:
	def __init__(self, topic = "TEST", ip = '127.0.0.1', port = 59500, 
	             callback_url: Optional[str] = None):
		self.ip_port = (ip, port)
		self.topic = topic
		self.callback_url = callback_url
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect(self.ip_port)
		self.is_publishing = False
		self.subscriber_count = 0

	def pub_sync(self, data, metadata: Optional[dict] = None):
		try:
			msg = GandanMsg('P', self.topic, data, metadata=metadata)
			self.sock.send(bytes(msg))
			self.is_publishing = True
		except Exception as e:
			logging.info(f"error: {e}")
			raise Exception("connection lost")

	def pub_async(self, data, metadata: Optional[dict] = None):
		"""비동기 Publish (콜백 지원)"""
		try:
			msg = GandanMsg('P', self.topic, data, metadata=metadata)
			self.sock.send(bytes(msg))
			self.is_publishing = True
			return True
		except Exception as e:
			logging.info(f"error: {e}")
			raise Exception("connection lost")

	def set_callback(self, callback: Callable):
		"""Publisher 콜백 설정"""
		self.callback = callback

	def get_publishing_status(self) -> bool:
		"""Publishing 상태 조회"""
		return self.is_publishing

	def get_subscriber_count(self) -> int:
		"""현재 Subscriber 수 조회"""
		return self.subscriber_count

	def close(self):
		self.sock.close()
		self.is_publishing = False