
from asyncio import StreamWriter
from typing import Callable
from .response import Response



class Request:
    '''
    addr    : 请求方地址，格式：(地址:str, 端口:int, )
    method  : 请求方法
    path    : 请求路径
    target  : 请求目标
    data    : 数据体
    header  : 所有标头，格式：{key : [value1, value2, ...]}
    sw      : 连接对象（写）

    header 中，value 包含对应值的指令
    '''

    addr    : tuple[str, int]
    method  : str
    path    : str
    target  : str
    data    : bytes
    header  : dict[str, list[str]]
    sw      : StreamWriter

    submitResponse : Callable[[Response], None]


    def __init__(self) -> None:
        self.header = {}


