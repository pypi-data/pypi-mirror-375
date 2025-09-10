from asyncio import Event
from typing import TypeVar

T = TypeVar('T') 

class AsyncWaitableEvents(Event):
    def __init__(self) -> None:
        super().__init__()
        self.result:T = None
    
    def set(self, value:T) -> None:
        self.result = value

        return super().set()
    
    async def wait(self, timeout: float | None = None) -> tuple[bool, T]:
        return await super().wait(timeout), self.result