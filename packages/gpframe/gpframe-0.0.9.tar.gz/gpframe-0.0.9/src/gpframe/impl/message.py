
from abc import ABC, abstractmethod
from enum import Enum
import threading
from typing import Any, Callable, TypeVar, cast, overload
from multiprocessing.managers import DictProxy

T = TypeVar("T")

class _NO_DEFAULT(Enum):
    _ = "dummy member"

class MessageUpdater(ABC):
    __slots__ = ()
    @abstractmethod
    def get(self, key: Any) -> Any:
        ...
    @abstractmethod
    def getwd(self, key: Any, default: T) -> T:
        ...
    @abstractmethod
    def getwt(self, key: Any, typ: type[T]) -> T:
        ...
    @abstractmethod
    def update(self, key: Any, value: T) -> T:
        ...
    @abstractmethod
    def apply(self, key: Any, fn: Callable[[T], T], default: T | type[_NO_DEFAULT] = _NO_DEFAULT) -> T:
        ...
    @abstractmethod
    def remove(self, key: Any, default: T | None = None) -> T | None:
        ...

class MessageReader(ABC):
    __slots__ = ()
    @abstractmethod
    def get(self, key: Any) -> Any:
        ...
    @abstractmethod
    def getwd(self, key: Any, default: T) -> T:
        ...
    @abstractmethod
    def getwt(self, key: Any, typ: type[T]) -> T:
        ...


class MessageRegistry:
    __slots__ = ("_usage_state_checker", "_lock", "_map", "_updater", "_reader")
    def __init__(
            self,
            lock: threading.Lock,
            map_: dict | DictProxy,
            usage_state_checker: Callable[[], None] | None = None
        ):
        self._usage_state_checker = usage_state_checker if usage_state_checker else lambda: None
        self._lock = lock
        self._map = map_
        self._updater = self._create_updater()
        self._reader = self._create_reader()
    
    def _extract_checking_type(self, default: T | type[_NO_DEFAULT] = _NO_DEFAULT, typ: type[T] | None = None) -> type[T]:
        dtype = type(cast(T, default)) if default is not _NO_DEFAULT else None
        if dtype:
            if typ is not None and not issubclass(typ, dtype):
                raise TypeError(f"type mismatch: expected {dtype} (from default={default!r}), got {typ}")
            return dtype
        else:
            if typ is None:
                raise ValueError("no type information available")
            return typ
    
    def _get_unsafe(self, key: Any, default: T | type[_NO_DEFAULT] = _NO_DEFAULT, typ: type[T] | None = None) -> T:
        if self._map is not None:
            checking_type = self._extract_checking_type(default, typ)
            if key in self._map:
                value = self._map[key]
            else:
                if default is _NO_DEFAULT:
                    raise KeyError
                value = default
            if not isinstance(value, checking_type):
                raise TypeError
            return value
        else:
            raise RuntimeError
    
    def get(self, key) -> Any:
        self._usage_state_checker()
        with self._lock:
            if self._map is not None:
                return self._map[key]
            else:
                raise RuntimeError
    
    def getwd(self, key: Any, default: T) -> T:
        self._usage_state_checker()
        with self._lock:
            return self._get_unsafe(key, default)
    
    def getwt(self, key: Any, typ: type[T]) -> T:
        self._usage_state_checker()
        with self._lock:
            return self._get_unsafe(key, typ = typ)
    
    def update(self, key: Any, value: T) -> T:
        self._usage_state_checker()
        with self._lock:
            if self._map is not None:
                self._map[key] = value
                return value
            else:
                raise RuntimeError
    
    def apply(self, key: Any, fn: Callable[[T], T], default: T | type[_NO_DEFAULT] = _NO_DEFAULT) -> T:
        self._usage_state_checker()
        with self._lock:
            if self._map is not None:
                value = self._get_unsafe(key, default)
                applied_value = fn(value)
                self._map[key] = applied_value
                return applied_value
            else:
                raise RuntimeError
    
    def remove(self, key: Any, default: T | None = None) -> T | None:
        self._usage_state_checker()
        with self._lock:
            if self._map is not None:
                return self._map.pop(key, default)
            else:
                raise RuntimeError
    
    def __str__(self):
        self._usage_state_checker()
        with self._lock:
            if self._map is not None:
                return str(self._map)
            else:
                return "!!MessageRegistry is cleanuped."

    def _create_updater(self):
        outer = self
        class _Updater(MessageUpdater):
            __slots__ = ()
            def get(self, key: Any) -> Any:
                return outer.get(key)
            def getwd(self, key: Any, default: T) -> T:
                return outer.getwd(key, default)
            def getwt(self, key: Any, typ: type[T]) -> T:
                return outer.getwt(key, typ)
            def update(self, key: Any, value: T) -> T:
                return outer.update(key, value)
            def apply(self, key: Any, fn: Callable[[T], T], default: T | type[_NO_DEFAULT] = _NO_DEFAULT) -> T:
                return outer.apply(key, fn, default)
            def remove(self, key: Any, default: T | None = None) -> T | None:
                return outer.remove(key, default)
            def __str__(self):
                return outer.__str__()
            def __reduce__(self):
                outer._usage_state_checker()
                with outer._lock:
                    if outer._map is not None:
                        return (_create_message_updater, (outer._lock, outer._map))
                    else:
                        raise RuntimeError("map is cleared")
        return _Updater()

    def _create_reader(self):
        outer = self
        class _Reader(MessageReader):
            __slots__ = ()
            def get(self, key: Any) -> Any:
                return outer.get(key)
            def getwd(self, key: Any, default: T) -> T:
                return outer.getwd(key, default)
            def getwt(self, key: Any, typ: type[T]) -> T:
                return outer.getwt(key, typ)
            def __str__(self):
                return outer.__str__()
            
            def __reduce__(self):
                outer._usage_state_checker()
                with outer._lock:
                    if outer._map is not None:
                        return (_create_message_reader, (outer._lock, outer._map))
                    else:
                        raise RuntimeError("map is cleared")

        return _Reader()
    
    @property
    def updater(self):
        return self._updater
    
    @property
    def reader(self):
        return self._reader
    
    def copy_map_without_usage_state_check(self) -> dict:
        with self._lock:
            if self._map is not None:
                return dict(self._map)
            else:
                raise RuntimeError("map is cleared")
    
    def clear_map_unsafe(self) -> None:
        if self._map is not None:
            self._map.clear()
            self._map = None
    
    def __reduce__(self):
        return (MessageRegistry, (self._lock, self._map))


def _create_message_updater(
        lock_: threading.Lock,
        map_: dict | DictProxy
) -> MessageUpdater:
    return MessageRegistry(lock_, map_).updater

def _create_message_reader(
        lock_: threading.Lock,
        map_: dict | DictProxy
) -> MessageReader:    
    return MessageRegistry(lock_, map_).reader

