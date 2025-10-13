
import asyncio
from interface.echoLevel.request import Request
from interface.echoLevel.echoThread import EchoThread
from interface.echoLevel.echo import BehindEcho, FrontEcho, MiddleEcho



class EchoLevel:
    
    _frontEchoContainer  : list[FrontEcho]
    _middleEchoContainer : list[MiddleEcho]
    _behindEchoContainer : list[BehindEcho]
    _echoThreadTable     : dict[int, tuple[asyncio.AbstractEventLoop, EchoThread]]
    _possibleTable       : dict[tuple[str, str|None], tuple[list[FrontEcho], list[MiddleEcho], list[BehindEcho]]]
    _possibleTableNo     : list[tuple[str, str|None]]
    _echoThreadQuantity  : int
    _echoThreadIndex     : int = 0


    def __init__(self) -> None:
        self._frontEchoContainer = []
        self._middleEchoContainer = []
        self._behindEchoContainer = []
        self._echoThreadTable = {}
        self._possibleTable = {}
        self._possibleTableNo = []
        self._echoThreadQuantity = 0


    def newRunEchoThread(self) -> None:
        ''' 创建并运行一个 echoThread 对象 '''
        et = EchoThread(self._frontEchoContainer, self._middleEchoContainer, self._behindEchoContainer,
                        self._possibleTable, self._possibleTableNo)
        loop = et.run(f'Echo_thread_{self._echoThreadQuantity}')
        self._echoThreadTable[self._echoThreadQuantity] = (loop, et, )
        self._echoThreadQuantity += 1


    def stopEchoThread(self) -> None:
        ''' 终止一个 EchoThread 对象 '''
        _, et = self._echoThreadTable[self._echoThreadQuantity]
        self._echoThreadQuantity -= 1
        et.close()
        del self._echoThreadTable[self._echoThreadQuantity]
        del et


    def frontEchoAppend(self, frontEcho:FrontEcho) -> None:
        self._frontEchoContainer.append(frontEcho)


    def middleEchoAppend(self, middleEcho:MiddleEcho) -> None:
        self._middleEchoContainer.append(middleEcho)


    def behindEchoAppend(self, BehindEcho:BehindEcho) -> None:
        self._behindEchoContainer.append(BehindEcho)


    def getEchoThreadQuantity(self) -> int:
        return len(self._echoThreadTable)


    def getFrontEchoQuantity(self) -> int:
        return len(self._frontEchoContainer)


    def getMiddleEchoQuantity(self) -> int:
        return len(self._middleEchoContainer)


    def getBehindEchoQuantity(self) -> int:
        return len(self._behindEchoContainer)


    def submitRequest(self, request:Request) -> None:
        if self._echoThreadQuantity == 0:
            return

        self._echoThreadTable[self._echoThreadIndex][1].resolveRequest(request)

        if self._echoThreadIndex >= self._echoThreadQuantity:
            self._echoThreadIndex = 0


    def setPossibleTableNo(self, path:str, target:str|None) ->None:
        key = (path, target, )
        self._possibleTableNo.append(key)
        if key in self._possibleTable:
            del self._possibleTable[key]



