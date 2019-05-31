import pickle
with open('origin_detail.pkl', 'rb') as f:
    details = pickle.load(f)

with open('dicts/entity_dict.pkl', 'rb') as f:
    loaded_models_dict = pickle.load(f)
n_details = {}
UNKNOW = 'unknow'
for id, detail in details.items():
    detail['id'] = id
    model = detail['型号'].upper()
    # print(model)
    modelEntity = loaded_models_dict.get(model, -1)

    origin_brand = detail['品牌']
    if origin_brand != -1:
        brand = origin_brand.split('（')[0].upper()
    else:
        brand = UNKNOW
    brandEntity = loaded_models_dict.get(brand, -1)
    if model == -1:
        model = UNKNOW
    if brand == -1:
        if origin_brand != -1:
            brand = origin_brand
        else:
            brand = UNKNOW

    if modelEntity == -1:
        if model != -1:
            modelEntity = [model]
        else:
            modelEntity = [UNKNOW]
    if brandEntity == -1:
        brandEntity = brand
    if len(modelEntity) > 1:
        find = False
        for entity in modelEntity:
            if brand in entity:
                modelEntity = entity
                find = True
                break
        if not find:
            modelEntity = modelEntity[0]
    else:
        modelEntity = modelEntity[0]
    detail['ModelEntity'] = modelEntity.upper()
    detail['BrandEntity'] = brandEntity.upper()

    # print('model: ', detail['ModelEntity'])
    # print("brand: ", detail['BrandEntity'])



    # print(brandEntity)

    n_details[id] = detail
with open('processed_detail.pkl', 'wb') as f:
    pickle.dump(n_details, f)