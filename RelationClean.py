import pickle
import re
with open('comparison_triples.pkl', 'rb') as f:
    comp_triples = pickle.load(f)
def main():
    clean_triples = []
    for triple in comp_triples:
        n_triple = triple
        n_triple[2] = re.sub(',|\?|\.|;|!|。|，|？|！|；', '', triple[2])
        if n_triple[2] != '':
            clean_triples.append(n_triple)
    with open('clean_comp_trips.pkl', 'wb') as f:
        pickle.dump(clean_triples, f)
