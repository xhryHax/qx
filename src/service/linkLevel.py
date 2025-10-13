
import asyncio
from ssl import SSLContext
from typing import Callable
from interface.linkLevel.sar import Sar
from interface.linkLevel.connect import Connect
from interface.echoLevel.request import Request
from interface.systemPrint import systemPrintErrorInfo, systemPrintInfo, systemPrintWarningInfo



class LinkLevel:

    submitRequest         : Callable[[Request], None]
    _connectTable         : dict[tuple[str, int], tuple[asyncio.AbstractEventLoop, Connect]]
    _sarTable             : dict[Sar, asyncio.AbstractEventLoop]
    _sarList              : list[Sar]
    _cacheTableAcceptlist : list[tuple[str, str]]


    def __init__(self, submitRequest:Callable[[Request], None]) -> None:
        self._connectTable = {}
        self._sarTable = {}
        self._sarList = []
        self._cacheTableAcceptlist = []
        self.submitRequest = submitRequest


    def getConnectQuantity(self) -> int:
        ''' 获取 Connect 数量 '''
        return len(self._connectTable)


    def getSarQuantity(self) -> int:
        '''获取 Sar 数量 '''
        return len(self._sarTable)


    def getSarCacheTable(self) -> list[tuple[str, str]]:
        ''' 获取表 '''
        return self._cacheTableAcceptlist


    def sarCacheTableAppend(self, path:str, target:str) -> None:
        ''' 添加允许缓存的项 '''
        self._cacheTableAcceptlist.append((path, target, ))


    def sarCacheTableDel(self, path:str, target:str) -> bool:
        ''' 删除指定的缓存项 '''
        key = (path, target, )
        if key in self._cacheTableAcceptlist:
            self._cacheTableAcceptlist.remove(key)
            for i in self._sarList:
                i.SarCacheTableDel(key)
            return True
        else:
            return False


    def runNewConnect(self, host:str, port:int, timeout:int=600, sslConText:SSLContext|None=None) -> bool:
        ''' 创建并运行一个 Connect 对象 '''
        connect = Connect(self._sarList, host, port, sslConText, timeout)
        if (loop := connect.run(f'Connect_thread_{host}:{port}')) is None:
            systemPrintErrorInfo(f'创建线程失败，线程名：Connect_thread_{host}:{port}', f'无法绑定：{host}:{port}')
            return False
        else:
            self._connectTable[(host, port, )] = (loop, connect, )
            return True


    def runNewSar(self, maxMessageLength:int, effectiveMaxMessageLength:int,) -> None:
        ''' 创建并运行一个 Sar 对象 '''
        maxMessageLength *= 1024 ** 2
        sar = Sar(self.submitRequest, maxMessageLength, effectiveMaxMessageLength, self._cacheTableAcceptlist)
        loop = sar.run(f'Sar_thread_{len(self._sarList)}')
        self._sarTable[sar] = loop
        self._sarList.append(sar)

        sarLength = len(self._sarList)
        for connect in self._connectTable:
            self._connectTable[connect][1].sarLength = sarLength


    def stopConnect(self, host:str, port:int) -> bool:
        ''' 终止指定端口的 Connect 对象 '''
        key = (host, port, )
        if key in self._connectTable:
            self._connectTable[key][1].close()
            systemPrintInfo(f'已终止线程：connect_thread_{host}:{port}')
            return True
        else:
            return False


    def stopSar(self, urgent:bool) -> bool:
        ''' 终止一个 Sar 对象，urgent 表示直接终止还是所有任务完成后再终止（不会产生新进入的任务）'''
        if len(self._sarList) == 0:
            systemPrintErrorInfo('Sar 对象终止失败', '已经没有 Sar 对象正在运行')
            return False
        for i in self._connectTable:
            self._connectTable[i][1].sarLength -= 1
        sar = self._sarList.pop()
        if urgent:
            sar.urgentClose()
        else:
            sar.close()

        if len(self._sarList) == 0:
            systemPrintWarningInfo('没有可用于收发数据的 Sar 对象', '已经没有 Sar 对象正在运行')

        return True



