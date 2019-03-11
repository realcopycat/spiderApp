#查重模块


from pymongo import MongoClient as Mc

client=Mc()

db=client.spider_data

collect=db.baiduqa_add1

data=collect.find()

for item in data:
    q=item["question"]
    
    data_=collect.find()
    for item_ in data_:
        q_=item

