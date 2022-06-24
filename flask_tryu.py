from flask import Flask, request
import time
import logging
import json
import re


app = Flask(__name__)
@app.route("/test_json", methods=("GET", "POST"))
def _chat_with_chinese():
    started = int(time.time())
    data = request.json
    data['input_text'] = re.sub(' ', '', data['input_text'])
    print(data)
    logging.warning(data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=23456, debug=True)
