# BlenderBot2_flask_server
## 集成Parlai框架下的Blenderbot2及百度翻译实现中文对话模型服务，服务框架为Flask

### 在个人电脑上启动的方法

根目录下直接执行 python chat_api.py

出现"Running on http://172.23.130.225:3331/ (Press CTRL+C to quit)",表示启动成功

测试通过postman实现，get或post请求均可，具体api地址如下：

（参数统一通过bady中的json串传递）

（response的格式参考前端要求）

    - response格式：
        {
            "code": 0,
            "message": '操作成功',
            "data": {
                "type": 'text',
                "content": 返回内容
            }
        }


    - 百度翻译：url/baidu_translate
    - 入参:
            'content': data['content'],
            'from': data['fromLang'],
            'to': data['toLang']
    - return:
            'content': 翻译文本

    - 中文聊天: url/chat_with_chinese
    - 入参：
            'input_text': input_text
    - return:
            'content': 中文回复
 
