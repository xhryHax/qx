
from typing import Any
from . import echoTool
from .request import Request
from .response import Response



class Echo:

    def possible(self, method:str, path:str, target:str, header:dict[str, list[str]]) -> bool:
        ''' 
        匹配函数，决定此 Echo 是否对这个请求进行响应 \n
        返回 True 为接受，False 为不接受 \n
        传入参数：
        ~~~
            method : 请求方法
            path   : 请求路径
            target : 请求目标
            header : 所有标头
        
        例子
        http://abc.com/home/index 
        path   为  /home/
        target 为  index

        例子
        http://abc 或 http://abc/
        path   为  /
        target 为  空字符串
        '''
        return False


    async def echo(self, request:Request, response:Response) -> None:
        '''
        响应函数
        ~~~
        实际进行响应的函数，在多线程环境之中运行
        request  是请求对象
        response 是响应对象
        修改 response 的属性以修改发送的响应
        不返回任何值
        '''
        ...



class FrontEcho(Echo):
    '''
    前置匹配对象
    ~~~
    用于进行请求拦截和请求预处理操作
    比如识别请求来源并拦截请求（访问 ）
    '''
    
    def interrupt(self, addr:tuple[str, int], method:str, path:str, target:str, header:dict[str, list[str]]) -> bool:
        '''
        前置 Echo 独有的 \n
        中断函数
        ~~~
        addr 为请求方地址，格式如：(ip:str, port:int, )
        其它参数与 possible 函数相同
        此函数的作用是：返回 True 将中断匹配，且仅用此 Echo 的 echo 函数进行响应

        注意，调用此函数的前提是 possible 函数返回为 True
        '''
        return False



class MiddleEcho(Echo):
    '''
    中置匹配对象
    ~~~
    用于对请求的资源、指令进行响应
    _targetCache 属性为响应内容缓存，可以用来存放一些需要的数据，外部不会访问此属性

    compressMime 属性为资源类型扩展名对应的 MIME 类型的声明值元组
        compressMime 的用法如：
            response.mime = self.compressMime['.js'] (response.mime => 'text/javascript')
        注意，compressMime 中只有常见的 MIME 类型
        完整 MIME 类型参照：https://www.iana.org/assignments/media-types/media-types.xhtml
    
    可以在 echo 方法中处理完事务后调用：self.summary
    这将完善：内容压缩、MIME 类型、响应生成时间、响应长度
    '''

    compressMime: dict[str, str] = {
        '.txt'  : 'text/plain',
        '.html' : 'text/html',
        '.css'  : 'text/css',
        '.csv'  : 'text/csv',
        '.js'   : 'text/javascript',
        '.jpg'  : 'image/jpeg'	,
        '.png'  : 'image/png',
        '.gif'  : 'image/gif',	
        '.svg'  : 'image/svg+xml',
        '.webp' : 'image/webp',
        '.ico'  : 'image/x-icon',	
        '.bmp'  : 'image/bmp',
        '.json' : 'application/json',
        '.xml'  : 'application/xml',
        '.pdf'  : 'application/pdf',
        '.zip'  : 'application/zip',
        '.gz'   : 'application/gzip',
        '.bin'  : 'application/octet-stream',
        '.doc'  : 'application/msword',
        '.docx' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.mp3'  : 'audio/mpeg',
        '.wav'  : 'audio/wav',
        '.ogg'  : 'audio/ogg',
        '.mp4'  : 'video/mp4',
        '.mpeg' : 'video/mpeg',
        '.mpg'  : 'video/mpeg',
        '.mov'  : 'video/quicktime',
        '.webm' : 'video/webm',
        '.avi'  : 'video/x-msvideo',
        '.woff' : 'font/woff',
        '.woff2': 'font/woff2',
        '.ttf'  : 'font/ttf',
        '.otf'  : 'font/otf',
    }
    _targetCache : Any


    def summary(self, request:Request, response:Response, mime:str|None=None, compress:bool=True) -> None:
        '''
        完善响应对象的值
        ~~~
        mime     : 资源的扩展名
        compress : 是否进行压缩，这里进行压缩只会使用 gzip 算法
        '''
        if not response.data is None:
            if compress:
                response.data = echoTool.compress(response.data, 'gzip')
            response.header['Content-Length'] = [str(len(response.data)), ]
        else:
            response.header['Content-Length'] = ['0', ]

        if not mime is None and mime in self.compressMime:
            response.header['Content-Type'] = [self.compressMime[mime], ]
        response.header['Date'] = [echoTool.getDate(), ]



class BehindEcho(Echo):
    '''
    后置匹配对象
    ~~~
    用于对中置对象的结果进一步处理，如对资源进行定制的变换
    '''


