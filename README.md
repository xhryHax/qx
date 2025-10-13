
- **它叫什么？**
    - qx。
- **What is its name?**
    - qx。
***

- **这是什么？**
    - 这是一个使用纯 python 编写的 web 后端简易框架。
- **What is this?**
    - This is a simple web backend framework written in pure Python.
***


- **它能够做些什么？**
    - 和 Django、Flask 一样。
- **What can it do?**
    - Like Django and Flask.
***


- **它的性能如何？**
    - 基于 asyncio 编写，在 python 3.13 no-gil 下，能够充分利用多核性能，在 gil 下也能发挥不错性能，总之是不会逊色于 Flask 太多的。（也许实际的性能会给你一个惊喜，有兴趣的朋友可以自行压测）
- **How is its performance?**
    - Based on asyncio, it can fully utilize multi-core performance in Python 3.13 no-gil, and also perform well in GIL. In short, it will not be inferior to Flask by much. (Perhaps the actual performance will surprise you, interested friends can test it themselves)
***


- **怎么快速的启动这个框架，让我看到一点东西？**
    - 非常简单，实例化 Server 类，然后调用 run 方法即可，此时控制台会输出一些信息，如果包含：**“system info -> default: 已启用：http://172.0.0.1:80”** 就表示成功启动并开始监听端口。现在就可以通过游览器开始访问：**“http://172.0.0.1:80”**。这时你将看到默认的首页页面。
- **How to quickly launch this framework and show me something?**
    - It is very simple. Instantiate the Server class and call the run method. At this time, the console will output some information. If it contains: **"system info ->default: 已启用: http://172.0.0.1:80"** It means that it has successfully started and started listening to the port. You can now start accessing through the browser:**"http://172.0.0.1:80"**. At this point, you will see the default homepage page.
- **代码 | code**
```python
    import Server
    sv = Server()
    sv.run()
```
***


- **怎么进一步的使用这个框架？**
    - 在开始前，需要了解一些东西。
        - qx 的工作流程（简易的）：
            - 1.`Connect` 对象接受连接，然后将连接传递给 `Sar` 对象。
            - 2.`Sar` 对象从连接中读取数据并转换为 `Request` 对象，然后传递给 `EchoThread` 对象。
            - 3.`EchoThread` 对象使用此 `Request` 对象对应的 `BehindEcho`，`FrontEcho`，`MiddleEcho` 这三类对象分别按顺序进行调用。
            - 4.`BehindEcho`，`FrontEcho`，`MiddleEcho` 这三类对象产生具体的响应。
    - “`FrontEcho`”对象：
        - 前置响应对象，类似于 `Flask` 中的钩子，将在 `MiddleEcho` 对象之前进行调用，一般用于对请求进行预处理。
    - “`MiddleEcho`”对象：
        - 中置响应对象，此对象进行具体的响应，比如加载一个 `HTML` 文档。
    - “`BehindEcho`”对象：
       - 后置响应对象，此对象在 `MiddleEcho` 对象之后进行调用，一般用于对响应进行进一步处理，如将 `HTML` 中的文字修改为合适客户端语言的文字。
    - @ 我构建了一个前端项目，需要托管，应该怎么做？
        - 你可以在实例化 `Server` 对象后，调用 `adaptationProject` 方法，传入你的项目根路径即可。
    - @ 我想要定制的响应一个东西，应该怎么做？
        - 你可以继承 `MiddleEcho` 对象，然后重写对应的方法，然后调用 `Server` 对象的 `middleEchoAppend` 方法，将你的对象传入即可。
- **How to further utilize this framework?**
    - Before starting, it is necessary to understand something.
        - qx workflow (simple):
        - 1: The `Connect` object accepts the connection and then passes it to the `Sar` object
        - 2: The `Sar` object reads data from the connection and converts it into a `Request` object, which is then passed to the `EchoThread` object
        - 3: The `EchoThread` object is called sequentially using the three types of objects corresponding to this `Request` object: `BehindEcho`, `FrontEcho`, and `MiddleEcho`
        - 4: The three types of objects, `BehindEcho`, `FrontEcho`, and `MiddleEcho`, generate specific responses
    - `FrontEcho` object:
        - Pre response objects, similar to hooks in `Flask`, are called before `MiddleEcho` objects and are typically used for preprocessing requests.
    - `MiddleEcho` object:
        - Mid set response object, which performs specific responses, such as loading an `HTML` document.
    - `BehindEcho` object:
        - Post response object, which is called after the `MiddleEcho` object and is generally used for further processing of the response, such as modifying text in `HTML` to appropriate client language.
    - @ I have built a front-end project that requires hosting. What should I do?
        - You can call the `adaptationProject` method after instantiating the `Server` object and pass in your project root path
    - @ What should I do to customize a response to something?
        - You can inherit the MiddleEcho object, rewrite the corresponding method, and then call the `middleEchoAppend` method of the `Server` object to pass in your object.
***




