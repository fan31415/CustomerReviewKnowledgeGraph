import  pickle
from sentiment import *
from resolveEntity import  *
def getEntity(idx, array):
    entity = ''
    next_token = array[idx]
    if next_token[-1] == 'S':
        entity = next_token[0]
#         nextIdx +=1
    if next_token[-1] == 'B':
        entity += next_token[0]
        k = idx+1
        while array[k][-1] != 'E':
            entity += array[k][0]
            k+=1
        entity += array[k][0]
#         nextIdx = k+1
    return entity

with open('temp/test_crf_output.txt', 'r', encoding='utf-8') as f:
    sentences = []
    sentence = []
    for line in f:
        token = line[:-1].split('\t')
        if token[0] == '。':
            sentences.append(sentence)
            sentence = []
            continue
        sentence.append(token)

with open('crf++/clean_comp_trips.pkl', 'rb') as f:
    triples = pickle.load(f)


def tokens2str(token_list):
    result = ''
    for idx, token in enumerate(token_list):
        if idx != 0:
            result += ' '
            result += token[0]
        else:
            result += token[0]
    return result

def incDict(_dict, triple1, triple2, entity):
    if _dict.get(triple1 , -1)== -1:
        _dict[triple1] = {}
    if _dict[triple1].get(triple2, -1) == -1:
        _dict[triple1][triple2] = {}
    if _dict[triple1][triple2].get(entity, -1) == -1:
        _dict[triple1][triple2][entity] = 1
    else:
        _dict[triple1][triple2][entity] += 1



pos_dict = {}
neg_dict = {}

for idx, sentence in enumerate(sentences):
    last_entity = ''
    for i in range(len(sentence)):
        entity = getEntity(i, sentence)
        if entity != '':
            last_entity = entity
    # entity resolution
    triples[idx][0] = str2Entity(triples[idx][0])
    triples[idx][1] = str2Entity(triples[idx][1])
    triples[idx].append(last_entity)
    triples[idx].append(detectSentiment(tokens2str(sentence)))
    # TODO: CUrrently do not minus positive with negative
    if triples[idx][4] == 1:
        incDict(pos_dict, triples[idx][0], triples[idx][1], last_entity)
        incDict(neg_dict, triples[idx][1], triples[idx][0], last_entity)
    elif triples[idx][4] == -1:
        incDict(neg_dict, triples[idx][0], triples[idx][1], last_entity)
        incDict(pos_dict, triples[idx][1], triples[idx][0], last_entity)

def getRecommend(query_entity, query_attr):
    if neg_dict.get(query_entity, -1) == -1:
        # not exist model
        return -1
    comparisons = neg_dict[query_entity]
    scores = {}
    query_score = {}
    for model, comp in comparisons.items():
        scores[model] = 0
        query_score[model] = 0
        for attr, cnt in comp.items():
            scores[model] += cnt
            if query_attr != '' and attr == query_attr:
                query_score[model] += cnt

    score_list = list(scores.items())
    query_score_list = list(query_score.items())
    ranks = sorted(score_list, key=lambda x: x[1], reverse=True)
    query_ranks = sorted(query_score_list, key=lambda x: x[1], reverse=True)

    option = query_ranks[0]
    # if no this attribute, backtrack to the total recommend
    if option[1] == 0:
        option = ranks[0]
    return option[0]


print(pos_dict['苹果IPHONE X'])

print(neg_dict['苹果IPHONE X'])

print(pos_dict['小米8'])

print(neg_dict['小米8'])


query_entity = '小米8'
query_attr = ''
query_attr = '屏幕'

# Resolve brand and model names, make difference of them and count the number of brand



option = getRecommend(query_entity, query_attr)
print(option)









