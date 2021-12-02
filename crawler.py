from bs4 import BeautifulSoup
from csv import DictWriter
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import quote_plus
from re import findall
import time


HOME_URL = 'https://www.musashino-u.ac.jp'

def recursion_url(url_org, access_set = set()):
    result_dict = {}
    time.sleep(0.1)
    print(url_org)
    url = url_org
    matched_list = findall('[ぁ-ヶ亜-熙]', url)
    if matched_list:
        for m in matched_list:
            url = url.replace(m, quote_plus(m, encoding="utf-8"))
    try:
        html = urlopen(url)
    except HTTPError:
        return result_dict, access_set
    finally:
        access_set.add(url_org)
    soup = BeautifulSoup(html, "lxml")
    try:
        url_title = soup.title.string
        result_dict[url_org] = url_title
        print(url_title)
    except AttributeError:
        pass
    for a in soup.find_all('a'):
        url_child = a.get('href')
        if not url_child:
            continue
        url_child = url_child.strip()
        url_child = url_child[:url_child.index('#') if '#' in url_child else len(url_child)]
        if not url_child or len(url_child) == 1 or not(url_child.endswith('.html') or url_child.endswith('/')):
            continue
        if not url_child.startswith('http'):
            if url_child.startswith('/'):
                url_child = HOME_URL+url_child
            elif url_child == './':
                url_child = HOME_URL
            elif url_child.startswith('./'):
                url_child = HOME_URL+url_child[1:]
            else:
                url_child = HOME_URL+'/'+url_child
        else:
            if not url_child.startswith(HOME_URL):
                continue
        if url_child in access_set:
            continue
        else:
            dic, access_set = recursion_url(url_child, access_set)
            for k, v in dic.items():
                result_dict[k] = v
    return result_dict, access_set


def main():
    result_dict, _ = recursion_url(HOME_URL)
    print(result_dict)
    with open('sitemap.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = DictWriter(f, fieldnames=["url", "title"])
        for k, v in result_dict.items():
            w.writerow({'url':k, 'title':v})
    print('done')

if __name__ == '__main__':
    main()
