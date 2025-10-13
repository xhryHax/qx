
import urllib
from ..echoLevel.request import Request
from ..echoLevel.response import Response



code = {
    100 : (b'100', b'100 Continue'),
    101 : (b'101', b'101 Switching Protocols'),
    200 : (b'200', b'200 OK'),
    201 : (b'201', b'201 Created'),
    202 : (b'202', b'202 Accepted'),
    203 : (b'203', b'203 Non-Authoritative Information'),
    204 : (b'204', b'204 No Content'),
    205 : (b'205', b'205 Reset Content'),
    206 : (b'206', b'206 Partial Content'),
    300 : (b'300', b'300  Multiple Choices'),
    301 : (b'301', b'301 Moved Permanently'),
    302 : (b'302', b'302 Found'),
    303 : (b'303', b'303 See Other'),
    304 : (b'304', b'304 Not Modified'),
    305 : (b'305', b'305 Use Proxy'),
    306 : (b'306', b'307 Temporary Redirect'),
    400 : (b'400', b'400 Bad Request'),
    401 : (b'401', b'401 Unauthorized'),
    402 : (b'402', b'402 Payment Required'),
    403 : (b'403', b'403 Forbidden'),
    404 : (b'404', b'404 Not Found'),
    405 : (b'405', b'405 Method Not Allowed'),
    406 : (b'406', b'406 Not Acceptable'),
    407 : (b'407', b'407 Proxy Authentication Required'),
    408 : (b'408', b'408 Request Time-out'),
    409 : (b'409', b'409 Conflict'),
    410 : (b'410', b'410 Gone'),
    411 : (b'411', b'411 Length Required'),
    412 : (b'412', b'412 Precondition Failed'),
    413 : (b'413', b'413 Request Entity Too Large'),
    414 : (b'414', b'414 Request-URI Too Large'),
    415 : (b'415', b'415 Unsupported Media Type'),
    416 : (b'416', b'416 Requested range not satisfiable'),
    417 : (b'417', b'417 Expectation Failed'),
    500 : (b'500', b'500 Internal Server Error'),
    501 : (b'501', b'501 Not Implemented'),
    502 : (b'502', b'502 Bad Gateway'),
    503 : (b'503', b'503 Service Unavailable'),
    504 : (b'504', b'504 Gateway Time-out'),
    505 : (b'505', b'505 HTTP Version not supported')
}



def toRequest(bMessage:bytes) -> Request:
    '''
    首页时， target 的值为空字符串 ， path 的值为 '/'
    '''
    request = Request()

    # 分割数据体和标头
    index = bMessage.find(b'\r\n\r\n')
    request.data = bMessage[index+4:]
    headMessage = bMessage[0:index]

    # 标头头行处理
    lineList = headMessage.decode('utf-8').split('\r\n')
    head = lineList[0].split(' ')
    request.method = head[0]
    if (target := head[1].split('/')[-1]) == head[1]:
        request.path = ''
        request.target = '/'
    else:
        
        request.path = urllib.parse.unquote(head[1][:len(head[1])-len(target)]) # type: ignore
        request.target = urllib.parse.unquote(target) # type: ignore
    del lineList[0]
    
    # 标头字段处理
    headDict:dict[str,list[str]] = {}
    for item in lineList:
        key, value = item.replace(' ', '').split(':', 1)
        headDict[key] = value.split(',')
    request.header = headDict

    return request


def toResponse(response:Response) -> bytes:
    ''' 直接返回二进制对象 '''
    bytesList:list[bytes] = []

    bytesList.append(b'HTTP/1.1 ')
    bytesList.append(code[response.code][1])

    for item in response.header:
        bytesList.append(f'\r\n{item}: {", ".join(response.header[item])}'.encode('utf-8'))

    bytesList.append(b'\r\n\r\n' + (b'' if response.data is None else response.data))

    return b''.join(bytesList)



