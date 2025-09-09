#--*--coding:utf-8--*--
import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Callable, Optional, Any
from enum import Enum
import traceback

class PublisherState(Enum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    PUBLISHING = "publishing"
    FIRST_SUBSCRIBER = "first_subscriber"
    LAST_SUBSCRIBER = "last_subscriber"
    STOPPED = "stopped"

class CallbackEvent:
    def __init__(self, event_type: str, topic: str, timestamp: Optional[float] = None, 
                 subscriber_count: int = 0, payload: Optional[Dict[str, Any]] = None):
        self.event_type = event_type
        self.topic = topic
        self.timestamp = timestamp or time.time()
        self.subscriber_count = subscriber_count
        self.payload = payload or {}
        
    def to_dict(self):
        return {
            'event_type': self.event_type,
            'topic': self.topic,
            'timestamp': self.timestamp,
            'subscriber_count': self.subscriber_count,
            'payload': self.payload
        }
    
    def to_json(self):
        return json.dumps(self.to_dict())

class CallbackManager:
    def __init__(self):
        self.callbacks: Dict[str, List[Callable]] = {}
        self.publisher_states: Dict[str, PublisherState] = {}
        self.subscriber_counts: Dict[str, int] = {}
        self.callback_lock = asyncio.Lock()
        
    async def register_callback(self, topic: str, callback: Callable):
        """Publisher 콜백 등록"""
        async with self.callback_lock:
            if topic not in self.callbacks:
                self.callbacks[topic] = []
            self.callbacks[topic].append(callback)
            logging.info(f"Callback registered for topic: {topic}")
    
    async def unregister_callback(self, topic: str, callback: Callable):
        """Publisher 콜백 해제"""
        async with self.callback_lock:
            if topic in self.callbacks and callback in self.callbacks[topic]:
                self.callbacks[topic].remove(callback)
                logging.info(f"Callback unregistered for topic: {topic}")
    
    async def trigger_callback(self, topic: str, event: CallbackEvent):
        """콜백 이벤트 발생"""
        async with self.callback_lock:
            if topic in self.callbacks:
                for callback in self.callbacks[topic]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            callback(event)
                    except Exception as e:
                        logging.error(f"Callback error for topic {topic}: {e}")
    
    async def update_publisher_state(self, writers : List[Any], topic: str, new_state: PublisherState, 
                                   subscriber_count: int = 0):
        """Publisher 상태 업데이트 및 콜백 발생"""
        old_state = self.publisher_states.get(topic, None)
        old_count = self.subscriber_counts.get(topic, 0)
        self.publisher_states[topic] = new_state
        self.subscriber_counts[topic] = subscriber_count
        
        # 상태 변화에 따른 콜백 이벤트 생성
        event_type = f"state_{new_state.value}"
        
        # 특별한 상태 변화 감지
        if new_state == PublisherState.FIRST_SUBSCRIBER and old_state != PublisherState.FIRST_SUBSCRIBER:
            event_type = "first_subscriber_registered"
            logging.info(f"### First subscriber registered: {topic}")
        elif new_state == PublisherState.LAST_SUBSCRIBER and old_state != PublisherState.LAST_SUBSCRIBER:
            event_type = "last_subscriber_unregistered"
            logging.info(f"###Last subscriber unregistered: {topic}")
        
        event = CallbackEvent(
            event_type=event_type,
            topic=topic,
            subscriber_count=subscriber_count,
            payload={
                'old_state': old_state.value if old_state else None,
                'new_state': new_state.value,
                'state_change': True
            }
        )
        
        await self.trigger_callback(topic, event)
        logging.info(f"Publisher state updated: {topic} -> {new_state.value} (subscribers: {subscriber_count})")
    
    async def update_subscriber_count(self, writers : List[Any], topic: str, delta: int):
        """Subscriber 수 변화 업데이트"""
        try:
            current_count = self.subscriber_counts.get(topic, 0)
            new_count = max(0, current_count + delta)

            # 상태 결정
            if new_count == 0:
                if current_count > 0:  # 1->0 변화
                    await self.update_publisher_state(writers, topic, PublisherState.LAST_SUBSCRIBER, 0)
                    logging.info(f"###Last subscriber unregistered: {topic}")
                else:
                    await self.update_publisher_state(writers, topic, PublisherState.PUBLISHING, 0)
                    logging.info(f"###Publisher publishing: {topic}")
            elif new_count == 1 and current_count == 0:  # 0->1 변화
                await self.update_publisher_state(writers, topic, PublisherState.FIRST_SUBSCRIBER, 1)
                logging.info(f"###First subscriber registered: {topic}")
            else:
                await self.update_publisher_state(writers, topic, PublisherState.PUBLISHING, new_count)
                logging.info(f"###Publisher publishing: {topic}")
        except Exception as e:
            logging.info(traceback.format_exc())
            logging.info(f"###Error update_subscriber_count: {e}")
    
    def get_publisher_state(self, topic: str) -> Optional[PublisherState]:
        """현재 Publisher 상태 조회"""
        return self.publisher_states.get(topic)
    
    def get_subscriber_count(self, topic: str) -> int:
        """현재 Subscriber 수 조회"""
        return self.subscriber_counts.get(topic, 0)
