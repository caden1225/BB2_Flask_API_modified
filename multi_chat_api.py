# -*- coding: utf-8 -*-
# @Time    : 2022/6/10 下午3:50
# @Author  : caden1225
# @File    : chat_api.py
# @Description : 依据单例修改的多用户api服务, 通过userName区分不同用户

from flask import Flask, request
import logging
import time
from copy import deepcopy
from services.multi_interactive_api import SHARED, MultiInteractive
from config import myConfig
import requests
import re

app = Flask(__name__)
MAX_CONNECTS = myConfig.MAX_NUMS
SHARED['connect_num'] = 0
USER_LIST = {}

# from config import nacos
# nacosServer = nacos.nacos(ip=myConfig.nacosIp, port=myConfig.nacosPort)
# # 将本地配置注入到nacos对象中即可获取远程配置，并监听配置变化实时变更
# nacosServer.config(dataId="demo-python.json", group="DEFAULT_GROUP", tenant="public", myConfig=myConfig.GlobalConfig)
# # nacosServer.config(dataId="python.json",group="dev",tenant="public",myConfig=myConfig.GlobalConfig)
# # 配置服务注册的参数
# nacosServer.registerService(serviceIp=myConfig.SERVICE_IP, servicePort=myConfig.PORT, serviceName="multi-chat-api",
#                             namespaceId="public", groupName="DEFAULT_GROUP")
# # 开启监听配置的线程和服务注册心跳进程的健康检查进程
# nacosServer.healthyCheck()
# from controller import providerController, consumerController
# # 将配置传给控制层使用即可
# providerController.main(app, myConfig.GlobalConfig)
# # nacos 服务消费者demo 负载均衡
# consumerController.main(app)
# # 熔断限流demo
# # fuseController.main(app)
response_template = {
    "code": 0,
    "message": '操作成功',
    "data": {
        "type": 'text',
        "content": None,
    }
}


def clean_timeout_session():
    global USER_LIST
    for userName in list(USER_LIST.keys()):
        if time.time() - USER_LIST[userName] > 300:
            del SHARED[userName]
            del USER_LIST[userName]
            if SHARED['connect_num'] > 0:
                SHARED['connect_num'] -= 1

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
    global USER_LIST
    started = int(time.time())
    data = request.json
    signType = data.get('type',0)
    if len(data['input_text']) == 0:
        return "not null"
    logging.warning(data)
    response = deepcopy(response_template)
    userName = data['userName']
    input_raw = data['input_text']

    if all(ord(char) < 128 for char in input_raw):
        input_chat = {'episode_done': False, 'text': input_raw}
    elif signType == 1 or signType == '1':
        input_chat = {'episode_done': False, 'text': input_raw}
    else:
        input_raw = re.sub(' ', '', input_raw)
        content_en = translate_api(fromLang='zh', toLang='en', content=input_raw)
        input_chat = {'episode_done': False, 'text': content_en}
    logging.warning(f"model_input: {input_chat}")

    clean_timeout_session()
    if SHARED['connect_num'] == MAX_CONNECTS and not SHARED.get(userName, None):
        raise Exception("超出最大连接数")
    elif not SHARED.get(userName, None):
        SHARED[userName] = SHARED['agent_ori'].clone()
        SHARED['connect_num'] += 1
        USER_LIST[userName] = started
        logging.warning(f"detected new userName {userName}, created a new clone at {started}")

    try:
        SHARED[userName].observe(input_chat)
        model_response = SHARED[userName].act()
    except Exception as e:
        if "CUDA out of memory" in str(e):
            logging.warning("*" * 20)
            logging.warning("trigger the reset")
            SHARED[userName].reset()
            SHARED[userName].observe(input_chat)
            model_response = SHARED[userName].act()
        else:
            print(e)
            raise e

    logging.warning(model_response['text'])
    response_cleaned = clean_unsafe(model_response['text'])
    # 20220310修改至外挂翻译API
    reply_chinese = translate_api(fromLang='en', toLang='zh', content=response_cleaned)

    response['code'] = 200
    response['data']['content'] = reply_chinese
    response['data']['english'] = response_cleaned
    response['userName'] = userName
    time_used = time.time() - started
    logging.warning(f"cost time {time_used:.4f}s")
    logging.warning(response)
    return response


@app.route("/chat_with_english", methods=("GET", "POST"))
def _chat_with_bot():
    global USER_LIST

    data = request.json
    started = int(time.time())
    userName = data['userName']
    input_text = data['input_text']
    response = deepcopy(response_template)

    # 补充空格验证，空输入导致模型跳出
    if len(input_text) < 1:
        response['code'] = 500
        response['message'] = '请勿进行空输入'
        response['userName'] = userName
        return response

    input_chat = {'episode_done': False, 'text': input_text}
    clean_timeout_session()
    if SHARED['connect_num'] == MAX_CONNECTS and not SHARED.get(userName, None):
        raise Exception("超出最大连接数")
    elif not SHARED.get(userName, None):
        SHARED[userName] = SHARED['agent_ori'].clone()
        SHARED['connect_num'] += 1
        USER_LIST[userName] = started
        logging.warning(f"detected new userName {userName}, created a new clone at {started}")

    SHARED[userName].observe(input_chat)
    try:
        response_en = SHARED[userName].act()
    except Exception as e:
        if "CUDA out of memory" in str(e):
            SHARED[userName].reset()
            SHARED[userName].observe(input_chat)
            response_en = SHARED[userName].act()
        else:
            raise e

    response['code'] = 200
    response['data']['content'] = response_en['text']
    response['userName'] = userName
    return response


@app.route("/reset", methods=("GET", "POST"))
def _reset():
    data = request.json
    userName = data['userName']
    if SHARED.get(userName, None):
        SHARED[userName].reset()
    # return "Done"
    response = deepcopy(response_template)
    response['code'] = 200
    response['data']['content'] = 'DONE'
    response['userName'] = userName
    return response


@app.route("/", methods=("GET", "POST"))
def _root_response(self):
    # return "TODO_STATUS"
    response = deepcopy(response_template)
    response['code'] = 200
    response['data']['content'] = "TODO_STATUS"
    return response


if __name__ == '__main__':
    MultiInteractive.main(
        "--o", "config/blenderbot2-400M-DI.json",
        "--allow-missing-init-opts", "true",
        "--mf", "zoo:blenderbot2/blenderbot2_400M/model",
        "--datapath", "/data/data_hub",
        "--knowledge-access-method", "classify"
    )

    app.run(host=myConfig.IP, port=myConfig.PORT, debug=False)
