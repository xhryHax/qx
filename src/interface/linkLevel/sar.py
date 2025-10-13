
import socket
import asyncio
from threading import Thread, current_thread
from collections import deque
from typing import Callable

from interface.systemPrint import systemPrintInfo
from . import external
from . import change
from ..echoLevel.request import Request
from ..echoLevel.response import Response



class Sar:
    
    _submitRequest               : Callable[[Request], None]
    _maxMessageLength            : int
    _effectiveMaxMessageLength   : int
    _sequence                    : dict[asyncio.StreamWriter, tuple[deque[Request], deque[Response]]]
    _loop                        : asyncio.AbstractEventLoop

    _cacheTable                  : dict[tuple[str, str], tuple[Response, bytes]]
    _cacheTableAccept            : list[tuple[str, str]]
    _state                       : bool


    def __init__(self, submitRequest : Callable[[Request], None],
                        maxMessageLength:int, effectiveMaxMessageLength:int,
                        cacheTableAcceptlist:list[tuple[str, str]]) -> None:
        self._submitRequest = submitRequest
        self._maxMessageLength = maxMessageLength
        self._effectiveMaxMessageLength = effectiveMaxMessageLength
        self._sequence = {}
        self._cacheTable = {}
        self._cacheTableAccept = cacheTableAcceptlist
        self._state = True


    async def _monitor(self, sr:asyncio.StreamReader, sw:asyncio.StreamWriter, addr:tuple[str, int]) -> None:
        while 1:
            bMessage = await external.recv(sr, self._maxMessageLength, self._effectiveMaxMessageLength)
            if bMessage is None:
                del self._sequence[sw]
                sw.close()
                try:
                    await sw.wait_closed()
                except:
                    # 连接已经关闭，忽略即可
                    ...
                return
            else:
                request = change.toRequest(bMessage)
                self._sequence[sw][0].append(request)
                
                key = (request.path, request.target, )
                if key in self._cacheTable:                         # 命中缓存
                    self._cacheTable[key][0].sw = sw
                    self._cacheTable[key][0].request = request      # type: ignore
                    self.submitResponse(self._cacheTable[key][0], True)
                    # self.submitResponse(self._cacheTable[key][0])
                    continue

                request.addr = addr
                request.sw = sw
                request.submitResponse = self.submitResponse
                self._submitRequest(request)   # 提交请求


    async def _acceptLink(self, sk:socket.socket, addr:tuple[str, int]) -> None:
        sr, sw = await asyncio.open_connection(sock=sk)
        self._sequence[sw] = (deque([]), deque([]), )
        await self._monitor(sr, sw, addr)


    async def _send(self, response:Response, cache:bool=False):
        if not response.sw in self._sequence:
            return

        if self._sequence[response.sw][0][0] == response.request: # type: ignore
            if await external.send(response.sw, change.toResponse(response) if not cache else self._cacheTable[(response.request.path, response.request.target, )][1]) is False: # type: ignore
                del self._sequence[response.sw]
                return
            self._sequence[response.sw][0].popleft()
        else:
            self._sequence[response.sw][1].append(response)

        while 1:
            quantity = 0
            for i in self._sequence[response.sw][1]:
                quantity += 1
                if self._sequence[response.sw][0][0] == i.request: # type: ignore
                    quantity = -1
                    if await external.send(i.sw, change.toResponse(response) if not cache else self._cacheTable[(response.request.path, response.request.target, )][1]) is False: # type: ignore
                        del self._sequence[i.sw]
                        return
                    self._sequence[response.sw][0].popleft()
                    self._sequence[i.sw][1].remove(i)
                    break 
                if quantity == 10:
                    break

            if quantity == 10 or quantity == -1 or quantity == 0:
                break

        key = (response.request.path, response.request.target, ) # type: ignore
        if not key in self._cacheTable and key in self._cacheTableAccept:
            self._cacheTable[key] = (response, change.toResponse(response), )


    def submitLink(self, sk:socket.socket, addr:tuple[str, int]) -> None:
        asyncio.run_coroutine_threadsafe(self._acceptLink(sk, addr), self._loop)


    def submitResponse(self, response:Response, cache:bool=False) -> None:
        asyncio.run_coroutine_threadsafe(self._send(response, cache), self._loop)


    def _run(self, loop:asyncio.AbstractEventLoop) -> None:
        async def do():
            while self._state:
                try:
                    await asyncio.sleep(10)
                except asyncio.CancelledError:
                    break
            systemPrintInfo(f'线程退出：{current_thread().name}')
            return

        self._loop = loop
        asyncio.set_event_loop(self._loop)
        systemPrintInfo(f'已启动线程：{current_thread().name}')
        self._loop.run_until_complete(do())


    def run(self, threadName:str) -> asyncio.AbstractEventLoop:
        loop = asyncio.new_event_loop()
        t = Thread(target=self._run, args=(loop, ), name=f'{threadName}')
        t.start()
        return loop


    def close(self):
        self._state = False


    def urgentClose(self) -> None:
        tasks = [t for t in asyncio.all_tasks(self._loop) if t is not asyncio.current_task(self._loop)]
        for task in tasks:
            task.cancel()


    def SarCacheTableDel(self, key:tuple[str, str]):
        if key in self._cacheTable:
            del self._cacheTable[key]

