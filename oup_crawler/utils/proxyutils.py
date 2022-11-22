import json
import os
import random
import sys
import urllib.request
from http.client import HTTPException
from urllib.error import URLError
from urllib.parse import quote

import requests
from requests.structures import CaseInsensitiveDict
from urllib3.exceptions import HTTPError

from loggingutils import Logger

os.chdir(sys.path[0])

log = Logger('proxy.log', level='info')
CLASH_PATH = './clash-proxies.txt'
SQUID_PATH = './squid-proxies.txt'

def extract_proxy_squid():
    proxies = _read_proxies(SQUID_PATH)
    available_proxy_list = []
    if len(proxies) == 0:
        return available_proxy_list
    proxy = random.sample(proxies, 1)
    for p in proxy:
        host = p.split(',')[0]
        port = p.split(',')[1]
        username = p.split(',')[2]
        password = p.split(',')[3]
        available_proxy_list.append({'host': host, 'port': port, 'username': username, 'password': password, 'type': 'basic'})
    return available_proxy_list

def extract_proxy_clash(url='http://ip', port='7890', secret='secret', test_available=False):
    api_url = ''.join([url, ':', port])
    count = 3
    available_proxy_list = []
    if test_available:
        setup_proxy()
        while True and count > 0:
            count = count - 1
            if is_good_proxy(api_url, secret):
                available_proxy_list.append({'api_url': api_url, 'secret': secret, 'type': 'bearer'})
                break
            else:
                setup_proxy()
    else:
        setup_proxy()
        available_proxy_list.append({'api_url': api_url, 'secret': secret})
    return available_proxy_list

def is_good_proxy(proxy, secret):
    proxy_support = urllib.request.ProxyHandler({'http': str(proxy),
                                                 'https': str(proxy)})
    opener = urllib.request.build_opener(proxy_support)
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'),
                         ('Authorization', ''.join(['Bearer ', str(secret)]))]
    urllib.request.install_opener(opener)
    try:
        response = urllib.request.urlopen('https://www.kickstarter.com', timeout=3)
    except HTTPError as e:
        return False
    except URLError as e:
        return False
    except HTTPException as e:
        return False
    else:
        return True

def fetch_proxies(url, port, secret):
    api_url = ''.join([url, ':', str(port), '/proxies'])
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = ''.join(["Bearer ", str(secret)])
    return requests.get(api_url, headers=headers).json().get('proxies')

def fetch_proxy_names(provider, url, port, secret):
    return fetch_proxies(url, port, secret).get(provider).get('all')

def get_available_proxies(provider, url, port, secret, test_url, time):
    names = fetch_proxy_names(provider, url, port, secret)
    api_url = ''.join([url, ':', str(port), '/proxies', '/{0}', '/delay', '?', 'url={1}', '&', 'timeout={2}'])
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = ''.join(["Bearer ", str(secret)])
    available_proxies = []
    for name in names:
        params = {
            'name': name,
            'url': test_url,
            'time': time
        }
        url_call = api_url.format(quote(params['name']), quote(params['url']), quote(str(params['time'])))
        result = requests.get(url_call, headers=headers).json()
        delay = result.get('delay') if result.get('delay') != None else 0
        if delay > 0:
            available_proxies.append(name)
    log.logger.info('Fetched %s available proxies.', len(available_proxies))
    return available_proxies

def _read_proxies(path=None):
    proxies = []
    with open(path, 'r') as f:
        for line in f:
            p = line[:-1]
            proxies.append(p)
    return proxies

def _write_proxies(proxies):
    with open(CLASH_PATH, 'w') as f:
        f.write('\n'.join(proxies))

def get_random_proxies(provider, url, port, secret, test_url, time, count):
    if os.path.exists(CLASH_PATH):
        proxies = _read_proxies(CLASH_PATH)
    else:
        proxies = get_available_proxies(provider, url, port, secret, test_url, time)
        if len(proxies) > 0:
            _write_proxies(proxies)
    if len(proxies) > 0:
        return random.sample(proxies, count)
    else:
        return []

def schedule_refresh_available_proxies(provider, url, port, secret, test_url, time):
    proxies = get_available_proxies(provider, url, port, secret, test_url, time)
    if len(proxies) > 0:
        _write_proxies(proxies)

def setup_proxy(provider='♻️ 手动切换', url='ip', port='9090', secret='secret', test_url='http://www.gstatic.com/generate_204', time=3000, count=1):
    proxies = get_random_proxies(provider, url, port, secret, test_url, time, count)
    name = ''
    if len(proxies) > 0:
        name = proxies[0]
        log.logger.info('Setup proxy to %s:', name)
    else:
        log.logger.info('Setup proxy failure!')
        return False
    api_url = ''.join([url, ':', str(port), '/proxies','/{0}']).format(quote(provider))
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = ''.join(["Bearer ", str(secret)])
    code = requests.put(api_url, data=json.dumps({"name": name}), headers=headers).status_code
    return True if code == 204 else False

if __name__ == '__main__':
    # schedule_refresh_available_proxies('♻️ 手动切换', 'ip', '9090', 'secret', 'http://www.gstatic.com/generate_204', 3000)
    # print(setup_proxy())
    # print(extract_proxy(test_available=True))
    print(extract_proxy_squid())