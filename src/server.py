
from ssl import SSLContext
from interface.echoLevel.sysEcho import Echo_sys_missing
from service.linkLevel import LinkLevel
from service.echoLevel import EchoLevel
from interface.adaptEMiddleEcho import AdaptationProject
from interface.echoLevel.echo import MiddleEcho, FrontEcho, BehindEcho



class Server:
    '''
    实例化 Server 对象，以操控框架
    ~~~
    对象：
        Connect    对象：接受客户端的连接（运行在独立线程中）
        Sar        对象：收发客户端的数据（运行在独立线程中）
        EchoThread 对象：调用实际进行响应的对象（运行在独立线程中）
        FrontEcho  对象：实际进行响应的前置响应对象，被 EchoThread 调用，通常对请求进行预处理或拦截等操作，类似于钩子
        MiddleEcho 对象：实际进行响应的中置响应对象，被 EchoThread 调用，通常对请求进行响应，入构造合适的 HTML 文档
        BehindEcho 对象：实际进行响应的后置响应对象，被 EchoThread 调用，通常对请求进行进一步处理，如为 HTML 适配对应的语言
    方法：
        run()                           默认的启动框架，若 Connect 对象或 Sar 对象或 EchoThread 对象低于一个会自动创建一个
                                        注意：调用 run 不是必要的，创建好 Connect、Sar、EchoThread 后其实就已经在运行了
        runNewConnect()                 创建 Connect 对象并启用
        runNewSar()                     创建 Sar 对象并启用
        runNewEchoThread()              创建 EchoThread 对象并启用
        middleEchoAppend()              添加 MiddleEcho 对象
        frontEchoAppend()               添加 FrontEcho 对象
        behindEchoAppend()              添加 BehindEcho 对象
        cacheTableAcceptlistAppend()    向响应缓存表中添加项
        cacheTableAcceptlistDel()       在响应缓存表中删除对应项
        setPossibleTableNo()            项路由匹配缓存中添加排除项
        adaptationProject()             构造指向的项目 URI 和 MiddleEcho 对象
    '''

    linkLevel     : LinkLevel
    echoLevel     : EchoLevel


    def __init__(self) -> None:
        self.echoLevel = EchoLevel()
        self.linkLevel = LinkLevel(self.echoLevel.submitRequest)


    def runNewConnect(self, host:str, port:int, timeout:int=600, sslConText:SSLContext|None=None) -> bool:
        '''
        创建并启用 Connect 对象，用于接受对方连接
        ~~~
        host       : 绑定地址
        port       : 绑定端口
        timeout    : 超时时间（s）
        sslConText : ssl.SSLContext 对象，用于启用 https

        返回 True 表示成功，False 表示失败
        '''
        if self.linkLevel.runNewConnect(host, port, timeout, sslConText):
            return True
        else:
            return False


    def stopConnect(self, host:str, port:int) -> bool:
        ''' 终止对应的 Connect 对象 '''
        return self.linkLevel.stopConnect(host, port)


    def runNewSar(self, maxMessageLength:int=1024, effectiveMaxMessageLength:int=8192) -> None:
        '''
        创建并启用 Sar 对象，用于接收和发送数据（包括报文解析）
        ~~~
        maxMessageLength          : 请求最大接受长度（MB）
        effectiveMaxMessageLength : 在没有长度声明时，超出必须校验完整性，否则尝试直接解析（B）
        '''
        self.linkLevel.runNewSar(maxMessageLength, effectiveMaxMessageLength)


    def stopSar(self, urgent:bool=False) -> bool:
        ''' 终止一个 Sar 对象，urgent 表示直接终止还是所有任务完成后再终止（不会产生新进入的任务） '''
        return self.linkLevel.stopSar(urgent)


    def runNewEchoThread(self) -> None:
        ''' 创建并启用 EchoTHread 对象，用于进行实际的响应 '''
        self.echoLevel.newRunEchoThread()


    def stopEchoThread(self) -> None:
        ''' 终止一个 EchoThread 对象 '''
        self.echoLevel.stopEchoThread()


    def middleEchoAppend(self, middleEcho:MiddleEcho) -> None:
        ''' 添加 MiddleEcho 对象 '''
        self.echoLevel.middleEchoAppend(middleEcho)


    def frontEchoAppend(self, frontEcho:FrontEcho) -> None:
        ''' 添加 FrontEcho 对象 '''
        self.echoLevel.frontEchoAppend(frontEcho)


    def behindEchoAppend(self, behindEcho:BehindEcho) -> None:
        ''' 添加 BehindEcho 对象 '''
        self.echoLevel.behindEchoAppend(behindEcho)


    def cacheTableAcceptlistAppend(self, path:str, target:str) -> None:
        ''' 添加允许缓存结果的项，将加快响应速度，但仅适合长时间不变动的静态资源，使用时注意内存占用 '''
        self.linkLevel.sarCacheTableAppend(path, target)


    def cacheTableAcceptlistDel(self, path:str, target:str) -> None:
        ''' 删除允许缓存结果的项 '''
        self.linkLevel.sarCacheTableDel(path, target)


    def setPossibleTableNo(self, path:str, target:str|None) -> None:
        '''
        设置不进行匹配缓存的 URI
        ~~~
        path 为 URI 路径，target 为 URI 目标
        当 URI 目标即 target 为 None 时，将只对 path 进行排除
        '''
        self.echoLevel.setPossibleTableNo(path, target)


    def adaptationProject(self, projectPath:str, debug:bool=True) -> None:
        '''
        projectPath 指定的目录作为根目录，按照目录结构生成对应的 URI，对目录中所有的项目进行响应
        ~~~
        将生成对应的 MiddleEcho 对象放入 EchoThread 中进行实际的响应
        index.html 将会额外作为请求 '/' 时的响应对象
        示例：
            目录结构：
                projectPath
                |--index.html
                |--css
                |   |--index.css
                |--js
                |   |--index.js
            生成：
                /               指向    index.html
                /index.html     指向    index.html
                /css/index.css  指向    index.css
                /js/index.js    指向    index/js
        '''
        ap = AdaptationProject(projectPath, debug)
        for i in ap.getProjectEcho():
            self.middleEchoAppend(i)


    def run(self):
        '''
        启动
        ~~~
        默认情况下，如果没有进行任何其它操作
        将创建一个 EChoThread、Sar、Connect 对象
        Connect 对象将监听 127.0.0.1:8080 的连接
        '''
        if self.echoLevel.getEchoThreadQuantity() == 0:
            self.runNewEchoThread()
        if self.linkLevel.getSarQuantity() == 0:
            self.runNewSar()
        if self.linkLevel.getConnectQuantity() == 0:
            self.runNewConnect('127.0.0.1', 80)
        
        if self.echoLevel.getMiddleEchoQuantity() == 0:
            self.middleEchoAppend(Echo_sys_missing())



if __name__ == '__main__':
    sv = Server()
    sv.cacheTableAcceptlistAppend('/', '')
    sv.run()




