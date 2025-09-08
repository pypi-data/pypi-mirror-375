from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel
from pyee import EventEmitter
from pyee.base import Handler

from logis.ctx import Context

T = TypeVar("T")


class EventContext(BaseModel, Generic[T]):
    # 事件所携带的数据
    payload: T | None = None
    # 事件源ID
    source_id: str | None = None
    # 事件目标ID
    target_id: Optional[Any] = None
    # 事件名称
    name: str
    # 附加数据
    extra: Any = None


class EventBus(Context):
    """
    事件总线，支持监听、发出事件
    """

    emitter = EventEmitter()

    @classmethod
    def get_event_emitter(cls) -> EventEmitter:
        return cls.emitter

    @classmethod
    def emit(cls, event_name: str, *args, **kwargs):
        cls.get_event_emitter().emit(event_name, *args, **kwargs)

    @classmethod
    def on(cls, event_name: str, func: Handler):
        cls.get_event_emitter().on(event_name, func)

    @classmethod
    def add_listener(cls, event_name: str, listener: Handler):
        cls.get_event_emitter().add_listener(event_name, listener)
