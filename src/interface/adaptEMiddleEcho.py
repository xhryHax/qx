
import os

from interface.systemPrint import systemPrintInfo
from .echoLevel.request import Request
from .echoLevel.response import Response
from .echoLevel.echo import MiddleEcho



class AdaptEMiddleEcho(MiddleEcho):

    contentPath : str
    contentBytes: bytes
    path        : str
    target      : str
    method      : str
    filePath    : str


    def __init__(self, contentPath:str, path:str, target:str, method:str, filePath:str):
        self.contentPath = contentPath
        self.path = path
        self.target = target
        self.method = method
        self.filePath = filePath
        with open(file=self.filePath, mode='rb') as f:
            self._targetCache = f.read()


    def possible(self, method: str, path: str, target: str, header: dict[str, list[str]]) -> bool:
        if method == self.method and path == self.path and target == self.target:
            return True
        return False


    async def echo(self, request: Request, response: Response) -> None:
        response.data = self._targetCache
        response.code = 200
        self.summary(request, response, None if (target:=self.target[self.target.find('.'):]) == '' else target, False)



class AdaptEMiddleEchoDebug(AdaptEMiddleEcho):

    def __init__(self, contentPath: str, path: str, target: str, method: str, filePath: str):
        self.contentPath = contentPath
        self.path = path
        self.target = target
        self.method = method
        self.filePath = filePath


    async def echo(self, request: Request, response: Response) -> None:
        try:
            with open(file=self.filePath, mode='rb') as f:
                response.data = f.read()
            response.code = 200
        except:
            response.code = 404
        self.summary(request, response, None if (target:=self.target[self.target.find('.'):]) == '' else target, False)



class AdaptationProject:

    projectStructure : list[str]
    projectEcho      : list[MiddleEcho]
    rootPath         : str
    debug            : bool


    def __init__(self, projectRootPath:str, debug:bool=True) -> None:
        ''' projectPath ：项目根路径 '''
        self.rootPath = projectRootPath.replace('\\', '\\')
        self.projectStructure = self._selectAllFile()
        self.debug = debug
        self._build()


    def _selectAllFile(self) -> list[str]:
        allFiles:list[str] = []
        for root, _, files in os.walk(self.rootPath):
            for file in files:
                filePath = os.path.join(root.replace(f'{self.rootPath}', ''), file).replace('\\', '/')
                allFiles.append(filePath)
        return allFiles


    def _build(self) -> None:
        self.projectEcho = []
        for i in self.projectStructure:
            if (target := i.split('/')[-1]) == i:
                if target[:target.find('.')] in ('index', 'home'):
                    # 首页
                    self.projectEcho.append(AdaptEMiddleEcho(i, '/', '', 'GET', f'{self.rootPath}\\{target}') if not self.debug 
                                                else AdaptEMiddleEchoDebug(i, '/', '', 'GET', f'{self.rootPath}\\{target}'))
                    systemPrintInfo(f'{self.rootPath}\\{target} -> /')
                self.projectEcho.append(AdaptEMiddleEcho(i, '/', target, 'GET', f'{self.rootPath}\\{target}') if not self.debug 
                                                else AdaptEMiddleEchoDebug(i, '/', target, 'GET', f'{self.rootPath}\\{target}'))
                systemPrintInfo(f'{self.rootPath}\\{target} -> /{target}')
            else:
                self.projectEcho.append(AdaptEMiddleEcho(i, i[:len(i)-len(target)], target, 'GET', f'{self.rootPath}{i[:len(i)-len(target)].replace('/', '\\')}{target}') if not self.debug 
                                                else AdaptEMiddleEchoDebug(i, i[:len(i)-len(target)], target, 'GET', f'{self.rootPath}{i[:len(i)-len(target)].replace('/', '\\')}{target}'))
                systemPrintInfo(f'{self.rootPath}\\{target} -> {i[:len(i)-len(target)]}{target}')


    def getProjectEcho(self) -> list[MiddleEcho]:
        return self.projectEcho


