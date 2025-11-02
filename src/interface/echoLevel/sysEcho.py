
from interface.echoLevel.request import Request
from interface.echoLevel.response import Response
from .echo import MiddleEcho



class Echo_sys_404(MiddleEcho):

    _targetCache = '''<!DOCTYPE html><html lang="cn"><head><meta charset="UTF-8"><title>页面不存在</title>
                        </head><body><h1 style="text-align: center;">404 所访问的页面不存在</h1><hr>
                        <h2 style="text-align: center;">**</h2></body></html>'''.encode('utf-8')

    async def echo(self, request: Request, response: Response) -> None:
        response.code = 404
        response.data = self._targetCache
        self.summary(request, response, '.html', False)



class Echo_sys_missing(MiddleEcho):

    _targetCache = '''<!DOCTYPE html><html lang="cn"><head><meta charset="UTF-8"><title>首页</title>
                        </head><body>
                        <h2 style="text-align: center;">qx</h2><hr></body></html>'''.encode('utf-8')
    
    def possible(self, method: str, path: str, target: str, header: dict[str, list[str]]) -> bool:
        if path == '/' and target == '':
            return True
        return False

    async def echo(self, request: Request, response: Response) -> None:
        response.code = 200
        response.data = self._targetCache
        self.summary(request, response, '.html', False)
