import os
import pickle
from collections import defaultdict

def generateModelDict():
    files = os.listdir('zol_information')
    brand_dict = {}
    for file in files:
        if file[-3:] == 'pkl':
            brand = file.split('_')[0]
            if brand_dict.get(brand, -1) == -1:
                brand_dict[brand] = []
            with open('zol_information/' + file, 'rb') as f:
                temp = pickle.load(f)
                brand_dict[brand].append(temp)
    brand_uni_dict = {}
    for pair in brand_dict.items():
        items = pair[1]
        key = pair[0]
        if len(items) == 1:
            brand_uni_dict[key] = items[0]
        temp = {}
        for item in items:
            temp = {**temp, **item}
        brand_uni_dict[key] = temp

    uni_brand_dict = defaultdict(list)
    for d in tuple(brand_uni_dict.values()):  # you can list as many input dicts as you want here
        for key, value in d.items():
            uni_brand_dict[key].append(value)

    with open('dicts/model_names_dict.pkl', 'wb') as f:
        pickle.dump(uni_brand_dict, f)
    return uni_brand_dict


def generateBrandDict():
    brands = ["OPPO", "vivo", "华为", "荣耀", "三星", "苹果", "一加", "努比亚", "魅族", "联想", "金立", "中兴", "Moto", "锤子科技", "360", "国美",
              "小米", "夏普", "华硕", "美图", "诺基亚", "HTC", "8848", "SUGAR", "黑莓", "海信", "AGM", "索尼", "黑鲨", "LG", "谷歌", "酷派",
              "微软", "飞利浦", "VERTU", "小辣椒", "TCL", "天语", "YotaPhone", "长虹", "ROG", "朵唯", "格力"]
    brand_dict = {}
    for brand in brands:
        # use lowercase as uniform
        brand_dict[brand.lower()] = brand
    brand_dict['Apple'] = '苹果'
    brand_dict['锤子'] = '锤子科技'
    brand_dict['Huawei'] = '华为'
    brand_dict['Nokia'] = '诺基亚'
    brand_dict['Google'] = "谷歌"
    # brand_dict.keys()
    keys = list(brand_dict.keys())
    for k in keys:
        value = brand_dict[k]
        del brand_dict[k]
        brand_dict[k.upper()] = value

    with open('dicts/brand_dict.pkl', 'wb') as f:
        pickle.dump(brand_dict, f)
    return brand_dict

def generateEntiryKeywordsDict():
    models = generateModelDict()
    brands = generateBrandDict()
    # latter will cover former if exist same key
    entity_dict = {**models, **brands}
    with open('dicts/entity_dict.pkl', 'wb') as f:
        pickle.dump(entity_dict, f)

generateEntiryKeywordsDict()


