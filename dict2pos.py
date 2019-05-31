# -*- coding: utf-8 -*-
import ahocorasick
import pickle
import re
from pyhanlp import *
from pyltp import Postagger
import subprocess


def sentence2file(sentences, filename = 'temp/temp_sentence.txt'):
    with open(filename, encoding='utf-8', mode='w') as f:

        for sentence in sentences:
            f.write(sentence)
            f.write('\n')

def dict2pkl(dict_list, filename = 'temp/temp_dict.pkl'):
    with open(filename, mode = 'wb') as f:
        pickle.dump(dict_list, f)


def d2p(sentences, dict_list, isTrain = True):
    sentence2file(sentences)
    dict2pkl(dict_list)
    dict2pos('temp/temp_sentence.txt', 'temp/temp_dict.pkl', isTrain, False, False, True)

# input_text_file_name: utf8 txt
# dict_file_name: .pkl data, saved in array
def dict2pos(input_text_file_name, dict_file_name, isTrain = True, hasProcessed = False, doTokenization = False, isNER_Train = False, isNER_Test = False):
    def loadPostModel():
        postagger = Postagger()  # 初始化实例
        postagger.load('/Users/fanyijie/Downloads/ltp_data_v3.4.0/pos.model')  # 加载模型
        return postagger
    postagger = loadPostModel()
    # must be pkl file
    def loadDict(filename):
        # load models
        with open(filename, 'rb') as f:
            dict = pickle.load(f)
        return dict

    def loadTrainData(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = f.read()
            # clean \n in comments, this will make pos tag works bad
            data = re.sub('\n', '。', data)
            comments = data.split('||')
            return comments

    def generateAC(words):
        A = ahocorasick.Automaton()
        for idx, word in enumerate(words):
            A.add_word(word, (idx, word))
        A.make_automaton()
        return A

    A = generateAC(loadDict(dict_file_name))

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

    def addPostag(items, isTrain=True):
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

    def splitByToken(string):
        words = []
        for term in HanLP.segment(string):
            words.append(term.word)
        return words
    def token2Tuple(tokens):
        results = []
        for token in tokens:
            results.append((token,))
        return results

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

    def preprocess(filename, output_filename, no_nextline=False):
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
                    comment_dict[comment] += 1
                    # print('duplicates')
                    # print(comment)

                    # print(comment_dict[comment])
                    continue
                comment_dict[comment] = 1
                if not checkHasPeriod(comment[-1]):
                    comment += '。'
                comments.append(comment)
        with open(output_filename, 'w', encoding='utf-8') as f:
            for comment in comments:
                f.write(comment)
                f.write('||')

    def file_generate(input_data, output_file, isTrain=True):
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

    def non_token_file_generate(input_data, output_file, isTrain=True):
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
                results.append(('@@',))

        output(output_file, results)

    processed_file_name = input_text_file_name + '.processed.txt'
    train_file_name = input_text_file_name+ '.train.txt'

    if not hasProcessed:
        preprocess(input_text_file_name, processed_file_name)
    if doTokenization:
        file_generate(processed_file_name, train_file_name, isTrain)
    else:
        non_token_file_generate(processed_file_name, train_file_name, isTrain)

    if isNER_Train:
        if not doTokenization:
            subprocess.call(
                ["crf_learn", "crf++/crf_word.template", 'temp/temp_sentence.txt.train.txt', 'temp/temp_crf.model'])
        else:
            subprocess.call(
                ["crf_learn", "crf++/crf.template", 'temp/temp_sentence.txt.train.txt', 'temp/temp_crf.model'])



