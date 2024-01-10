import html
import os
import random
import re
import textwrap
import time
from collections import defaultdict
from datetime import datetime
from urllib import parse

import requests

GOOGLE_TRANSLATE_URL = 'https://translate.google.com/m?q=%s&tl=%s&sl=%s'


headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44',
    'Connection': 'close'
}


def find_keyword(summary, keywords):
    summary = summary.lower()
    for keyword in keywords:
        if keyword in summary:
            return keyword
    return None


def check_title(title, categories):
    words = title.split('(')[-1].split()
    if len(words) > 2:
        return False
    category = words[1][1:6]
    if category in categories:
        return True
    return False


def get_code_url(short_id):
    base_url = 'https://arxiv.paperswithcode.com/api/v0/repos-and-datasets/'
    time.sleep(random.random())
    data = requests.get(base_url + short_id, headers=headers).json()
    if data and 'code' in data:
        if data['code'] and 'official' in data['code']:
            if data['code']['official'] and 'url' in data['code']['official']:
                return data['code']['official']['url']
    return None


def get_week_dates(root):
    week_dates = defaultdict(list)
    for file in os.scandir(root):
        date = file.name.split('.')[0]
        week = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-W%W')
        week_dates[week].append(date)
    return week_dates


def translate(text, to_language="zh-CN", text_language="en"):
    time.sleep(random.random())
    text = textwrap.replace('\n', ' ')
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

    return textwrap.fill(html.unescape(result[0]), width=79)
