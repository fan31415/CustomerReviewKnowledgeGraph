import ahocorasick
from pyhanlp import *
with open('dicts/clean_neg_word.txt', 'r', encoding='utf-8') as f:
    neg_word = []
    for line in f:
        neg_word.append(line[:-1])

with open('dicts/clean_pos_word.txt', 'r', encoding='utf-8') as f:
    pos_word = []
    for line in f:
        pos_word.append(line[:-1])

with open('dicts/negate.txt', 'r', encoding='utf-8') as f:
    negate = []
    for line in f:
        negate.append(line[:-1])


def splitByToken(string):
    words = []
    for term in HanLP.segment(string):
        words.append(term.word)
    return words

def list2str(token_list):
    result = ''
    for idx, token in enumerate(token_list):
        if idx != 0:
            result += ' '
            result += token
        else:
            result += token
    # print(result)
    return result



def detectSentiment(sentence, doTokenize = False):
    def generateAC(words):
        A = ahocorasick.Automaton()
        for idx, word in enumerate(words):
            A.add_word(word, (idx, word))
        A.make_automaton()
        return A

    def getPurePos(A, test_string):
        occurs = []
        for end_index, (insert_order, original_value) in A.iter(test_string):
            start_index = end_index - len(original_value) + 1
            #         occurs.append((start_index, end_index, (insert_order, original_value))
            occurs.append([start_index, end_index])
        sorted_occur = sorted(occurs, key=lambda pair: pair[0] - pair[1])
        removed_index = []
        for i, item in enumerate(sorted_occur):
            for j in range(len(sorted_occur)):
                if i == j:
                    continue;
                # if two words overlap, pick the first one
                if (item[0] >= sorted_occur[j][0] and item[1] <= sorted_occur[j][1]) or (
                        item[0] > sorted_occur[j][0] and item[1] > sorted_occur[j][1] and item[0] <= sorted_occur[j][
                    1]):
                    removed_index.append(i)
                    break
        #             absorb_pos.append(item)
        result_occurs = []
        for idx, item in enumerate(sorted_occur):
            if idx not in removed_index:
                result_occurs.append(item)
        return result_occurs
    posAC = generateAC(pos_word)
    negAC = generateAC(neg_word)
    negateAC= generateAC(negate)

    # avoid  好 match xx 好像 xx
    def dealWithPartTokenTag(tokens, poses):
        removedDict = {}
        for idx, pos in enumerate(poses):
            if pos[1] + 1>= len(tokens):
                continue

            if tokens[pos[1]+1] != ' ':
                removedDict[idx] = True
        return removedDict
    def removeByDict(removeDict, array):
        n_array = []
        for idx, item in enumerate(array):
            if not removeDict.get(idx, False):
                n_array.append(item)
        return n_array

    def show(words, poses):
        for pos in poses:
            pass
            # print(words[pos[0]:pos[1]+1], end=' ')

    def dealWithPos(sentence):
        pos_score = 0
        neg_score = 0

        poshead = -1
        neghead = -1

        if doTokenize:
            seg_sentence = list2str(splitByToken(sentence))
        else:
            seg_sentence = sentence


        positivePos = getPurePos(posAC, seg_sentence)
        if doTokenize:
            removeDict = dealWithPartTokenTag(seg_sentence, positivePos)
            positivePos = removeByDict(removeDict, positivePos)
        # print('\n\n好评')
        show(seg_sentence, positivePos)
        if len(positivePos) >= 1:
            pos_score = 1
            poshead = positivePos[0][0]


        negativePos = getPurePos(negAC, sentence)
        if doTokenize:
            removeDict = dealWithPartTokenTag(seg_sentence, negativePos)
            negativePos = removeByDict(removeDict, negativePos)
        # print('\n\n差评')
        show(seg_sentence, negativePos)
        # have bad only when no good
        if len(positivePos) == 0:
            if len(negativePos) >= 1:
                neg_score = -1
                neghead = negativePos[0][0]
        negatePos = getPurePos(negateAC, sentence)
        show(seg_sentence, negatePos)


        if len(negatePos) >= 1:
            negatetail = negatePos[0][1]

            if negatetail < poshead and poshead - negatetail <= 4:
                pos_score = -1
            if negatetail < neghead and neghead - negatetail <= 4:
                neg_score = 1
        senti_score = neg_score + pos_score
        return senti_score

    return dealWithPos(sentence)

def test():
    score = detectSentiment('速度也快')
    print('\n')
    if score > 0:
        print('好评')
    if score < 0:
        print('差评')
    if score == 0:
        print('normal')







