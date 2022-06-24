import requests
import json
import hashlib
import logging
# import time, re

# 请求失败码
REQUEST_FAILED = -1
logging.info('imported translate_function')


def getMD5(values):
    m2 = hashlib.md5()
    m2.update(values.encode('utf-8'))
    return m2.hexdigest()


def trans(url, data):
    appid = data['appid']
    content = data['content']
    salt = data['salt']
    secret_key = data['secret_key']
    appid = data['appid']

    sign = getMD5(appid + str(content) + str(salt) + secret_key)

    query = '?appid=' + appid + '&q=' + str(content) + \
            '&from=' + data['from'] + '&to=' + data['to'] + '&salt=' + str(salt) + '&sign=' + sign
    req_url = url + query

    print(f'request to baidu:{req_url}')

    response = requests.get(req_url).json()
    result = response['trans_result'][0]

    return result


# def translate():
#     file = open('en.php', 'r')
#     output = open('cn.php', 'w')
#     for line in file.readlines():
#         # print(line)
#         if re.match(settings_regex, line):
#             result = re.search(r"\'[^=]+\'", line)
#             # original_text 待翻译文本
#             original_text = result.group()
#             translated_text = trans(original_text).lower()
#             translated_text = translated_text.replace('”', '')
#             translated_text = translated_text.replace('“', '')
#             if translated_text[0] != "'":
#                 translated_text = "'" + translated_text
#             if translated_text[-1] != "'":
#                 translated_text = translated_text + "'"
#             # print(translated_text)
#             # print(original_text,' => ',translated_text)
#             line = "    " + original_text + " => " + translated_text + ",\n"
#             line = line.replace('"', "'")
#         output.write(line)
#         output.flush()
#         print("写入：" + line, end='')
#     file.close()
#     output.close()


# if __name__ == '__main__':
#     # translate()
#     text = trans('huawei')
#     print(text)
