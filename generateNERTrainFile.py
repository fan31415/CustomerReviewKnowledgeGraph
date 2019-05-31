# -*- coding: utf-8 -*-
import ahocorasick
import pickle
from pyhanlp import *
from pyltp import Postagger
import re
postagger = Postagger() # 初始化实例
postagger.load('/Users/fanyijie/Downloads/ltp_data_v3.4.0/pos.model')  # 加载模型

# load models
with open('dicts/entity_dict.pkl', 'rb') as f:
    entity_dict = pickle.load(f)

A = ahocorasick.Automaton()
for idx, key in enumerate(entity_dict.keys()):
    A.add_word(key, (idx, key))
A.make_automaton()


def getOccur(test_string):
    occurs = []
    for end_index, (insert_order, original_value) in A.iter(test_string.upper()):
        start_index = end_index - len(original_value) + 1
        #         occurs.append((start_index, end_index, (insert_order, original_value))
        occurs.append([start_index, end_index, original_value])
    return occurs


def getPos(test_string):
    occur = getOccur(test_string)
    sorted_occur = sorted(occur, key=lambda pair: pair[0] - pair[1])
    removed_index = []
    for i, item in enumerate(sorted_occur):
        for j in range(len(sorted_occur)):
            if i == j:
                continue;
            # if two words overlap, pick the first one
            if (item[0] >= sorted_occur[j][0] and item[1] <= sorted_occur[j][1]) or (
                    item[0] > sorted_occur[j][0] and item[1] > sorted_occur[j][1] and item[0] <= sorted_occur[j][1]):
                removed_index.append(i)
                break
    #             absorb_pos.append(item)
    result_occurs = []
    for idx, item in enumerate(sorted_occur):
        if idx not in removed_index:
            result_occurs.append(item)
    for item in result_occurs:
        item.append(entity_dict[item[2]])
    return result_occurs


def getPurePos(test_string):
    occurs = []
    for end_index, (insert_order, original_value) in A.iter(test_string.upper()):
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
                    item[0] > sorted_occur[j][0] and item[1] > sorted_occur[j][1] and item[0] <= sorted_occur[j][1]):
                removed_index.append(i)
                break
    #             absorb_pos.append(item)
    result_occurs = []
    for idx, item in enumerate(sorted_occur):
        if idx not in removed_index:
            result_occurs.append(item)
    return result_occurs


def pos2dict(pos):
    cnt = 0
    result = {}
    for item in pos:
        for i in range(item[0], item[1] + 1):
            result[i] = cnt
        cnt += 1
    return result


