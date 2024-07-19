import os
import re
from datetime import datetime
from urllib import request

import dateutil.parser
import yaml
from bs4 import BeautifulSoup

from utils.utils import HEADERS, get_week_dates, translate

CONTENT_IN_BRACKET = re.compile(r'\((.*?)\)')


def parse_user():
    config_root = './configs'
    user_info = {}
    for file in os.scandir(config_root):
        if file.name.endswith('.yml'):
            with open(file.path) as f:
                info = yaml.load(f, Loader=yaml.FullLoader)
            name, ext = os.path.splitext(file.name)
            user_info[name] = info
    return user_info


class Paper:
    def __init__(self):
        self.abs_prefix = 'https://arxiv.org/abs/'
        self.pdf_prefix = 'https://arxiv.org/pdf/'

    def parse(self, dt, dd):
        self.id = re.findall(r'\d+\.\d+', dt.text)[0]
        self.abs_url = self.abs_prefix + self.id
        self.pdf_url = self.pdf_prefix + self.id

        self.title = dd.find(
            'div', {'class': 'list-title mathjax'}).text.replace('Title:', '').strip()
        self.authors = dd.find('div', {'class': 'list-authors'}).text.replace('Authors:\n', '').replace(
            '\n', '').strip()
        self.subjects = CONTENT_IN_BRACKET.findall(
            dd.find('div', {'class': 'list-subjects'}).text)
        self.abstract = dd.find(
            'p', {'class': 'mathjax'}).text.replace('\n', ' ').strip()

    def find_keyword(self, keywords):
        title = self.title.lower()
        abstract = self.abstract.lower()
        self.keywords = [
            keyword for keyword in keywords if keyword in title or keyword in abstract]

    def translate(self):
        self.abstract_zh = translate(self.abstract)

    def __str__(self):
        subjects = ', '.join(self.subjects)
        keywords = ', '.join(self.keywords)
        text = f'<h3>Title: {self.title}</h3>\n' \
            f'<ul>\n' \
            f'<li><strong>Authors: </strong>{self.authors}</a></li>\n' \
            f'<li><strong>Subjects: </strong>{subjects}</a></li>\n' \
            f'<li><strong>Abstract URL: </strong><a href="{self.abs_url}">{self.abs_url}</a></li>\n' \
            f'<li><strong>Pdf URL: </strong><a href="{self.pdf_url}">{self.pdf_url}</a></li>\n' \
            f'<li><strong>Copy Paste: </strong><code><input type="checkbox">[[{self.id}]] {self.title}({self.abs_url})</code><input type="text"></li>\n' \
            f'<li><strong>Keywords: </strong>{keywords}</a></li>\n' \
            f'<li><strong>Abstract: </strong>{self.abstract}</li>\n'

        if getattr(self, 'abstract_zh', None) is not None:
            text += f'<li><strong>摘要：</strong>{self.abstract_zh}</li>\n'

        text += f'</ul>\n'

        return text


def main():
    user_infos = parse_user()

    new_url = 'https://arxiv.org/list/cs/new'
    req = request.Request(url=new_url, headers=HEADERS)
    page = request.urlopen(req, timeout=20)
    bs = BeautifulSoup(page, features='html.parser')
    content = bs.body.find('div', {'id': 'content'})

    dts = content.dl.find_all('dt')
    dds = content.dl.find_all('dd')
    parse_date = dateutil.parser.parse(content.h3.text.split(' (')[0].replace('New submissions for ', ''))

    assert len(dts) == len(dds)

    user_papers = {}
    for user_name, info in user_infos.items():
        subjects = set(info['subjects'])
        keywords = info['keywords']
        trans = info['translate']
        papers = []
        for dt, dd in zip(dts, dds):
            paper = Paper()
            paper.parse(dt, dd)
            if paper.subjects[0] in subjects:
                paper.find_keyword(keywords)
                if len(paper.keywords) > 0:
                    if trans:
                        paper.translate()
                    papers.append(paper)

        user_papers[user_name] = papers

    # 更新README
    now = datetime.utcnow()
    timestamp = datetime.strftime(now, '%Y-%m-%d %H:%M:%S')
    with open('README.md', 'w', encoding='utf-8') as fp:
        fp.write(f'# arxiv-daily\n')
        fp.write(f'updated on {timestamp}\n')
        fp.write(f'| name | count |\n')
        fp.write(f'| - | - |\n')
        for user_name, papers in user_papers.items():
            fp.write(f'| {user_name} | {len(papers)} |\n')

    out_root = 'html'

    date = datetime.strftime(parse_date, '%Y-%m-%d')
    week = datetime.strftime(parse_date, '%Y-W%W')
    # 更新index
    with open('index.html', 'w', encoding='utf-8') as f:
        print(f'<link rel="stylesheet" href="css/markdown.css" />', file=f)
        print(f'<article class="markdown-body">', file=f)
        for user_name, info in user_infos.items():
            print(f'<div><a href="./{out_root}/{user_name}.html">{user_name}</a></div>',
                  file=f)
        print(f'</article>', file=f)

    # 更新user index
    for user_name, papers in user_papers.items():
        os.makedirs(f'{out_root}/{user_name}', exist_ok=True)
        # 更新html
        with open(f'{out_root}/{user_name}/{date}.html', 'w', encoding='utf-8') as f:
            print(f'<link rel="stylesheet" href="../../css/markdown.css" />',
                  file=f)
            print(f'<article class="markdown-body">', file=f)
            print(f'<h1>{date}</h1>', file=f)
            for paper in papers:
                print(paper, file=f)
            print(f'<button id="copy">Copy All</button>', file=f)
            print(f'</article>', file=f)
            print(
                f'<script src="../../javascript/clipboard.min.js"></script>',
                file=f)
            print(f'<script src="../../javascript/clipboard.js"></script>',
                  file=f)

        with open(f'{out_root}/{user_name}.html', 'w', encoding='utf-8') as f:
            print(f'<link rel="stylesheet" href="../css/markdown.css" />',
                  file=f)
            print(f'<article class="markdown-body">', file=f)
            week_dates = get_week_dates(f'{out_root}/{user_name}')
            for week, dates in sorted(week_dates.items(),
                                      key=lambda d: d[0],
                                      reverse=True):
                print(f'<h2>{week}</h2>', file=f)
                for item in sorted(dates, reverse=True):
                    print(
                        f'<div><a href="./{user_name}/{item}.html">{item}</a></div>',
                        file=f)
            print(f'</article>', file=f)


if __name__ == '__main__':
    main()
