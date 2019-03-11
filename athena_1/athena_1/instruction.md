# A Quick Instruction Of a Scrapy Project for Athena Web APP

最后编辑于2019-3-9

### ATTENTION！！

本爬虫设置中不遵守robots.txt  
请在实际应用中更改

### 问答对爬虫

启动方式：通过scrapy命令行启动  
开发平台：VisualStudio 2017 Community  
爬虫名称：qaspider  
依赖环境：MongoDB、Scrapy、Re、BS4

供参考的爬取关键词：  
电信诈骗、金融诈骗、‘公检法 诈骗’、网络诈骗、
‘微信 诈骗’、‘qq 诈骗’、‘跨国 诈骗’、‘支付 诈骗’、
‘公务 诈骗’、‘电信 欺诈’


### 文件说明

driverpath.py 设置chromedriver的路径（因为中间件里用到了selenium）  
baike_design.py 设置百科爬虫爬取词条的条件（基于正则表达式）  
keyword.py 设置问答对爬取的关键词

