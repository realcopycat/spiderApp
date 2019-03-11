# -*- coding:utf-8 -*-

import scrapy
import re
import pymongo
from pymongo import MongoClient as Mc
from bs4 import BeautifulSoup as bs
from urllib import parse as urlcode
from athena_1.baike_design import *

class baike_spider(scrapy.Spider):
    name='BKspider'
    allowed_domains=['baidu.com']

    def __init__(self):
        self.totalSearch=0
        #用于确定搜索的总数
        self.search_limit=500
        #用于确定搜索的上限
        self.searched_url=[]
        #储存已经搜索过的url

    def start_requests(self):
        '''设定起始urls'''

        urls=['https://baike.baidu.com/item/%E7%94%B5%E4%BF%A1%E8%AF%88%E9%AA%97']

        for url in urls:
            yield scrapy.Request(url=url,callback=self.parse)

    def parse(self,response):
        '''百科页面解析主函数'''

        dic_main_content=self.main_content_parse(response)
        dic_basicInfo=self.basicInfoParse(response)
        (core_title,title_abstract)=self.titleANDabstract(response)

        other_meaning=self.multiMeaningDealer(response)
        if other_meaning:
            pass
        else:
            other_meaning=['None']
            #如果没有相关的义项，直接返回一个列表None

        
        #print(dic_main_content)
        #print(dic_basicInfo)
        print(core_title)
        #print(title_abstract)
        #print(other_meaning)
        

        result=[core_title,title_abstract,dic_basicInfo,other_meaning,dic_main_content]
        self.item_packed(result)

        #print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

        urllist=self.page_search(response)
        if urllist:
            for url in urllist:
                yield scrapy.Request(url=url,callback=self.parse)

        #print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')


        return None

    def main_content_parse(self,response):
        '''主内容解析函数'''

        rawText=response.text

        soup=bs(rawText)
        #soup is BeautifulSoup Object

        start_tag=soup.find('div','top-tool')

        tag_iter=start_tag.next_siblings
        #得到迭代对象

        dic_content=self.tagIterAnalyser(tag_iter)
        #放入解析器中解析

        return dic_content

    def tagIterAnalyser(self,tag_iter):
        '''迭代器解析函数'''

        content_dict={}
        #最终的内容字典

        for each in tag_iter:
            className=self.classNameBuilder(each)
            #print('\n'+className)

            if className=='None':
                continue

            elif className=='para-title level-2':
                #print('进入一级解析\n')

                nowKey=''
                nowKey2=''
                tmpList=[]

                for eachstr in each.h2.strings:
                    tmpList.append(eachstr)

                content_dict[tmpList[1]]={'para':[]}
                #全新的小标题则新建一个键
                nowKey=tmpList[1]
                #并更新nowKey的值方便接下来的写入

                #print(nowKey)
                #print('\n')
                #print(content_dict)
                #print('\n')
                #input()
                continue

            elif className=='para-title level-3':
                #print('进入二级解析\n')

                nowKey2=''
                tmpList=[]

                for eachstr in each.h3.strings:
                    tmpList.append(eachstr)

                content_dict[nowKey][tmpList[1]]=[]
                #先放一个空字符串占位置
                nowKey2=tmpList[1]
                #更新nowKey2

                #print(nowKey2)
                #print('\n')
                #print(content_dict)
                #print('\n')
                #input()
                continue

            elif className=='para':
                #处理段落

                #print('进入段落解析\n')

                listSpan=[]
                if each.span:
                    for eachstr in each.span.strings:
                        listSpan.append(eachstr)
                        #用于处理图片占位说明导致的异常文字
                #print(listSpan)

                listSup=[]
                if each.sup:
                    for eachstr in each.sup.strings:
                        listSup.append(eachstr)
                        #用于处理脚注带来的异常标注
                #print(listSup)

                listText=[]
                for eachstr in each.strings:
                    listText.append(eachstr)
                    #读取所有文本

                pattern=re.compile('[[0-9]+]')

                processedText=[]    
                for eachstr in listText:
                    tmpans=eachstr.replace('\n','')
                    tmpans=tmpans.replace(u'\xa0','')
                    tmpans=re.sub(pattern,'',tmpans)
                    if tmpans:
                        processedText.append(tmpans)
                        #对于换行符进行处理
                #print(processedText)

                if listSpan:
                    processedText=[x for x in processedText if x not in listSpan]

                if listSup:
                    processedText=[x for x in processedText if x not in listSup]
                    #以上为分别对两种异常文本进行筛选

                finalText=''.join(processedText)
                #合并字符串
                #print(finalText)

                if 'nowKey2' in dir():
                    #如果出现了不在层级里的para，那么我们直接放弃

                    #接下来就是考虑怎么放入指定位置了
                    if nowKey2=='':
                        content_dict[nowKey]['para'].append(finalText)
                        #我们假设所有的小标题里都有para默认字段，这个字段下是一个列表
                        #储存一段一段的文字
                    else:
                        content_dict[nowKey][nowKey2].append(finalText)
                        #但如果恰好nowKey2是真，那么写入属于它的字段
                else:
                    continue

                #print('\n')
                #print(content_dict)
                #print('\n')

                #input()
                continue

        #print(content_dict)

        return content_dict

    def basicInfoParse(self,response):
        '''基本信息获取器'''

        copy=response.css('[class="basicInfo-item name"] ::text').extract()

        basicName=[]

        for each in copy:
            tmp=each.replace(u'\xa0',u'')
            basicName.append(tmp)

        #print(basicName)

        #接下来获取valueList

        soup=bs(response.text)
        #soup是bs对象

        valueRaw=soup.find_all('dd','basicInfo-item value')
        #valueRaw是提取的符合条件的标签列表

        pattern=re.compile('[[0-9]+]')
        #用于去除引注的正则表达式

        valueList=[]

        for strIter in valueRaw:
            #遍历标签列表
            tmplist=[]
            for strs in strIter.strings:
                #访问每个标签带有的字符串的生成器
                #print(str(strs))
                tmplist.append(str(strs))
                #把断断续续的字符串先按顺序放入列表

            finalans=self.string_processer(tmplist)
            #合成最终答案
            valueList.append(finalans)
            #加入最终答案的列表

        dic_basicInfo=dict(zip(basicName,valueList))
        #print(dic_basicInfo)

        return dic_basicInfo

    def classNameBuilder(self,tag):
        '''基于bs4的class名称合成器'''

        try:
            tmp_className=tag['class']
        except:
            return 'None'

        #接下来要得到标准的class名称
        if len(tmp_className)>1:
            tmp_className=' '.join(str(i) for i in tmp_className)
        else:
            tmp_className=str(tmp_className[0])

        return tmp_className

    def item_packed(self,listResult):
        '''最终结果的打包器'''

        core_title=listResult[0]
        title_abstract=listResult[1]
        basic_info=listResult[2]
        other_meaning=listResult[3]
        main_content=listResult[4]

        pack_data={
            'title':core_title,
            'abstract':title_abstract,
            'basic_info':basic_info,
            'multi_meaning':other_meaning,
            'relative_info':main_content
            }

        DBclient=Mc()
        spiderDB=DBclient.spider_data
        collection=spiderDB.baidu_baike_3_test

        data_id=collection.insert_one(pack_data).inserted_id

        #return None

    def titleANDabstract(self,response):
        '''标题及摘要的获取函数'''

        title=response.css('dd[class="lemmaWgt-lemmaTitle-title"] h1 ::text').extract()[0]
        #string形式的title

        rawAbstract=response.css('div[class="lemma-summary"] ::text').extract()
        #未经处理的带有摘要的列表

        abstract=self.string_processer(rawAbstract)
        #调用函数进行处理

        return (title,abstract)

    def string_processer(self,str_list):
        '''文本处理三件套'''

        pattern=re.compile('[[0-9]+]')

        final_list=[]

        for each in str_list:
            tmpans=each.replace('\n','')
            tmpans=tmpans.replace(u'\xa0','')
            tmpans=re.sub(pattern,'',tmpans)

            if not tmpans=='':
                final_list.append(tmpans)

        fianlAns=''.join(i for i in final_list)

        return fianlAns

    def multiMeaningDealer(self,response):
        '''检测是否具有多个意思，并进行保存'''

        if response.css('ul[class="polysemantList-wrapper cmn-clearfix"]'):
            return response.css('ul[class="polysemantList-wrapper cmn-clearfix"] li a ::text').extract()
        else:
            return []

    def page_search(self,response):
        '''在页面内搜寻相关页面深度探索'''

        #print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
        if self.totalSearch>self.search_limit:
            return None

        url_list=response.css('a ::attr(href)').extract()
        
        possible_list=[]

        pattern1=re.compile(RE_PATTERN_KEY_WORD)
        pattern2=re.compile(RE_PATTERN_ITEM)

        for each in url_list:
            tmp_url=urlcode.unquote(each)
            #print(tmp_url)
            #input()
            if re.search(pattern2,tmp_url):
                if re.search(pattern1,tmp_url):
                    if tmp_url not in self.searched_url:
                        self.totalSearch=self.totalSearch+1
                        self.searched_url.append(tmp_url)

                        #如果链接同时满足两种条件，那么进行搜索
                        #print(tmp_url)
                        #input()

                        possible_url='https://baike.baidu.com'+each
                        possible_list.append(possible_url)
                    else:
                        continue
                else:
                    continue
            else:
                continue
        #print(possible_list)
        return possible_list