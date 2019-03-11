# -*- coding:utf-8 -*-
#Author：Copycat

import scrapy
import re
import pymongo
from pymongo import MongoClient as Mc
from athena_1.keyword import *

class qa_spider(scrapy.Spider):
    name='qaspider'
    #allowed_domains = ['baidu.com']

    def __init__(self):
        '''初始函数'''

        #用于初始化数据库设置，避免重复链接数据库
        self.DBclient=Mc()

        #设置需要链接的数据库名称
        self.spiderDB=self.DBclient.spider_data

        #设置需要查重的collection名称
        self.collectCheck1=self.spiderDB.baiduQaFormal
        self.collectCheck2=self.spiderDB.baiduqa_

        #set a collection to store
        self.collectInsert=self.spiderDB.baiduqa_add1

    def start_requests(self):
        '''搜寻页面url生成'''

        crawl_range=70
        #爬取范围设定

        urls=[]
        #设定url池

        for word in keyword:
            for i in range(1,crawl_range):
                urls.append("https://zhidao.baidu.com/search?word="+word+"&pn="+str((i-1)*10))

        #打印将要搜寻的搜索结果页面
        print("\n*************************************************\n")
        print('\nhere are start urls\n')
        print(urls)
        print("\n*************************************************\n")

        for url in urls:
            yield scrapy.Request(url=url,callback=self.parse)

    def parse(self,response):
        '''一级页面分析函数'''

        sec_level_page_urls=response.css('.ti ::attr(href)').extract()
        #得到二级页面的url列表

        #打印爬取到的二级页面的urls
        print("\n*************************************************\n")
        print('\nhere are sec level urls\n')
        print(sec_level_page_urls)
        print(len(sec_level_page_urls))
        print("\n*************************************************\n")

        #再次发出请求
        for url_2 in sec_level_page_urls:
            yield scrapy.Request(url=url_2,callback=self.parse_2)

    def parse_2(self,response):
        '''二级页面分析函数'''

        #打印进行二级解析的url
        print("\n***********************************************\n")
        print('\nhere means parse_2 passed\n')
        print(response.url)
        print("\n***********************************************\n")

        ask_title=response.css('.ask-title ::text').extract()[0]
        #获取问题标题

        #将标题转换为字符串
        ask_title=str(ask_title)
        #print('\n 以下是ask_title \n '+ask_title+'\n\n')

        best_answer_time=response.css('.wgt-best .wgt-replyer-all-time').extract()
        #获取最佳解答的回答时间

        #对获取的回答时间原始文本进行处理，得到最终文本
        match_pattern='\d\d\d\d-\d\d-\d\d'
        if re.search(match_pattern,str(best_answer_time)):
            best_answer_time=re.search(match_pattern,str(best_answer_time)).group(0)

        #将时间转换为字符串
        best_answer_time=str(best_answer_time)
        #print('\n 以下是time \n '+best_answer_time+'\n\n')

        best_answer_text=self.process_answer_text(response)
        #解析答案文本

        if not best_answer_text:
            #如果答案没有提取出来，那么这次解析直接中止
            print('最佳答案解析失败，中止！')
            return None

        #接下来使用mongodb储存
        packed_data={'title':ask_title,'time':best_answer_time,'answer':best_answer_text}

        print('parse_2,执行储存函数')
        #调用储存函数进行储存
        self.store_data(packed_data)

        return None

    def process_answer_text(self,response):
        '''解析答案文本专用的函数'''

        pre_answer=list(response.css('div[class="best-text mb-10"] p ::text').extract())
        #针对有下拉按钮的页面的解析
        if not pre_answer:
            #如果上述语句没有挖掘到数据，那么是另外一种页面，需要另外一种解析方式
            pre_answer=self.process_another_kind_page(response)


        #print("\n***********************pre_answer**************************\n")
        #print(pre_answer)
        #print("\n***********************************************************\n")

        answer_str=''

        if not pre_answer:
            #如果两次提取都是空，那么直接中断
            return None

        #将列表化的答案串合在一起
        answer_str=answer_str.join(pre_answer)

        answer_str=answer_str.strip().replace(u'\u3000', u' ').replace(u'\xa0', u' ')
        #最后去除空格及一些烦人的unicode字符

        #print("\n***********************answer_str**************************\n")
        #print(answer_str)
        #print("\n***********************************************************\n")

        #input()

        return answer_str

    def process_another_kind_page(self,response):
        '''用于处理另外一种的百度知道页面，即没有下拉按钮的页面'''

        #以下两行是为了解决div[class="best-text mb-10"]里混有杂物的情形
        #通过选取差集来获取纯净的答案
        pre_div_mass=list(response.css('div[class="best-text mb-10"] ::text').extract())

        pre_div_pattern=list(response.css('div[class="wgt-best-mask"] ::text').extract())

        answer_list=[x for x in pre_div_mass if x not in pre_div_pattern]
        #因为这几个东西是分两个部分，通过分别提取来替换

        answer_str=''

        answer_str=answer_str.join(answer_list)

        answer_str=answer_str.strip('\n')
        #去除换行符

        return answer_str

    def store_data(self,packed_data):

        #由于是大型搜集状态，所以需要考虑问题是重复的可能
        #特此新增查重模块，避免问题的重复插入

        print('开始储存数据！')

        #取出问题,构造查询所需的字典
        findKey={'title':packed_data['title']}

        #如果相关问题已经存在，直接结束本次数据插入过程
        if self.collectCheck1.find_one(findKey):
            print('查重！结束插入！')
            return None

        if self.collectCheck2.find_one(findKey):
            print('查重！结束插入！')
            return None


        print('查重完成！可以插入！')
        #如果不存在相关数据，则插入数据
        data_id=self.collectInsert.insert_one(packed_data).inserted_id

        return None