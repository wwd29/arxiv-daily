import html
import os
import random
import re
import time
from collections import defaultdict
from datetime import datetime
from urllib import parse

import requests

GOOGLE_TRANSLATE_URL = 'https://translate.google.com/m?q=%s&tl=%s&sl=%s'
HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Connection': 'close'
}


def get_week_dates(root):
    week_dates = defaultdict(list)
    for file in os.scandir(root):
        date = file.name.split('.')[0]
        week = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-W%W')
        week_dates[week].append(date)
    return week_dates


def translate(text, to_language="zh-CN", text_language="en"):
    time.sleep(random.random() + 1)
    text = parse.quote(text)
    url = GOOGLE_TRANSLATE_URL % (text, to_language, text_language)
    try:
        response = requests.get(url, timeout=2)
    except Exception:
        return ""

    data = response.text
    expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
    result = re.findall(expr, data)
    if (len(result) == 0):
        return ""

    return html.unescape(result[0])
