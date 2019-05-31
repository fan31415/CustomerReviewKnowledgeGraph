from pyltp import Postagger
import re
postagger = Postagger() # 初始化实例
postagger.load('/Users/fanyijie/Downloads/ltp_data_v3.4.0/pos.model')  # 加载模型

def clean_adj_dict(filename, output_name):
    with open(filename, 'r', encoding='utf-8') as f:
        pos_words = []
        for line in f:
            pos_words.append(line[:-1])
    results = []
    for word in pos_words:
        result = postagger.postag([word])
        if result[0] == 'a':
            results.append(word)
    with open(output_name, 'w', encoding='utf-8') as f:
        for word in results:
            f.write(word + '\n')

clean_adj_dict('dicts/pos_word.txt', 'dicts/clean_pos_word.txt')
clean_adj_dict('dicts/neg_word.txt', 'dicts/clean_neg_word.txt')


