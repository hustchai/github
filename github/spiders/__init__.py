#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    抓取github search页面下Java类型代码库的代码

Authors: cjy(cjy_hust@163.com)
Date:    2017/10/18
"""


import scrapy
from scrapy import Request

from scrapy.selector import Selector



class GitHubSpider(scrapy.Spider):
    name = "github"
    allowed_domains = []
    start_urls = [
        "https://github.com/search?q=Java&type=Repositories&utf8=%E2%9C%93&_pjax=%23js-pjax-container"
    ]

    def parse(self, response):
        selector = Selector(response)
        divs = selector.xpath('//div[@class="repo-list-item d-flex flex-justify-start py-4 public source"]')
        for div in divs:
            a = div.xpath('.//a[@class="v-align-middle"]/@href').extract()
            name = a[0]
            span = div.xpath('.//div[@class="d-table-cell col-2 text-gray pt-2"]/text()').extract()
            type = span[1].replace(' ', '').replace('\n', '')
            url = 'https://github.com' + name
            if type == "Java":      # 只看类型是Java的文件
                yield Request(url, callback=self.parse_repo_contents)
            else:
                continue
        next = selector.xpath('//a[@class="next_page"]/@href').extract()
        if len(next) > 0:
            next_url = 'https://github.com' + next[0]
            yield Request(next_url, callback=self.parse)




    def parse_repo_contents(self, response):
        selector = Selector(response)
        tbody = selector.xpath('//tbody')
        for tr in tbody.xpath('tr'):
            type = tr.xpath('.//td[@class="icon"]').xpath('.//svg/@class').extract()[0]  # 文件 or 目录
            list = tr.xpath('.//td[@class="content"]').xpath('.//a/@href').extract()
            if len(list) > 0 :
                if type == 'octicon octicon-file-text':
                    file_url = 'https://raw.githubusercontent.com' + list[0]   # 下载文件的路径
                    file_url = file_url.replace('blob/','')
                    yield Request(file_url, callback=self.get_file_content)
                else:
                    directory_url = 'https://github.com' + list[0]  # 如果是目录则递归
                    yield Request(directory_url, callback=self.parse_repo_contents)



    def get_file_content(self, reponse):
        print reponse.body
        # print '1111'


