from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

R = TypeVar("R")

if TYPE_CHECKING:
    from logging import Logger

    from ..impl.routine.result import RoutineResult
    from ..impl.syncm import SynchronizedMapReader, SynchronizedMapUpdater


class EventContext(ABC, Generic[R]):
    __slots__ = ()
    @property
    @abstractmethod
    def frame_name(self) -> str:
        ...
    @property
    @abstractmethod
    def logger(self) -> Logger:
        ...
    @property
    @abstractmethod
    def routine_in_subprocess(self) -> bool:
        ...
    @property
    @abstractmethod
    def environment(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def request(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def event_message(self) -> SynchronizedMapUpdater:
        ...
    @property
    @abstractmethod
    def routine_message(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def routine_result(self) -> RoutineResult[R]:
        ...

class RoutineContext(ABC):
    __slots__ = ()
    @property
    @abstractmethod
    def frame_name(self) -> str:
        ...
    @property
    @abstractmethod
    def logger_name(self) -> str:
        ...
    @property
    @abstractmethod
    def routine_in_subprocess(self) -> bool:
        ...
    @property
    @abstractmethod
    def environment(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def request(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def event_message(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def routine_message(self) -> SynchronizedMapUpdater:
        ...
