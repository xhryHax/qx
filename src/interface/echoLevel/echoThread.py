

import asyncio
import sys
from threading import Thread, current_thread
from interface.echoLevel.sysEcho import Echo_sys_404
from interface.systemPrint import systemPrintErrorInfo, systemPrintInfo
from .request import Request
from .response import Response
from .echo import FrontEcho, MiddleEcho, BehindEcho



class EchoThread:

    frontEchoContainer  : list[FrontEcho]
    middleEchoContainer : list[MiddleEcho]
    behindEchoContainer : list[BehindEcho]
    possibleTable       : dict[tuple[str, str|None], tuple[list[FrontEcho], list[MiddleEcho], list[BehindEcho]]]
    possibleTableNo     : list[tuple[str, str|None]]
    loop                : asyncio.AbstractEventLoop

    echo_sys_404        : Echo_sys_404 = Echo_sys_404()


    def __init__(self, frontEchoContainer  : list[FrontEcho],
                        middleEchoContainer : list[MiddleEcho],
                        behindEchoContainer : list[BehindEcho],
                        possibleTable       : dict[tuple[str, str|None], tuple[list[FrontEcho], list[MiddleEcho], list[BehindEcho]]],
                        possibleTableNo     : list[tuple[str, str|None]]) -> None:
        self.frontEchoContainer = frontEchoContainer
        self.middleEchoContainer = middleEchoContainer
        self.behindEchoContainer = behindEchoContainer
        self.possibleTable = possibleTable
        self.possibleTableNo = possibleTableNo


    def _possible(self, request:Request) -> tuple[list[FrontEcho], list[MiddleEcho], list[BehindEcho]]:
        if (request.path, request.target, ) in self.possibleTable:
            return self.possibleTable[(request.path, request.target)]
        elif (request.path, None, ) in self.possibleTable:
            return self.possibleTable[(request.path, None)]

        frontContainer :list[FrontEcho]  = []
        middleContainer:list[MiddleEcho] = []
        behindContainer:list[BehindEcho]  = []

        for eo in self.frontEchoContainer:
            if eo.possible(request.method, request.path, request.target, request.header):
                frontContainer.append(eo)
                if eo.interrupt(request.addr, request.method, request.path, request.target, request.header):
                    return ([eo], [], [], )
        for eo in self.middleEchoContainer:
            if eo.possible(request.method, request.path, request.target, request.header):
                middleContainer.append(eo)
        for eo in self.behindEchoContainer:
            if eo.possible(request.method, request.path, request.target, request.header):
                behindContainer.append(eo)

        if len(middleContainer) == 0:       # 404
            middleContainer.append(self.echo_sys_404)
            return (frontContainer, middleContainer, behindContainer, )

        if (request.path, request.target, ) not in self.possibleTableNo:
            self.possibleTable[(request.path, request.target)] = (frontContainer, middleContainer, behindContainer, )
        elif (request.path, None, ) not in self.possibleTableNo:
            self.possibleTable[(request.path, None, )] = (frontContainer, middleContainer, behindContainer, )

        return (frontContainer, middleContainer, behindContainer, )


    async def _runEcho(self, request:Request, echoContainer:tuple[list[FrontEcho], list[MiddleEcho], list[BehindEcho]]) -> None:
        try:
            response = Response()

            for o in echoContainer[0]:
                try:
                    await o.echo(request, response)
                except Exception as e:
                    systemPrintErrorInfo(f'前置响应对象 {o}', f'{e}')
                    response.code = 500
            for o in echoContainer[1]:
                try:
                    await o.echo(request, response)
                except Exception as e:
                    systemPrintErrorInfo(f'中置响应对象 {o}', f'{e}')
                    response.code = 500
            for o in echoContainer[2]:
                try:
                    await o.echo(request, response)
                except Exception as e:
                    systemPrintErrorInfo(f'后置响应对象 {o}', f'{e}')
                    response.code = 500

            response.header['Server'] = ['qx', ]
            response.sw = request.sw
            response.request = request # type: ignore

            if 'Content-Length' not in response.header and 'Transfer-Encoding' not in response.header and response.code not in (100, 101, 204, 304, ):
                response.header['Content-Length'] = ['0' if response.data is None else str(len(response.data)), ]
            
            request.submitResponse(response)
        except asyncio.CancelledError:
            raise


    async def _resolveRequest(self, request:Request) -> None:
        await self._runEcho(request, self._possible(request))


    def resolveRequest(self, request:Request) -> None:
        asyncio.run_coroutine_threadsafe(self._resolveRequest(request), self.loop)


    def _run(self, loop:asyncio.AbstractEventLoop) -> None:
        async def do():
            try:
                while 1:
                    await asyncio.sleep(sys.maxsize)
            except asyncio.CancelledError:
                return

        self.loop = loop
        asyncio.set_event_loop(self.loop)
        systemPrintInfo(f'已启动线程：{current_thread().name}')
        self.loop.run_until_complete(do())


    def run(self, threadName:str) -> asyncio.AbstractEventLoop:
        loop = asyncio.new_event_loop()
        t = Thread(target=self._run, args=(loop, ), name=f'{threadName}')
        t.start()
        return loop


    def close(self) -> None:
        tasks = [t for t in asyncio.all_tasks(self.loop) if t is not asyncio.current_task(self.loop)]
        for task in tasks:
            task.cancel()


