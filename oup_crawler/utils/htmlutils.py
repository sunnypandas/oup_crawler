import glob
import os

import scrapy

from oup_crawler.utils.httputils import extractStringFromSelector


def process_basic():
    path = r'/Users/panpan/Workspace/PycharmProjects/oup_crawler/html/basic/'  # use your path
    files = glob.glob(os.path.join(path, "*.txt"))
    files.sort()
    for filename in files:
        f = open(filename, "r")
        txt = f.read()
        items = scrapy.Selector(text=txt).xpath(
            '(//div[contains(@id, "resourceTypeList-OUP_Issue")]/div[contains(@class, "section-container")]/section)[1]//div[contains(@class, "al-article-item-wrap al-normal")]').extract()
        for item in items:
            access = scrapy.Selector(text=item).xpath(
                '//span[contains(@class, "get-access js-get-access-label at-get-access")]').extract()
            get_access = 0
            if len(access) > 0:
                get_access = 1
            title = ''
            download_url = ''
            if get_access == 1:
                title = extractStringFromSelector(scrapy.Selector(text=item).xpath(
                    '//h5[contains(@class, "customLink item-title")]//span[contains(@class, "access-title")]/text()').extract(), 0).strip()
                download_url = extractStringFromSelector(scrapy.Selector(text=item).xpath(
                    '//div[contains(@class, "pub-history-row")]//div[contains(@class, "ww-citation-primary")]/a/@href').extract(),
                                                  0).strip()
            else:
                title = extractStringFromSelector(scrapy.Selector(text=item).xpath(
                    '//h5[contains(@class, "customLink item-title")]//a[contains(@class, "at-articleLink")]/text()').extract(),
                                                  0).strip()
                download_url = extractStringFromSelector(scrapy.Selector(text=item).xpath(
                    '//div[contains(@class, "pub-history-row")]//div[contains(@class, "ww-citation-primary")]/a/@href').extract(),
                                                         0).strip()

            # print(title+'|'+download_url+'|'+filename.split('/')[-1].split('.')[0].replace('33', '2020').replace('34', '2021')+'|'+str(get_access))


if __name__ == '__main__':
    process_basic()