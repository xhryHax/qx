
from asyncio import StreamWriter
from typing import Any



class Response:
    '''
    code    : 响应状态码
    data    : 数据体（bytes）
    header  : 所有标头，格式：{key : [value1, value2, ...]}
    cache   : 用于在多个 Echo 之间缓存数据的类属性，类型为 Any
    
    header 中，value 包含对应值的指令
    '''

    code    : int
    data    : bytes|None
    header  : dict[str, list[str]]
    cache   : Any

    sw      : StreamWriter
    # request : Request 实际上会显示的创建这个类属性，注释的原因是避免循环引用


    def __init__(self) -> None:
        self.header = {}
        self.data = None
        self.code = 500
