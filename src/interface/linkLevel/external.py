
import asyncio



async def recv(sr:asyncio.StreamReader, maxMessageLength:int, effectiveMaxMessageLength:int) -> bytes|None:
    '''
    返回完整的请求报文，以 bytes 形式，返回 None 表示连接异常，函数在异常时不会尝试关闭连接
    ~~~
    sr                        : 异步读对象
    maxMessageLength          : 报文的允许最大长度，超出将丢弃整个报文
    effectiveMaxMessageLength : 报文没有长度说明时接受的最大长度，小于长度系统将尝试解析，否则将视为无效报文
    '''
    bMessage = bytearray()
    
    try:
        while True:
            if len(bMessage) >= maxMessageLength:
                # 超出最大长度限制
                return None
            
            temporary = await sr.read(4096)
            bMessage.extend(temporary)

            if len(bMessage) % 4096 == 0:
                # 满的返回字节内容，还有字节内容
                if len(temporary) == 0:
                    # 恰好实际的字节内容就是整数倍？，即 read 返回 0 字节
                    if len(bMessage) > 0:
                        # 之前有数据，进行完整性校验，不通过直接返回 None ，而不是等待
                        if check(bMessage, effectiveMaxMessageLength):
                            return bytes(bMessage)
                        else:
                            return None
                    else:
                        # 之前没有数据，直接返回 None
                        return None
                else:
                    continue
            else:
                # 不是满的返回，没有后续字节内容或还未到达
                # 进行完整性校验，通过则返回，不通过则继续等待，直到超时返回 None
                if check(bMessage, effectiveMaxMessageLength):
                    return bytes(bMessage)
                else:
                    continue
    except:
        return None



async def send(sw:asyncio.StreamWriter, bMessage:bytes) -> bool:
    try:
        sw.write(bMessage)
        await sw.drain()
        return True
    except:
        return False



def check(bMessage:bytearray, effectiveMaxMessageLength:int) -> bool:
    '''
    True 表示通过完整性校验
    ~~~
    当报文携带 Content-Length 或 Transfer-Encoding: chunked 时，只有计算结果正确才会通过校验
    当不携带这两者时，判断是否在最大无数据体报文长度之内，在则通过，不在则不通过
    '''
    position = bMessage.find(b'Content-Length')

    if position == -1:
        # 没有找到声明报文长度的字段
        if bMessage.find(b'Transfer-Encoding: chunked') == -1:
            # 没有找到 Transfer-Encoding 声明
            if len(bMessage) < effectiveMaxMessageLength:
                # 最小报文长度之内
                return True
            else:
                # 无法确认
                return False
        else:
            # Transfer-Encoding: chunked 计算方式 
            if bMessage.find(b'0\r\n\r\n') == -1:
                # 没有找到尾部声明
                return False
            else:
                return True
    else:
        # 找到声明报文长度的字段
        # Content-Length 计算方式
        length = int(bMessage[position + 16 : bMessage.find(b'\r\n', position)].strip())
        dataPosition = bMessage.find(b'\r\n\r\n')
        
        if length == len(bMessage[dataPosition+4:]):
            return True
        else:
            return False




