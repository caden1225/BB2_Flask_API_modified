from utils import Baidu_translate
import random


# @app.route("/baidu_api", methods=("GET", "POST"))
# def translate():
#     url = 'https://api.fanyi.baidu.com/api/trans/vip/translate'
#
#     data = {'salt': random.randint(1, 2022),
#             'appid': '20220211001079919',
#             'secret_key': 'dTWhdYJ0lxsZAGlVDH8D',
#             'content': request.content,
#             'from': request.fromLang,
#             'to': request.toLang}
#
#     output = Baidu_translate.trans(url, data)
#     return output


def translateChat(fromLang: str, toLang: str, content: str):
    url = 'https://api.fanyi.baidu.com/api/trans/vip/translate'

    data = {'salt': random.randint(1, 2022),
            'appid': '20220211001079919',
            'secret_key': 'dTWhdYJ0lxsZAGlVDH8D',
            'content': content,
            'from': fromLang,
            'to': toLang}

    output = Baidu_translate.trans(url, data)
    return output
