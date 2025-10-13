
import gzip
from email import utils
from typing import Callable



algorithmTable : dict[str, Callable[[bytes], bytes]] = {
    'gzip' : gzip.compress
}



def getDate() -> str:
    ''' 生成当前的 GMT 时间 '''
    return utils.formatdate(usegmt=True)



def compress(data:bytes, algorithmType:str) -> bytes:
    '''
    压缩函数
    ~~~
    data 为需要压缩的数据
    algorithmType 为实现函数的标识值（此模块下的 algorithmTable 字典的 key）

    需要怎加支持的算法只需要向 algorithmTable 添加键值对即可
    algorithmTable 个格式为 dict[str, Callable[[bytes], bytes]]
    其 key 和 algorithmType 的参数的值相等
    其 value 为实现函数，函数需要接受一个 bytes 参数，返回一个 bytes 值
    '''
    return algorithmTable[algorithmType](data)



def weight(s:str) -> float:
    ''' 获取项的权重 '''
    idx = s.find('q=')
    return float(s[idx+2:]) if idx != -1 else 1




