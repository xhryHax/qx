
import socket
import asyncio
from ssl import SSLContext
from threading import Thread, current_thread

from interface.systemPrint import systemPrintErrorInfo, systemPrintInfo
from .sar import Sar



class Connect:

    host        : str
    port        : int
    timeout     : int
    sslConText  : SSLContext|None
    gateway     : socket.socket
    loop        : asyncio.AbstractEventLoop
    sarList     : list[Sar]
    sarLength   : int


    def __init__(self,  sarList:list[Sar],  host:str,
                        port:int,               sslConText:SSLContext|None,
                        timeout:int) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sslConText = sslConText
        self.sarList = sarList
        self.sarLength = len(self.sarList)


    async def _accept(self) -> None:
        index = 0
        self.gateway.listen()
        systemPrintInfo(f'已启用：http{'' if self.sslConText is None else 's'}://{self.host}:{self.port}')
        
        while 1:
            try:
                sk, addr = await self.loop.sock_accept(self.gateway)
            except Exception as e:
                systemPrintErrorInfo(f'线程 {current_thread().name} 终止，监听 {self.host}:{self.port} 的 Connect 对象异常', f'{e}')
                self.gateway.close()
                return
            except asyncio.CancelledError:
                self.gateway.close()
                return

            if self.sarLength == 0:
                sk.close()
                continue

            self.sarList[index-1].submitLink(sk if self.sslConText is None else self.sslConText.wrap_socket(sk, server_side=True), addr)
            
            index += 1
            if index == self.sarLength:
                index = 0


    def _run(self, loop:asyncio.AbstractEventLoop) -> None:
        self.loop = loop
        asyncio.set_event_loop(self.loop)
        systemPrintInfo(f'已启动线程：{current_thread().name}')
        self.loop.run_until_complete(self._accept())


    def run(self, threadName:str) -> None|asyncio.AbstractEventLoop:
        self.gateway = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.gateway.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.gateway.settimeout(self.timeout)
        self.gateway.setblocking(False)
        try:
            self.gateway.bind((self.host, self.port))
        except:
            return None

        loop = asyncio.new_event_loop()
        t = Thread(target=self._run, args=(loop, ), name=threadName)
        t.start()
        return loop


    def close(self) -> None:
        tasks = [t for t in asyncio.all_tasks(self.loop) if t is not asyncio.current_task(self.loop)]
        for task in tasks:
            task.cancel()

