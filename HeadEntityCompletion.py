import os
import pickle

def checkStop(item):
    if item == '.' or item == '。' or item == '！' or item == '!' or item == '，' or item == ',' or item == ';' or item == '&nbsp':
        return True
    return False


def showPre(idx, array, num):
    result = ''
    if idx - num < 0:
        start_idx = 0
    else:
        start_idx = idx - num
    for i in range(start_idx, idx):
        item = array[i][0]
        result += item
    return result


def showPrePhrase(idx, array, num):
    result = ''
    if idx - num < 0:
        start_idx = 0
    else:
        start_idx = idx - num
    for i in range(idx - 1, start_idx - 1, -1):

        item = array[i][0]
        if item == '.' or item == '。' or item == '！' or item == '!':
            break
    for j in range(i, idx - 1):
        item = array[j][0]
        result += item
    return result


def getPrePhrasePos(idx, array):
    if idx - 1 <= 0:
        return 0
    result = idx - 1
    for i in range(idx - 1, -1, -1):

        item = array[i][0]
        if checkStop(item):
            break
    return max(i - 1, 0)


def showNext(idx, array, num):
    result = ''
    if idx >= len(array):
        return result
    if idx + num >= len(array):
        end_idx = len(array)
    else:
        end_idx = idx + num
    for i in range(idx, end_idx):
        item = array[i][0]
        if item == '，' or item == ',' or item == '.' or item == '。' or item == '！' or item == '!':
            break
        result += item
    return result


def beforeEntity(idx, array, num):
    entity = ''
    if idx - num < 0:
        start_idx = 0
    else:
        start_idx = idx - num
    for i in range(idx - 1, start_idx - 1, -1):
        token = array[i]
        if token[-1] == 'S':
            entity = token[0]
            break
        if token[-1] == 'B':
            entity += token[0]
            k = i + 1
            while array[k][-1] != 'E':
                entity += array[k][0]
                k += 1
            entity += array[k][0]
            break
    return entity


def afterEntity(idx, array, num):
    entity = ''
    preEntity = ''
    nextIdx = idx + 1
    if idx + 1 >= len(array):
        return (entity, nextIdx)
    if idx + num > len(array):
        end_idx = len(array)
    else:
        end_idx = idx + num
    for i in range(idx + 1, end_idx):
        token = array[i]
        if token[-1] == 'S':
            entity = token[0]
            break
        elif token[-1] == 'B':
            entity += token[0]
            k = i + 1
            while array[k][-1] != 'E':
                entity += array[k][0]
                k += 1
            nextIdx = k + 1
            entity += array[k][0]
            break
        else:
            preEntity += token[0]
    return (preEntity, entity, nextIdx)


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


def string2EntityToken(entity_string):
    words = splitByLanguage(entity_string)
    tokens = []

    if len(words) == 1:
        token = [words[0], 'S']
        tokens.append(tokens)
    if len(words) > 1:

        for idx in range(len(words)):
            if idx == len(words) - 1:
                token = [words[idx], 'E']
            elif idx == 0:
                token = [words[idx], 'B']
            else:
                token = [words[idx], 'I']

            tokens.append(token)

    return tokens

def checkEntity(token):
    if token[1] == 'S' or token[1] == 'B' or token[1] == 'I' or token[1] == 'E':
        return True
    return False

def nextEntity(idx, array):
    entity = ''
#     nextIdx = idx
    if idx + 1 == len(array):
        return (entity, idx)
    next_token = array[idx+1]
    if next_token[-1] == 'S':
        entity = next_token[0]
#         nextIdx +=1
    if next_token[-1] == 'B':
        entity += next_token[0]
        k = idx+2
        while array[k][-1] != 'E':
            entity += array[k][0]
            k+=1
        entity += array[k][0]
#         nextIdx = k+1
    return (entity, idx+len(entity)+1)


def rewrite_comments(comments):
    edit_sentences = []
    for entity in comments.keys():
        sentences = entity_comments[entity]
        for sentence in sentences:
            for idx, token in enumerate(sentence):
                if idx + 1 == len(sentence):
                    continue
                if token[0] == '比':
                    edit_sentence = ''
                    pre_entity, tail_entity, nextIdx = afterEntity(idx, sentence, 4)
                    if tail_entity != '':
                        head_entity = beforeEntity(idx, sentence, 20)
                        if head_entity != '':
                            pass
#                             print('head', head_entity)
                        else:
#                             print('add head', entity)
                            addPos = getPrePhrasePos(idx, sentence)
#                             print(addPos)
#                             print(sentence[addPos+1])
                            edit_sentence = sentence[:addPos+2]
                            edit_sentence.extend(string2EntityToken(entity))
                            edit_sentence.extend(sentence[addPos+2:])
#                             print(edit_sentence)
                            edit_sentences.append(edit_sentence)
                        if tail_entity != '':
                            pass
#                             print('tail', tail_entity)
#                         print(showPre(idx, sentence, 50) + token[0] + pre_entity + tail_entity + showNext(nextIdx, sentence, 9))
    return edit_sentences


def output_edit_sentence(sentences):
    filename = 'edit_sentences.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        for sentence in sentences:
            for token in sentence:
                f.write(token[0] + '\t' + token[1] + '\n')
            f.write('\n')



def main():

    with open('processed_detail.pkl', 'rb') as f:
        details = pickle.load(f)

    path = 'crf++/'
    files = os.listdir(path)
    marked_comments = {}
    for file in files:
        if file[-11:] == '_marked.txt':
            id = file.split('.')[0].split('_')[1]
            with open(path+file, 'r', encoding='utf-8') as f:
                marked_comments[id] = f.read()


    model_comments = {}
    for k, v in marked_comments.items():
        model_comments[details[str(k)]['ModelEntity']] = v


    entity_comments = {}
    for entity in model_comments.keys():
        item = model_comments[entity]
        sentences = []
        tokens = []
        lines = item.split('\n')
        for line in lines:
            if line == '':
                sentences.append(tokens)
                tokens = []
                continue
            token = line.split('\t')
            tokens.append(token)
        entity_comments[entity] = sentences

    edit_sentences = rewrite_comments(entity_comments)

    output_edit_sentence(edit_sentences)

main()