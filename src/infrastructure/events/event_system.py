
"""
事件系統實現
實現觀察者模式用於事件處理
"""
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Type, Callable
from ...domain.events.crawl_events import DomainEvent


class EventHandler(ABC):
    """事件處理器抽象基礎類別"""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """處理事件"""
        pass


class ConsoleEventHandler(EventHandler):
    """控制台事件處理器"""
    
    async def handle(self, event: DomainEvent) -> None:
        """輸出事件到控制台"""
        event_name = event.__class__.__name__
        timestamp = event.occurred_at.strftime("%Y-%m-%d %H:%M:%S")
        
        if hasattr(event, 'issue_id'):
            print(f"[{timestamp}] {event_name}: Issue {event.issue_id}")
        elif hasattr(event, 'session_id'):
            print(f"[{timestamp}] {event_name}: Session {event.session_id}")
        else:
            print(f"[{timestamp}] {event_name}")


class LoggingEventHandler(EventHandler):
    """日誌事件處理器"""
    
    def __init__(self, logger=None):
        import logging
        self._logger = logger or logging.getLogger(__name__)
    
    async def handle(self, event: DomainEvent) -> None:
        """記錄事件到日誌"""
        event_name = event.__class__.__name__
        
        if hasattr(event, 'issue_id'):
            if 'Failed' in event_name:
                self._logger.error(f"{event_name}: Issue {event.issue_id}")
            else:
                self._logger.info(f"{event_name}: Issue {event.issue_id}")
        elif hasattr(event, 'session_id'):
            self._logger.info(f"{event_name}: Session {event.session_id}")
        else:
            self._logger.info(event_name)


class StatisticsEventHandler(EventHandler):
    """統計事件處理器"""
    
    def __init__(self):
        self._statistics = {
            'issues_processed': 0,
            'issues_successful': 0,
            'issues_failed': 0,
            'attachments_downloaded': 0,
            'pdfs_generated': 0,
            'sessions_started': 0,
            'sessions_completed': 0
        }
    
    async def handle(self, event: DomainEvent) -> None:
        """更新統計資料"""
        event_name = event.__class__.__name__
        
        if event_name == 'IssueProcessingStarted':
            self._statistics['issues_processed'] += 1
        elif event_name == 'IssueProcessingCompleted':
            if hasattr(event, 'success') and event.success:
                self._statistics['issues_successful'] += 1
        elif event_name == 'IssueProcessingFailed':
            self._statistics['issues_failed'] += 1
        elif event_name == 'AttachmentDownloadCompleted':
            self._statistics['attachments_downloaded'] += 1
        elif event_name == 'PdfGenerationCompleted':
            self._statistics['pdfs_generated'] += 1
        elif event_name == 'CrawlSessionStarted':
            self._statistics['sessions_started'] += 1
        elif event_name == 'CrawlSessionCompleted':
            self._statistics['sessions_completed'] += 1
    
    def get_statistics(self) -> Dict[str, int]:
        """取得統計資料"""
        return self._statistics.copy()
    
    def reset_statistics(self) -> None:
        """重置統計資料"""
        for key in self._statistics:
            self._statistics[key] = 0


class EventBus:
    """事件匯流排 - 實現觀察者模式的核心"""
    
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []
    
    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """訂閱特定類型的事件"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def subscribe_all(self, handler: EventHandler) -> None:
        """訂閱所有事件"""
        self._global_handlers.append(handler)
    
    def unsubscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """取消訂閱特定事件"""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    def unsubscribe_all(self, handler: EventHandler) -> None:
        """取消訂閱所有事件"""
        try:
            self._global_handlers.remove(handler)
        except ValueError:
            pass
    
    async def publish(self, event: DomainEvent) -> None:
        """發布事件"""
        # 處理特定類型的處理器
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    await handler.handle(event)
                except Exception as e:
                    print(f"事件處理器錯誤: {e}")
        
        # 處理全域處理器
        for handler in self._global_handlers:
            try:
                await handler.handle(event)
            except Exception as e:
                print(f"全域事件處理器錯誤: {e}")
    
    def clear(self) -> None:
        """清除所有處理器"""
        self._handlers.clear()
        self._global_handlers.clear()


class EventHandlerWrapper:
    """事件處理器包裝器 - 用於同步處理器"""
    
    def __init__(self, sync_handler: Callable[[DomainEvent], None]):
        self._sync_handler = sync_handler
    
    async def handle(self, event: DomainEvent) -> None:
        """包裝同步處理器為非同步"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._sync_handler, event)


# 全域事件匯流排實例
event_bus = EventBus()
