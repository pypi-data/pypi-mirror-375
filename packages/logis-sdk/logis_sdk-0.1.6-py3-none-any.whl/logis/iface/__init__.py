from abc import ABCMeta
from typing import Protocol, runtime_checkable


@runtime_checkable
class Shape(Protocol):
    """
    形状，例如路径、节点等
    """

    pass


@runtime_checkable
class Producer(Protocol):
    """
    生产者
    """

    def produce(self, *args, **kwargs):
        pass


@runtime_checkable
class Consumer(Protocol):
    """
    消费者
    """

    def consume(self, *args, **kwargs):
        pass


class StoreResult(metaclass=ABCMeta):
    """
    存储结果
    """

    pass


class RetrieveResult(metaclass=ABCMeta):
    """
    检索结果
    """

    pass


class StoreStrategy(metaclass=ABCMeta):
    """
    存储策略
    """


@runtime_checkable
class Storable(Protocol):
    # class Storable(metaclass=ABCMeta):
    """
    可存储的

    使用鸭子类型实现，相比ABC更灵活
    """

    def store(self, *args, **kwargs) -> StoreResult:
        pass

    def retrieve(self, *args, **kwargs) -> RetrieveResult:
        pass
