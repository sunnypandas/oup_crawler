# -*- coding: utf-8 -*-
import csv
import datetime

import pandas as pd
import scrapy
from scrapy_selenium import SeleniumRequest


class OupDownloadUrl(scrapy.Spider):
    name = 'oupDownloadUrl'
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
        tasks = self.get_rows(r'task/oup_list.csv')
        for row in tasks.itertuples():
            get_access = row.get_access
            download_url = row.download_url
            if get_access == '0':
                yield SeleniumRequest(
                    url=download_url,
                    method='GET', callback=self.parse_basic_info, meta={'row': row},
                    dont_filter=True)


    # @inline_requests
    def parse_basic_info(self, response):
        items = scrapy.Selector(text=response.text).xpath(
            '//ul[contains(@id, "Toolbar")]/li[contains(@class, "toolbar-item item-pdf js-item-pdf")]/a[contains(@class, "al-link pdf article-pdfLink")]/@href').extract()
        if len(items) > 0:
            print(response.url+'|'+items[0])
        else:
            print(response.url)

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