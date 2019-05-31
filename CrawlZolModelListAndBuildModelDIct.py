import requests
import re
import pickle
User_Agent =  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
headers = {'User-Agent':User_Agent}


def all_zh(s):
    for c in s:
        if not ('\u4e00' <= c <= '\u9fa5'):
            return False
    return True


def get_first_zh_pos(s):
    idx = 0
    zh_end_pos = -1
    while idx < len(s):
        has_add = False
        while idx < len(s) and '\u4e00' <= s[idx] <= '\u9fa5':
            zh_end_pos = idx
            idx += 1
            has_add = True
        if has_add == False:
            idx += 1
    return zh_end_pos


def is_int(s):
    for c in s:
        if c < '0' or c > '9':
            return False
    return True
def checkModelName(item):
    if all_zh(item) == False and is_int(item) == False:
        return True
    else:
        return False
def getModelNames(urls):
    models = []
    for idx, model in enumerate(models):
        models[idx] = re.sub('(（.*)', '', model)
    for u in urls:
        res = requests.get(u, headers=headers)
        content_re = re.compile('(?<=J_PicMode).*?(?="adSpace")', re.DOTALL)
        content = content_re.findall(res.text)[0]
        models.extend(re.findall('(?<=alt=").*?(?=")', content))
        # by sorted, we avoid the overlap issues. eg. Wrong assign '荣耀8X : 荣耀8X MAX‘, it should be '荣耀8X: 荣耀8X'
    for i, model in enumerate(models):
        models[i] = re.sub('(（.*)', '', model)
    models = sorted(models, key=lambda a: len(a))
    # flat mode
    model_names = {}
    for model in models:
        def assign(key):
            if model_names.get(key, -1) == -1:
                model_names[key] = model

        if model == '':
            continue
        # model = re.sub('(（.*)', '', model)
        # model = re.sub('\(.*\)', '', model)
        # uniform to upper case
        model = model.upper()
        items = model.split()
        lastItem = ''
        lastItem2 = ''
        isSplit = False
        hasTwoFirstItem = False

        for idx, item in enumerate(items):
            item = item.strip()
            if idx < 2:
                # no all Chinese
                # no only brand name but model names
                # no pure number
                if checkModelName(item) == True:

                    if idx != 0:
                        assign(item)
                    else:
                        zh_end_pos = get_first_zh_pos(item)
                        if zh_end_pos == -1:
                            assign(item)
                            lastItem = item

                            if idx + 1 < len(items) - 1 and checkModelName(items[idx + 1]):
                                #                             model_names[items[idx+1]] = model
                                hasTwoFirstItem = True
                                lastItem2 = items[idx + 1].strip()

                        else:
                            item1 = item.strip()
                            item2 = item[zh_end_pos + 1:].strip()
                            assign(item1)
                            lastItem = item1
                            if item2 != '' and checkModelName(item2):
                                hasTwoFirstItem = True
                                isSplit = True
                                assign(item2)
                                lastItem2 = item2

            if idx >= 1:
                currentItem = lastItem + ' ' + item
                # has space interval version

                # add space version
                assign(currentItem)
                # add no space version
                assign(currentItem.replace(' ', ''))
                lastItem = currentItem
            if idx >= 1 and hasTwoFirstItem:
                if idx == 1 and isSplit == False:
                    continue
                currentItem2 = lastItem2 + ' ' + item
                # has space interval version
                # add space version
                assign(currentItem2)
                # add no space version
                assign(currentItem2.replace(' ', ''))
                lastItem2 = currentItem2
    return model_names



def createUrlDict():
    s = {}

    # oppo
    s['oppo'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_1673_list_1.html'
    s['oppo'].append(url)
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_1673_list_1_0_1_2_0_2.html'
    s['oppo'].append(url)


    # vivo
    s['vivo'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_1795_list_1.html'
    s['vivo'].append(url)
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_1795_list_1_0_1_2_0_2.html'
    s['vivo'].append(url)
    # Huawei
    s['huawei'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_613_list_1.html'
    s['huawei'].append(url)
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_613_list_1_0_1_2_0_2.html'
    s['huawei'].append(url)

    # Rongyao
    s['rongyao'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_50840_list_1.html'
    s['rongyao'].append(url)
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_50840_list_1_0_1_2_0_2.html'
    s['rongyao'].append(url)

    # sumsung
    s['sumsung'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_98_list_1.html'
    s['sumsung'].append(url)
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_98_list_1_0_1_2_0_2.html'
    s['sumsung'].append(url)

    # apple
    s['apple'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_544_list_1_0_1_2_0_1.html'
    s['apple'].append(url)
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_544_list_1_0_1_2_0_2.html'
    s['apple'].append(url)
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_544_list_1_0_1_2_0_3.html'
    s['apple'].append(url)

    # oneplus
    s['oneplus'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_35579_list_1.html'
    s['oneplus'].append(url)

    # lumia
    s['lumia'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_35005_list_1.html'
    s['lumia'].append(url)

    # meizu
    s['meizu'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_1434_list_1.html'
    s['meizu'].append(url)
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_1434_list_1_0_1_2_0_2.html'
    s['meizu'].append(url)

    # lenovo
    s['lenovo'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_1763_list_1.html'
    s['lenovo'].append(url)

    # jingli
    s['jingli'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_1632_list_1.html'
    s['jingli'].append(url)

    # zhongxing
    s['zhongxing'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_642_list_1.html'
    s['zhongxing'].append(url)

    # moto
    s['sonic'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_295_list_1.html'
    s['sonic'].append(url)

    # chuizi
    s['chuizi'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_35849_list_1.html'
    s['chuizi'].append(url)

    # xiaomi
    s['xiaomi'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_34645_list_1.html'
    s['xiaomi'].append(url)
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_34645_list_1_0_1_2_0_2.html'
    s['xiaomi'].append(url)
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_34645_list_1_0_1_2_0_3.html'
    s['xiaomi'].append(url)

    # nokia
    s['nokia'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_297_list_1.html'
    s['nokia'].append(url)

    # htc
    s['htc'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_33080_list_1.html'
    s['htc'].append(url)

    # kupai
    s['kupai'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_1606_list_1.html'
    s['kupai'].append(url)
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_1606_list_1_0_1_2_0_2.html'
    s['kupai'].append(url)

    # google
    s['google'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_1922_list_1.html'
    s['google'].append(url)

    # sonic
    s['sonic'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_1069_list_1.html'
    s['sonic'].append(url)

    # philips
    s['philips'] = []
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_159_list_1.html'
    s['philips'].append(url)
    return s

urls = createUrlDict()
for k, v in urls.items():
    # actually this is entity names
    prefix = 'zol_information/' + k
    filename = prefix + '.pkl'
    model_names = getModelNames(v)
    with open(filename, 'wb') as f:
        pickle.dump(model_names, f)

