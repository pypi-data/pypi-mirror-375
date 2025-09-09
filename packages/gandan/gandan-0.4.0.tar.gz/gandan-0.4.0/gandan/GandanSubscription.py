#--*--coding:utf-8--*--
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class SubscriptionMode(Enum):
    PULL = "pull"
    PUSH = "push"

@dataclass
class SubscriptionConfig:
    topic: str
    receive_interval: float  # 초 단위
    mode: SubscriptionMode = SubscriptionMode.PULL
    buffer_size: int = 1000
    drop_old_messages: bool = True

class SubscriptionManager:
    def __init__(self):
        self.subscriptions: Dict[str, List[SubscriptionConfig]] = {}
        self.subscriber_buffers: Dict[str, List[Any]] = {}
        self.last_send_times: Dict[str, float] = {}
        self.message_counts: Dict[str, int] = {}
        self.dropped_counts: Dict[str, int] = {}
        self.subscription_lock = asyncio.Lock()
        
    async def add_subscription(self, subscriber_id: str, config: SubscriptionConfig):
        """새로운 구독 추가"""
        async with self.subscription_lock:
            if subscriber_id not in self.subscriptions:
                self.subscriptions[subscriber_id] = []
                self.subscriber_buffers[subscriber_id] = []
                self.last_send_times[subscriber_id] = 0
                self.message_counts[subscriber_id] = 0
                self.dropped_counts[subscriber_id] = 0
            
            self.subscriptions[subscriber_id].append(config)
            logging.info(f"Subscription added: {subscriber_id} -> {config.topic} (interval: {config.receive_interval}s)")
    
    async def remove_subscription(self, subscriber_id: str, topic: str):
        """구독 제거"""
        async with self.subscription_lock:
            if subscriber_id in self.subscriptions:
                self.subscriptions[subscriber_id] = [
                    sub for sub in self.subscriptions[subscriber_id] 
                    if sub.topic != topic
                ]
                if not self.subscriptions[subscriber_id]:
                    del self.subscriptions[subscriber_id]
                    del self.subscriber_buffers[subscriber_id]
                    del self.last_send_times[subscriber_id]
                    del self.message_counts[subscriber_id]
                    del self.dropped_counts[subscriber_id]
                logging.info(f"Subscription removed: {subscriber_id} -> {topic}")
    
    async def should_send_message(self, subscriber_id: str, topic: str) -> bool:
        """메시지 전송 여부 결정 (주기 기반)"""
        if subscriber_id not in self.subscriptions:
            return True  # 기본값: 즉시 전송
        
        current_time = time.time()
        last_send = self.last_send_times.get(subscriber_id, 0)
        
        # 해당 topic의 구독 설정 찾기
        for config in self.subscriptions[subscriber_id]:
            if config.topic == topic:
                if current_time - last_send >= config.receive_interval:
                    self.last_send_times[subscriber_id] = current_time
                    return True
                else:
                    # 주기 미만이면 메시지 Drop
                    self.dropped_counts[subscriber_id] += 1
                    return False
        
        return True  # 해당 topic에 대한 구독이 없으면 즉시 전송
    
    async def buffer_message(self, subscriber_id: str, message: Any):
        """메시지 버퍼링 (Push 모드용)"""
        if subscriber_id not in self.subscriber_buffers:
            return
        
        buffer = self.subscriber_buffers[subscriber_id]
        buffer.append({
            'message': message,
            'timestamp': time.time()
        })
        
        # 버퍼 크기 제한
        max_buffer_size = 1000  # 기본값
        if subscriber_id in self.subscriptions and self.subscriptions[subscriber_id]:
            max_buffer_size = self.subscriptions[subscriber_id][0].buffer_size
        
        if len(buffer) > max_buffer_size:
            if self.subscriptions[subscriber_id][0].drop_old_messages:
                buffer.pop(0)  # 가장 오래된 메시지 제거
            else:
                buffer.pop()  # 가장 최신 메시지 제거
    
    async def get_buffered_messages(self, subscriber_id: str) -> List[Any]:
        """버퍼된 메시지 조회"""
        if subscriber_id not in self.subscriber_buffers:
            return []
        
        messages = self.subscriber_buffers[subscriber_id].copy()
        self.subscriber_buffers[subscriber_id].clear()
        return messages
    
    async def update_subscription_config(self, subscriber_id: str, topic: str, 
                                       new_config: SubscriptionConfig):
        """구독 설정 업데이트"""
        async with self.subscription_lock:
            if subscriber_id in self.subscriptions:
                for i, config in enumerate(self.subscriptions[subscriber_id]):
                    if config.topic == topic:
                        self.subscriptions[subscriber_id][i] = new_config
                        logging.info(f"Subscription config updated: {subscriber_id} -> {topic}")
                        break
    
    def get_subscription_stats(self, subscriber_id: str) -> Dict[str, Any]:
        """구독 통계 조회"""
        return {
            'message_count': self.message_counts.get(subscriber_id, 0),
            'dropped_count': self.dropped_counts.get(subscriber_id, 0),
            'buffer_size': len(self.subscriber_buffers.get(subscriber_id, [])),
            'last_send_time': self.last_send_times.get(subscriber_id, 0)
        }
