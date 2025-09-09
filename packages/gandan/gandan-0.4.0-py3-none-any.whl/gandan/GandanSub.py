import struct, sys, time, logging, traceback
import socket
import re
import asyncio
from typing import Callable, Optional
try:
	from .GandanMsg import *
	from .GandanSubscription import *
except Exception as e:
	from gandan.GandanMsg import *
	from gandan.GandanSubscription import *
class GandanSub:
	def __init__(self, topic = "TEST", ip = '127.0.0.1', port = 59500, 
	             timeout = 1, receive_interval: float = 0.0, 
	             subscription_mode: str = "pull"):
		self.ip_port = (ip, port)
		self.topic = topic
		self.receive_interval = receive_interval
		self.subscription_mode = subscription_mode
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if timeout == 0:
			self.sock.setblocking(True)
		else:
			self.sock.settimeout(timeout)
		self.sock.connect(self.ip_port)
		
		# 구독 설정과 함께 메시지 전송
		msg = GandanMsg('S', self.topic, '', receive_interval, subscription_mode)
		self.sock.send(bytes(msg))

	def sub_sync(self, cb):
		try:
			msg = GandanMsg.recv_sync(self.sock)
			try:
				cb(msg.topic, msg.data, msg.metadata)
			except Exception as e:
				logging.info(f"callback error: {e}")
		except Exception as e:
			# logging.error(f"error: {e}")
			if str(e) == 'timed out':
				return None
			else:
			    raise Exception("connection lost")

	def sub_async(self, cb):
		"""비동기 구독 (주기 기반)"""
		async def _async_sub():
			while True:
				try:
					msg = GandanMsg.recv_sync(self.sock)
					if msg:
						await cb(msg.topic, msg.data, msg.metadata)
					
					# 주기 기반 대기
					if self.receive_interval > 0:
						await asyncio.sleep(self.receive_interval)
						
				except Exception as e:
					if str(e) == 'timed out':
						continue
					else:
						logging.error(f"Subscription error: {e}")
						break
		
		return asyncio.create_task(_async_sub())

	def update_receive_interval(self, new_interval: float):
		"""수신 주기 업데이트"""
		self.receive_interval = new_interval
		# 서버에 새로운 설정 전송
		msg = GandanMsg('S', self.topic, '', new_interval, self.subscription_mode)
		self.sock.send(bytes(msg))

	def get_subscription_config(self) -> dict:
		"""현재 구독 설정 조회"""
		return {
			'topic': self.topic,
			'receive_interval': self.receive_interval,
			'subscription_mode': self.subscription_mode
		}

	def close(self):
		self.sock.close()