from dict2pos import *
def buildNER(key_words):
    with open('crf++/clean_comp_trips.pkl', 'rb') as f:
        clean_triples = pickle.load(f)
        relations = []
        for tri in clean_triples:
            relations.append(tri[2])
    d2p(relations, key_words)


def testNER(key_words):
    with open('crf++/clean_comp_trips.pkl', 'rb') as f:
        clean_triples = pickle.load(f)
        relations = []
        for tri in clean_triples:
            relations.append(tri[2])
    d2p(relations, key_words, False)
    subprocess.call(['cp', 'temp/temp_sentence.txt.train.txt', 'temp/test_crf.txt'])
    subprocess.call(
        ["crf_test", "-m", 'temp/temp_crf.model', 'temp/test_crf.txt', '-o', 'temp/test_crf_output.txt'])

isTestNer = True

# Load keywords
key_words = []
with open('dicts/keyword.txt', 'r', encoding='utf-8') as f:
    for line in f:
        key_words.append(line[:-1])


if isTestNer:
    testNER(key_words)
else:
    buildNER(key_words)