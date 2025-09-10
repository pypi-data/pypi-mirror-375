from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from logging import Logger
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from ..impl.syncm import SynchronizedMapReader, SynchronizedMapUpdater

class Frame(ABC):
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
    def request(self) -> SynchronizedMapUpdater:
        ...
    @property
    @abstractmethod
    def event_message(self) -> SynchronizedMapReader:
        ...
    @property
    @abstractmethod
    def routine_message(self) -> SynchronizedMapReader:
        ...
    
    @abstractmethod
    def request_stop_routine(self, *, kill: bool = False) -> None:
        ...
        
    @property
    @abstractmethod
    def task(self) -> asyncio.Task:
        ...

