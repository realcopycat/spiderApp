# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


class Athena1SpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class Athena1DownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

from selenium import webdriver
from scrapy.http import HtmlResponse
from selenium.common.exceptions import TimeoutException
import re
from athena_1.driverpath import *

class ChromeDownloaderMiddleware(object):

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        '''取消上行注释以设置无界面'''
        self.driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH,chrome_options=options)

    def __del__(self):
        self.driver.close()

    def process_request(self,request,spider):

        #print("#######################################middleware#######################################")
        #print(request.url)
        #print("#######################################middleware#######################################")

        match_result1 = re.search('(question).*(gbk)',request.url)
        match_result2 = re.search('(word).*(pn=)',request.url)

        if match_result2:
            return None

        elif match_result1:
            print('\n######################################################################################')
            print("二级解析middleware启动")
            print('######################################################################################\n')

            [current_url,body]=self.process_with_selenium(request)
            test_response=HtmlResponse(current_url,body=body,encoding='utf-8',request=request)
            return test_response

        else:
            return None

    def process_with_selenium(self,request):

        self.driver.get(request.url)

        try:
            button=self.driver.find_element_by_css_selector('.wgt-best-arrowdown')
            button.click()
        finally:
            body=self.driver.page_source
            current_url=self.driver.current_url
            
            return (current_url,body)

