import requests
import os
import re
import pickle
import time
import random

with open('dicts/model_names_dict.pkl', 'rb') as f:
    loaded_models_dict = pickle.load(f)

User_Agent =  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
headers = {'User-Agent':User_Agent}

def getBrand(text):
    brand_re = re.compile('(?<=<dt>品牌</dt><dd>).*?(?=</dd>)', re.DOTALL)
    brand = brand_re.findall(text)
    if len(brand) > 0:
        return {'品牌': brand[0]}
    return {'品牌': -1}
def getModel(text):
    model_name_re = re.compile('(?<=<p>对外宣传型号</p>\n                      </div>\n                    </div>\n                  </dd>\n                  <dd>).*?(?=</dd>)', re.DOTALL)
    model_name = model_name_re.findall(text)
    if len(model_name) > 0:
        return {'型号': model_name[0]}
    return {'型号': -1}
def getAttr(queries, text):
    results ={}
    for query in queries:
        query_str = "(?<=<dt>" + query + "</dt><dd>).*?(?=</dd>)"
        result = re.findall(query_str, text)
        if len(result) > 0:
            results[query] = result[0]
    return results
def getRAM(text):
    t = re.compile('(?<=<dt>RAM</dt>\n                  <dd class="Ptable-tips">\n                    <a href="#none"><i class="Ptable-sprite-question"></i></a>\n                    <div class="tips">\n                      <div class="Ptable-sprite-arrow"></div>\n                      <div class="content">\n                        <p>机型的运行内存，决定机身的运行速度。</p>\n                      </div>\n                    </div>\n                  </dd>\n                  <dd>).*?(?=</dd>)')
    result = t.findall(text)
    if len(result) > 0:
        return {'RAM': result[0]}
    else:
        return {'RAM': 'unknow'}

def wait(s=1):
    time.sleep(s)

prefix = 'https://item.jd.com/'
postfix = '.html'

comments = os.listdir('comments')
details = {}
for file in comments:
    if file[-3:] == 'pkl':

        id = file.split('.')[0].split('_')[1]
        url = prefix + id + postfix

        res = requests.get(url,headers=headers)

        detail_tab_re = re.compile('(?<=J-detail-content-tab).*?(?=package-list)', re.DOTALL)
        detail_tab = detail_tab_re.findall(res.text)[0]
        brand = getBrand(detail_tab)
        model = getModel(detail_tab)
        # modelEntity = loaded_models_dict.get(model['型号'].upper(), -1)
        # modelEntity_dict = {'ModelEntity': modelEntity}
        # brandEntity = {'BrandEntity': loaded_models_dict.get(brand['品牌'], -1)}
        attr_queries = ["上市年份", '上市月份', "操作系统版本", 'CPU频率', 'CPU核数', 'CPU型号', '双卡机类型', '网络频率（4G）', '主屏幕尺寸（英寸）',
                        '屏幕像素密度（ppi）', '屏幕材质类型', '前置摄像头', '后置摄像头', '电池容量（mAh）', 'NFC/NFC模式', '指纹识别']
        attr = getAttr(attr_queries, detail_tab)
        ram = getRAM(detail_tab)

        detail = {**brand, **model, **attr, **ram}
        details[id] = detail

        wait(1 + 2 * random.random())
with open('origin_detail.pkl', 'wb') as f:
    pickle.dump(details, f)


