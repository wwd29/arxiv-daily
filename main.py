import os
from datetime import datetime

import feedparser
import yaml

from utils.utils import check_title, find_keyword, get_code_url, get_week_dates


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


def parse_rss(info):
    rss_addr = 'http://export.arxiv.org/rss/'
    categories = info['categories']
    keywords = info['keywords']
    paper_ids = set()
    keywords_bin = {k: [] for k in keywords}
    for category in categories:
        data = feedparser.parse(f'{rss_addr}{category}')
        if data and hasattr(data, 'entries') and len(data.entries) > 0:
            for entry in data.entries:
                if entry.id in paper_ids:
                    continue
                if not check_title(entry.title, categories):
                    continue
                keyword = find_keyword(entry.title, keywords)
                if keyword is None:
                    keyword = find_keyword(entry.summary, keywords)
                if keyword is None:
                    continue
                code_url = get_code_url(entry.id.split('/')[-1])
                item = get_item(entry.link, entry.title, code_url,
                                entry.summary)

                keywords_bin[keyword].append(item)
                paper_ids.add(entry.id)
    return keywords_bin


def get_item(paper_url, title, code_url, summary):
    id = paper_url.split('/')[-1]
    sub_title = title.split(".")[0]
    code_url = 'null' if code_url is None else f'<a href="{code_url}">{code_url}</a>'
    item = f'<h3>Title: {title}</h3>\n' \
        f'<ul>\n' \
        f'<li>Paper URL: <a href="{paper_url}">{paper_url}</a></li>\n' \
        f'<li>Code URL: {code_url}</li>\n' \
        f'<li>Copy Paste: <code><input type="checkbox">[[{id}]] {sub_title}({paper_url})</code></li>\n' \
        f'<li>Summary: {summary}</li>\n' \
        f'</ul>\n'
    return item


def main():
    user_info = parse_user()

    rss_info = {}
    for name, info in user_info.items():
        rss_info[name] = parse_rss(info)

    # 更新README
    now = datetime.utcnow()
    timestamp = datetime.strftime(now, '%Y-%m-%d %H:%M:%S')
    with open('README.md', 'w') as fp:
        fp.write(f'# arxiv-daily\n')
        fp.write(f'updated on {timestamp}\n')
        for name, info in rss_info.items():
            fp.write(f'## {name}\n')
            fp.write(f'| keyword | count |\n')
            fp.write(f'| - | - |\n')
            for keyword, items in info.items():
                fp.write(f'| {keyword} | {len(items)} |\n')

    out_root = 'html'

    date = datetime.strftime(now, '%Y-%m-%d')
    week = datetime.strftime(now, '%Y-W%W')
    # 更新index
    with open('index.html', 'w') as f:
        print(f'<link rel="stylesheet" href="css/markdown.css" />', file=f)
        print(f'<article class="markdown-body">', file=f)
        for name, info in user_info.items():
            print(f'<div><a href="./{out_root}/{name}.html">{name}</a></div>',
                  file=f)
        print(f'</article>', file=f)

    # 更新user index
    for name, info in rss_info.items():
        os.makedirs(f'{out_root}/{name}', exist_ok=True)
        # 更新html
        with open(f'{out_root}/{name}/{date}.html', 'w') as f:
            print(f'<link rel="stylesheet" href="../../css/markdown.css" />',
                  file=f)
            print(f'<article class="markdown-body">', file=f)
            print(f'<h1>{date}</h1>', file=f)
            for keyword, items in info.items():
                print(f'<h2>{keyword}</h2>', file=f)
                for item in items:
                    print(item, file=f)
            print(f'<button id="copy">Copy All</button>', file=f)
            print(f'</article>', file=f)
            print(
                f'<script src="https://cdn.staticfile.org/clipboard.js/2.0.4/clipboard.min.js"></script>',
                file=f)
            print(f'<script src="../../javascript/clipboard.js"></script>',
                  file=f)

        with open(f'{out_root}/{name}.html', 'w') as f:
            print(f'<link rel="stylesheet" href="../css/markdown.css" />',
                  file=f)
            print(f'<article class="markdown-body">', file=f)
            week_dates = get_week_dates(f'{out_root}/{name}')
            for week, dates in sorted(week_dates.items(),
                                      key=lambda d: d[0],
                                      reverse=True):
                print(f'<h2>{week}</h2>', file=f)
                for item in sorted(dates, reverse=True):
                    print(
                        f'<div><a href="./{name}/{item}.html">{item}</a></div>',
                        file=f)
            print(f'</article>', file=f)


if __name__ == '__main__':
    main()