def checkAlpha(c, ctype):
    if (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z'):
        ctype = 1
    return ctype


def checkDigit(c, ctype):
    if c >= '0' and c <= '9':
        ctype = 2
    return ctype


def checkSpace(c, ctype):
    if c == ' ':
        ctype = 3
    return ctype


def addMark(ctype, lastCtype, cnt):
    if ctype == lastCtype and ctype != -1:
        cnt -= 1
    return cnt


def dealNonChinese(string):
    cnt = -1
    mark = []
    ctype = -1  # -1 means chinese
    lastCtype = -1
    size = len(string)
    for idx, c in enumerate(string):
        # Chinese
        ctype = -1

        # specific
        ctype = checkAlpha(c, ctype)
        ctype = checkDigit(c, ctype)
        ctype = checkSpace(c, ctype)

        cnt += 1
        cnt = addMark(ctype, lastCtype, cnt)
        mark.append(cnt)
        lastCtype = ctype

    return mark


def splitByChar(string):
    result = []
    for c in string:
        result.append(c)
    return result


def splitByLanguage(string):
    result = []
    pos = dealNonChinese(string)
    temp = ''
    for i in range(len(pos)):
        temp += string[i]
        if i + 1 >= len(pos):
            result.append(temp)
            break
        if pos[i] != pos[i + 1]:
            result.append(temp)
            temp = ''
    return result


def splitByToken(string):
    words = []
    for term in HanLP.segment(string):
        words.append(term.word)
    return words


def tagTokens(tokens, posdict):
    idx = 0
    results = []
    for i, token in enumerate(tokens):
        curTag = posdict.get(idx, -1)
        if curTag == -1:
            results.append((token, 'O'))
            idx += len(token)
            continue
        preTag = posdict.get(idx - 1, -1)
        nextTag = posdict.get(idx + len(token), -1)
        if preTag != curTag and curTag != nextTag:
            results.append((token, 'S'))
        elif preTag != curTag and curTag == nextTag:
            results.append((token, 'B'))
        elif preTag == curTag and curTag == nextTag:
            results.append((token, 'I'))
        elif preTag == curTag and curTag != nextTag:
            results.append((token, 'E'))

        idx += len(token)
    return results

def token2Tuple(tokens):
    results = []
    for token in tokens:
        results.append((token, ))
    return results


def addPostag(items, isTrain = True):
    result = []
    words = []
    for row in items:
        words.append(row[0])
    postags = postagger.postag(words)
    # print(postags[0])
    for i, row in enumerate(items):
        # deal with white space
        if row[0] == ' ' or row[0] == '\n':
            postags[i] = 'wp'
        if isTrain:
            result.append((row[0], postags[i], row[1]))
        else:
            result.append((row[0], postags[i]))
    return result


def output(filename, labels):
    with open(filename, 'w', encoding='utf-8') as f:
        for label in labels:
            # make it mutate
            label = list(label)
            # deal with empty line
            allmark = True
            for c in label:
                if c != '@@':
                    allmark = False
                    break
            if allmark:
                f.write('\n')
                continue
            # crf++ not recognized space
            # maybe has many continued spaces, so use label[0][0] to pick the first one
            if label[0][0] == ' ' or label[0] == '\t':
                label[0] = '&nbsp'
            # deal with next line, replace it with 。
            elif label[0] == '\n':
                label[0] = '。'

            for i, c in enumerate(label):
                f.write(c)
                if i != len(label) - 1:
                    f.write('\t')
                else:
                    f.write('\n')
def outputTest(filename, labels):
    with open(filename, 'w', encoding='utf-8') as f:
        for label in labels:
            # deal with empty line
            if label[0] == '@@' and label[1] == '@@':
                f.write('\n')
                continue
            # crf++ not recognized space
            # maybe has many continued spaces, so use label[0][0] to pick the first one
            if label[0][0] == ' ' or label[0] == '\t':
                f.write('&nbsp' + '\t' + label[1])
            # deal with next line, replace it with 。
            elif label[0] == '\n':
                f.write('。' + '\t' + label[1])
            else:
                f.write(label[0] + '\t' + label[1])

            f.write('\n')

def preprocess(filename, output_filename, no_nextline = False):
    # valid_re = re.compile("[\u4e00-\u9fa5A-Za-z0-9&~～/=\-“”#\(\)@<>《》？?。.、+！!:：%*,，;'\"\\s]")
    # add period and check duplicate
    comment_dict = {}
    comments = []
    def checkHasPeriod(c):
        if c == '!' or c == '.' or c == '?' or c == '。' or c == '！' or c == '？':
            return True
        return False
    with open(filename, 'r', encoding='utf-8') as f:
        data = f.read()
        lines = data.split('||')
        for idx, line in enumerate(lines):
            if no_nextline == False:
                comment = line[:-1]
            else:
                comment = line
            # remove empty comments
            if len(comment) < 1:
                continue
            # remove duplicates
            if comment_dict.get(comment, -1) != -1:
                comment_dict[comment] +=1
                # print('duplicates')
                # print(comment)

                # print(comment_dict[comment])
                continue
            comment_dict[comment] = 1
            if not checkHasPeriod(comment[-1]):
                comment += '。'
            # replace illegal char
            # ncomment = ''
            #
            # for i, c in enumerate(comment):
            #
            #     # if c == '\t' or c == '\n' or c == ' ' or '\u4e00' <= c <= '\u9fa5' or '1' <= c <= '9' or 'a' <= c <= 'z' or 'A' <= c <= 'Z' or c == '.' or c == '。' or c == ',' or c == '，' or c == '?' or c == '？' or c == '!' or c == '！' or c == '"' or c == '“' or c == '"' :
            #     #     ncomment += c
            #     if valid_re.match(c):
            #         ncomment += c
            #     else:
            #         ncomment += '*'
            # comments.append(ncomment)
            comments.append(comment)
    with open(output_filename, 'w', encoding='utf-8') as f:
        for comment in comments:
            f.write(comment)
            f.write('||')

def loadTrainData(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = f.read()
        # clean \n in comments, this will make pos tag works bad
        data = re.sub('\n', '。', data)
        comments = data.split('||')
        return comments
def file_generate(input_data, output_file, isTrain = True):
    comments = loadTrainData(input_data)
    results = []
    count = 0
    for comment in comments:
        # print(comment)
        count += 1
        print(count)
        # if count > 10000:
        #     break
        entity_pos = getPurePos(comment)
        # ignore the sentence has no entity
        if len(entity_pos) == 0:
            continue
        if isTrain:
            labels = tagTokens(splitByToken(comment), pos2dict(entity_pos))
        else:
            labels = addPostag(token2Tuple(splitByToken(comment)), False)
        results.extend(addPostag(labels))
        # add blank line to convenient training
        if isTrain:
            results.append(('@@', "@@", "@@"))
        else:
            results.append(('@@', "@@"))
    output(output_file, results)

def non_token_file_generate(input_data, output_file, isTrain = True):
    comments = loadTrainData(input_data)
    results = []
    count = 0
    for comment in comments:
        # print(comment)
        count += 1
        print(count)
        if count > 10000:
            break
        entity_pos = getPurePos(comment)
        # ignore the sentence has no entity
        if len(entity_pos) == 0:
            continue
        if isTrain:
            labels = tagTokens(splitByLanguage(comment), pos2dict(entity_pos))
        else:
            labels = token2Tuple(splitByLanguage(comment))
        # results.extend(addPostag(labels))
        results.extend(labels)
        # add blank line to convenient training
        if isTrain:
            results.append(('@@', "@@"))
        else:
            results.append(('@@', ))

    output(output_file, results)




import subprocess
from copy import deepcopy
isTrain = True
# do preprocess() when change data
hasProcessed = False
doTokenization = True

divideById = False

if divideById:
    for file in os.listdir('comments'):
        if file[-3:] == 'txt' and file[0] == 'c' and file[-5] != 'd':
            origin_file = 'comments/' + file
            processed_file = 'comments/' + file[:-4] + '_processed.txt'
            train_file = 'crf++/' + file[:-4] + '_train.txt'
            output_file = 'crf++/' + file[:-4] + '_marked.txt'
            if not hasProcessed:
                preprocess(origin_file, processed_file, no_nextline = True)
            if doTokenization:
                file_generate(processed_file, train_file, isTrain)
                if not isTrain:
                    subprocess.call(
                        ["crf_test", "-m", 'crf++/crf.model', train_file, '-o', output_file])
            else:
                non_token_file_generate(processed_file, train_file, isTrain)
                if not isTrain:
                    subprocess.call(
                        ["crf_test", "-m", 'crf++/word_only.model', train_file, '-o', output_file])

else:
    if isTrain:
        if not hasProcessed:
            preprocess('comments/total_comments.txt', 'comments/total_comments_processed.txt')
        if doTokenization:
            file_generate('comments/total_comments_processed.txt', 'crf++/train_file.txt', True)
        else:
            non_token_file_generate('comments/total_comments_processed.txt', 'crf++/token_train_file2.txt', True)
    else:
        if not hasProcessed:
            preprocess('comments/test_comments.txt', 'comments/test_comments_processed.txt')
        if doTokenization:
            file_generate('comments/test_comments_processed.txt', 'crf++/token_test_file.txt', False)
            subprocess.call(
                ["crf_test", "-m", 'crf++/crf.model', 'crf++/token_test_file.txt', '-o', 'crf++/output.txt'])
        else:
            non_token_file_generate('comments/total_comments_processed.txt', 'crf++/token_test_file2.txt', False)
            subprocess.call(
                ["crf_test", "-m", 'crf++/crf.model', 'crf++/token_test_file2.txt', '-o', 'crf++/output.txt'])









