import requests
import re
import json
import codecs
from sys import argv, setrecursionlimit
from bs4 import BeautifulSoup

# Because some board like "Gossiping","C_Chat"... has more than 1000 pages
setrecursionlimit(10000)


class Title:
    def __init__(self, title, prefix, reply):
        self.title = title
        self.prefix = prefix
        self.reply = reply

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)


class DictEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


TITLE_REGEX = re.compile(
    '(?P<reply>Re: )?(?:\[(?P<prefix>.*)\])? ?(?P<title>.*)')


def parseTitle(title):
    r = TITLE_REGEX.search(title)
    title = r.group('title') or ''
    prefix = r.group('prefix') or ''
    reply = r.group('reply') != None
    if r != None:
        return Title(title.strip(), prefix.strip(), reply)
    else:
        return None


def get(url):
    # Bypass R18
    return requests.get(url, cookies={'over18': '1'}).text


if len(argv) == 1:
    print('Arguments missing.')
    exit(1)

URL = 'https://www.ptt.cc'
PATH = '/bbs/%s/index1.html' % argv[1]


def getPage(path):
    print('Fetching: %s' % path)
    soup = BeautifulSoup(get(URL + path), 'lxml')
    for title in soup.select('.title a'):
        parsed = parseTitle(title.get_text())
        parsed.url = URL + title['href']
        yield parsed
    nextpage = soup.select('.btn-group-paging .btn')[2]
    if 'href' in nextpage.attrs:
        yield from getPage(nextpage.attrs['href'])


def stringify(obj):
    return json.dumps(obj, cls=DictEncoder, ensure_ascii=False)


result = list(getPage(PATH))
with codecs.open('%s.json' % argv[1], 'w', 'utf-8') as f:
    f.write(stringify(result))
