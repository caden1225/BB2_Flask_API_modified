from config import nacos, myConfig

def errorFun(*args):
    for item in args:
        print(item)
    return "自定义错误"


nacosClient = nacos.nacosBalanceClient(ip=myConfig.nacosIp, port=myConfig.nacosPort,
                                       serviceName="mvp-api",
                                       group="DEFAULT_GROUP", namespaceId="public",timeout=3,
                                       timeOutFun=errorFun,fallbackFun=errorFun)


nacosClient1 = nacos.nacosBalanceClient(ip=myConfig.nacosIp, port=myConfig.nacosPort,
                                       serviceName="flask-api",
                                       group="DEFAULT_GROUP", namespaceId="public",timeout=3,
                                       timeOutFun=errorFun,fallbackFun=errorFun)

@nacosClient.customRequestClient(method="GET", url="/api/info")
def apiTest1():
    pass


@nacosClient1.customRequestClient(method="GET", url="/api/test2")
def apiTest2(id1: int, id2: int):
    pass


@nacosClient.customRequestClient(method="POST", url="/api/test3")
def apiTest3(formData):
    pass


@nacosClient.customRequestClient(method="POST", url="/api/test4", requestParamJson=True)
def apiTest4(jsonData):
    pass

@nacosClient.customRequestClient(method="GET", url="/api/test5")
def apiTest5(*args,**kwargs):
    pass