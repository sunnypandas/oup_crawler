import csv
import hashlib
import os
import platform
import random
import sys
import time

import pandas as pd
import scrapy
from pyvirtualdisplay import Display

from browserutils import get_browser, solve_blocked
from proxyutils import extract_proxy_squid
from loggingutils import Logger

os.chdir(sys.path[0])

log = Logger('crawler.log', level='info')
enable_proxy = bool(sys.argv[1]) if len(sys.argv) > 1 else False

def create_file(text, file):
    with open(file, 'a', newline='\r') as f:
        f.write(text)

def create_csv(rows, path):
    with open(path, 'a') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def fetch_url(url, file_path, history_path, proxy=None):
    display = None
    browser = None
    try:
        if platform.system() == 'Linux':
            display = Display(visible=False, size=(1600, 902))
            display.start()
        browser = get_browser(log, proxy)
        browser.get(url)
        items = scrapy.Selector(text=browser.page_source).xpath(
            '//div[contains(@id, "resourceTypeList-OUP_Issue")]//div[contains(@class, "al-article-item-wrap al-normal")]').extract()
        if len(items) > 0:
            print(url)
            for item in items:
                access = scrapy.Selector(text=item).xpath(
                    '//span[contains(@class, "get-access js-get-access-label at-get-access")]').extract()
                get_access = 0
                if len(access) > 0:
                    get_access = 1
                print(get_access)
    except Exception:
        log.logger.warning('exception: %s', url)
        if browser != None:
            browser.execute_script('window.stop()')
    finally:
        if browser != None:
            browser.quit()
        if display != None:
            display.stop()

def get_rows(path):
    rows = pd.read_csv(path, header=0, index_col=None, dtype=str)
    rows = rows.fillna('')
    return rows

def process_basic():
    tasks = [
        '33,1,January 2020,1–474',
        '33,2,February 2020,475–1009',
        '33,3,March 2020,1011–1366',
        '33,4,April 2020,1367–1877',
        '33,5,May 2020,1879–2377',
        '33,6,June 2020,2379–2843',
        '33,7,July 2020,2845–3391',
        '33,8,August 2020,3393–3924',
        '33,9,September 2020,3925–4443',
        '33,10,October 2020,4445–4972',
        '33,11,November 2020,4973–5462',
        '33,12,December 2020,5463–5939',
        '34,1,January 2021,1–568',
        '34,2,February 2021,569–1103',
        '34,3,March 2021,1105–1616',
        '34,4,April 2021,1617–2179',
        '34,5,May 2021,2181–2687',
        '34,6,June 2021,2689–3212',
        '34,7,July 2021,3213–3496',
        '34,8,August 2021,3497–4043',
        '34,9,September 2021,4045–4564',
        '34,10,October 2021,4565–5134',
        '34,11,November 2021,5135–5580',
        '34,12,December 2021,5581–6125'
    ]
    for task in tasks:
        year = task.split(',')[0]
        month = task.split(',')[1]
        publish = task.split(',')[2]
        url_web_project = 'https://academic.oup.com/rfs/issue/' + str(year) + '/' + str(month)
        log.logger.info('start processing %s', url_web_project)
        proxy = extract_proxy_squid() if enable_proxy else []
        if len(proxy) > 0 and enable_proxy:
            fetch_url(url_web_project, r'../../html/basic/', r'../../csv/kickstarter_basic_history.csv',  proxy)
            # time.sleep(random.randint(3, 5))
        else:
            fetch_url(url_web_project, r'../../html/basic/', r'../../csv/kickstarter_basic_history.csv')
            time.sleep(random.randint(5, 10))

if __name__ == '__main__':
    process_basic()