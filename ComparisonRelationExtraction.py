import re
import pickle
from HeadEntityCompletion import *
with open('edit_sentences.txt', 'r', encoding='utf-8') as f:
    edit_sentences = f.read()
def getAfterPhrasePos(idx, array):
    if idx+1 > len(array):
        start_idx = len(array)
    else:
        start_idx = idx+1
    for i in range(start_idx, len(array)):
        item = array[i][0]
        if checkStop(item):
            break
    return min(i+1, len(array))


def getPreRelation(idx, array):
    preRelations = ''
    prePhrasePos = getPrePhrasePos(idx, array)
    for i in range(prePhrasePos + 2, idx):
        token = array[i]
        if checkEntity(token) == False:
            preRelations += token[0]
    return preRelations


def getAfterRelation(idx, array):
    afterRelations = ''
    afterRelationPos = getAfterPhrasePos(idx, array)
    hasPassEntity = False
    for i in range(idx + 1, afterRelationPos):
        token = array[i]
        if checkEntity(token) == False and hasPassEntity == True:
            afterRelations += token[0]
        if checkEntity(token) == True:
            hasPassEntity = True

    return afterRelations


def extract_relation(sentences):
    triples = []
    for sentence in sentences:
        for idx, token in enumerate(sentence):
            if token[0] == '比':
                pre_entity, tail_entity, nextIdx = afterEntity(idx, sentence, 4)
                if tail_entity != '':
                    head_entity = beforeEntity(idx, sentence, 20)
                    if head_entity != '':
                        if tail_entity == head_entity:
                            print('same entity error')
                            continue

                        preRelation = getPreRelation(idx, sentence)

                        afterRelation = getAfterRelation(idx, sentence)
                        if afterRelation == '':
                            print('no attribute error')
                            continue
                        relation = preRelation + afterRelation
                        # TODO: deal with &nbsp
                        relation = re.sub('&nbsp', '', relation)
                        if relation == '':
                            print('no attribute error')
                            continue
                        triple = []
                        triple.append(head_entity)
                        triple.append(tail_entity)
                        triple.append(relation)
                        print(triple)
                        triples.append(triple)

                    else:
                        print('No head entity')
                        continue
    return triples





def main():
    lines = edit_sentences.split('\n')
    my_sentences = []
    my_sentence = []
    for line in lines:
        if line == '':
            my_sentences.append(my_sentence)
            my_sentence = []
            continue
        token = line.split('\t')
        my_sentence.append(token)
    triples = extract_relation(my_sentences)
    with open('comparison_triples.pkl', 'wb') as f:
        pickle.dump(triples, f)




