# -*- coding: UTF-8 -*-

from flask import Flask, request
import logging
import time
from copy import deepcopy
from services.interactive_api import SHARED, InteractiveWeb
from config import myConfig
import requests
import os
import re

# os.environ["CUDA_VISIBLE_DEVICES"] = "0"
# os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
# os.environ["TRANSFORMERS_OFFLINE"] = "1"

app = Flask(__name__)

# 导入sdk

# import KcangNacos.nacos as nacos
# 创建初始nacos连接对象
from config import nacos

nacosServer = nacos.nacos(ip=myConfig.nacosIp, port=myConfig.nacosPort)

# 将本地配置注入到nacos对象中即可获取远程配置，并监听配置变化实时变更
nacosServer.config(dataId="demo-python.json", group="DEFAULT_GROUP", tenant="public", myConfig=myConfig.GlobalConfig)
# nacosServer.config(dataId="python.json",group="dev",tenant="public",myConfig=myConfig.GlobalConfig)
# 配置服务注册的参数
nacosServer.registerService(serviceIp=myConfig.SERVICE_IP, servicePort=myConfig.PORT, serviceName="chat-api",
                            namespaceId="public", groupName="DEFAULT_GROUP")
# 开启监听配置的线程和服务注册心跳进程的健康检查进程
nacosServer.healthyCheck()

from controller import providerController, consumerController

# 将配置传给控制层使用即可
providerController.main(app, myConfig.GlobalConfig)
# nacos 服务消费者demo 负载均衡
consumerController.main(app)
# 熔断限流demo
# fuseController.main(app)


response_template = {
    "code": 0,
    "message": '操作成功',
    "data": {
        "type": 'text',
        "content": None
    }
}

# 20220310修改至外挂翻译API
def translate_api(fromLang, toLang, content):
    translate_url = 'http://' + myConfig.search_host + ':' + str(myConfig.translate_port) + '/baidu_translate'

    params = {
        'fromLang': fromLang,
        'toLang': toLang,
        'content': content
    }
    text = requests.get(translate_url, params=params).text
    return text


# 20220314直接在模型返回结果上过滤unsafe
def clean_unsafe(content):
    import re
    re_str = re.sub("""_+[A-Za-z_]+_+""", "", content)
    return re_str


@app.route("/chat_with_chinese", methods=("GET", "POST"))
def _chat_with_chinese():
    # logging.info(request)
    started = time.time()
    data = request.json
    data['input_text'] = re.sub(' ', '', data['input_text'])
    if len(data['input_text']) == 0:
        return "not null"
    logging.warning(data)

    response = deepcopy(response_template)

    input_raw = data['input_text']
    if all(ord(char) < 128 for char in input_raw):
        input_chat = {'episode_done': False, 'text': input_raw}
    else:
        content_en = translate_api(fromLang='zh', toLang='en', content=input_raw)
        input_chat = {'episode_done': False, 'text': content_en}

    logging.warning(f"model_input: {input_chat}")

    try:
        SHARED['agent'].observe(input_chat)
        model_response = SHARED['agent'].act()
    except Exception as e:
        if "CUDA out of memory" in str(e):
            logging.warning("*" * 20)
            logging.warning("trigger the reset")
            SHARED['agent'].reset()
            SHARED['agent'].observe(input_chat)
            model_response = SHARED['agent'].act()
        else:
            print(e)
            raise e

    logging.warning(model_response['text'])
    response_cleaned = clean_unsafe(model_response['text'])
    # 20220310修改至外挂翻译API
    reply_chinese = translate_api(fromLang='en', toLang='zh', content=response_cleaned)

    response['code'] = 200
    response['data']['content'] = reply_chinese
    time_used = time.time() - started
    logging.warning(f"cost time {time_used:.4f}s")
    logging.warning(response)
    return response


@app.route("/chat_with_english", methods=("GET", "POST"))
def _chat_with_bot():
    data = request.json
    input_text = data['input_text']
    response = deepcopy(response_template)

    # 补充空格验证，空输入导致模型跳出
    if len(input_text) < 1:
        response['code'] = 500
        response['message'] = '请勿进行空输入'
        return response

    input_chat = {'episode_done': False, 'text': input_text}
    SHARED['agent'].observe(input_chat)
    try:
        response_en = SHARED['agent'].act()
    except Exception as e:
        if "CUDA out of memory" in str(e):
            SHARED['agent'].reset()
            SHARED['agent'].observe(input_chat)
            response_en = SHARED['agent'].act()
        else:
            raise e

    response['code'] = 200
    response['data']['content'] = response_en['text']
    return response


@app.route("/reset", methods=("GET", "POST"))
def _reset():
    SHARED['agent'].reset()
    response = deepcopy(response_template)
    response['code'] = 200
    response['data']['content'] = 'DONE'
    return response


@app.route("/", methods=("GET", "POST"))
def _root_response(self):
    # return "TODO_STATUS"
    response = deepcopy(response_template)
    response['code'] = 200
    response['data']['content'] = "TODO_STATUS"
    return response


if __name__ == '__main__':
    InteractiveWeb.main(
        "--o", "config/blenderbot2-400M-DI.json",
        "--allow-missing-init-opts", "true",
        "--mf", "zoo:blenderbot2/blenderbot2_400M/model",
        "--datapath", "/data/data_hub",
        "--knowledge-access-method", "classify"
    )

    app.run(host=myConfig.IP, port=myConfig.PORT, debug=False)
