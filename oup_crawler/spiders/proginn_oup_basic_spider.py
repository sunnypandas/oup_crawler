# -*- coding: utf-8 -*-
import csv
import datetime
import hashlib
import html
import logging
import random
import time

import pandas
import pandas as pd
import scrapy
from inline_requests import inline_requests
from scrapy_selenium import SeleniumRequest

from oup_crawler.consts import DOWNLOADER_MIDDLEWARES_SQUID_PROXY_OFF
from oup_crawler.utils.httputils import extractStringFromSelector, convertRawString2Headers, \
    convertRawString2Json


class OupBasic(scrapy.Spider):
    name = 'oupBasic'
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 60000,
        'DOWNLOAD_MAXSIZE': 12406585060,
        'DOWNLOAD_WARNSIZE': 0,
        'DOWNLOAD_DELAY': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        # 'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_SQUID_PROXY_OFF
    }
    batch = datetime.datetime.now()
    allowed_domains = []

    def start_requests(self):
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
            yield SeleniumRequest(
                url='https://academic.oup.com/rfs/issue/' + str(year) + '/' + str(month),
                method='GET', callback=self.parse_basic_info, meta={'year': year, 'month': month, 'publish': publish},
                dont_filter=True)


    # @inline_requests
    def parse_basic_info(self, response):
        year = response.meta['year']
        month = response.meta['month']
        items = scrapy.Selector(text=response.text).xpath(
            '//div[contains(@id, "resourceTypeList-OUP_Issue")]//div[contains(@class, "al-article-item-wrap al-normal")]').extract()
        if len(items) > 0:
            print(response.url)
            self.create_file(response.text, r'/Users/panpan/Workspace/PycharmProjects/oup_crawler/html/basic/' + str(year) + '-' + str(month) + '.txt')

    def get_rows(self, path):
        rows = pd.read_csv(path, header=0, index_col=None, dtype=str)
        rows = rows.fillna('')
        return rows

    def create_csv(self, rows, path):
        with open(path, 'a') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    def create_file(self, text, file):
        with open(file, 'a', newline='\r') as f:
            f.write(text)

def closed(self, reason):
        '''
        爬虫结束时退出登录状态
        :param reason:
        :return:
        '''
        if 'finished' == reason:
            self.logger.warning('%s', '爬虫程序执行结束，即将关闭')
        elif 'shutdown' == reason:
            self.logger.warning('%s', '爬虫进程被强制中断，即将关闭')
        elif 'cancelled' == reason:
            self.logger.warning('%s', '爬虫被引擎中断，即将关闭')
        else:
            self.logger.warning('%s', '爬虫被未知原因打断，即将关闭')