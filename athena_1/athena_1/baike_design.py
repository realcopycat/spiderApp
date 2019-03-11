# 以下为百度百科的item的设计

'''
词条标题：core_title(str)
词条简介：title_abstract(str)
词条基本信息：basic_info(dict{属性：值}) *
多义选项：other_meaning(list(str))
词条内容：main_content(dict{段落标题：段落内容}）
'''

KEY_WORD_LIST=['诈骗','公','安','骗','账','转']

RE_PATTERN_KEY_WORD='诈骗|公安|骗|罪|网络|电信|移动'

RE_PATTERN_ITEM='/item/'